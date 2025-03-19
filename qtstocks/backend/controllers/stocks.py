from flask import jsonify, request, Response
from datetime import datetime, timezone
import io
import csv
from models import Stock, StockStats, user_stock_stats
from extensions import db
from services.get_stock_lists import get_stock_list
from services.get_stock_data import process_stock_list
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak, Frame, PageTemplate
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.patheffects as path_effects
import numpy as np

def init_stock_routes(app, token_required):
    @app.route('/api/stocks')
    @token_required
    def get_stocks(current_user):
        try:
            stocks = Stock.query.all()
            return jsonify({
                'stocks': [
                    {
                        'symbol': stock.symbol,
                        'name': stock.name,
                        'last_updated': stock.last_updated.strftime('%Y-%m-%d %H:%M:%S')
                    }
                    for stock in stocks
                ]
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/stocks_with_stats')
    @token_required
    def get_stocks_with_stats(current_user):
        try:
            # Query stocks that have stats
            stocks_with_stats = db.session.query(Stock).join(StockStats).join(user_stock_stats).filter(user_stock_stats.c.user_id == current_user.id).all()
            return jsonify({
                'stocks': [
                    {
                        'symbol': stock.symbol,
                        'name': stock.name,
                        'last_updated': stock.stats.last_updated.strftime('%Y-%m-%d %H:%M:%S'),
                        'price': stock.stats.price,
                        'market_cap': stock.stats.market_cap,
                        'eps': stock.stats.eps,
                        'pe': stock.stats.pe,
                        'pb': stock.stats.pb
                    }
                    for stock in stocks_with_stats
                ]
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/download_stock_list', methods=['POST'])
    @token_required
    def download_stock_list(current_user):
        try:
            stocks = get_stock_list()
            
            for stock_data in stocks:
                existing_stock = Stock.query.filter_by(symbol=stock_data['Symbol']).first()
                if existing_stock:
                    continue
                stock = Stock(
                    symbol=stock_data['Symbol'],
                    name=stock_data['Name'],
                    last_updated=datetime.now(timezone.utc)
                )
                db.session.add(stock)
            
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': f'Successfully downloaded {len(stocks)} stocks'
            })
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/fetch_stock_data', methods=['POST'])
    @token_required
    def fetch_stock_data(current_user):
        try:
            data = request.get_json()
            if not data or 'symbols' not in data:
                return jsonify({'error': 'No stock symbols provided'}), 400
                
            symbols = data['symbols']
            if not symbols:
                return jsonify({'error': 'Empty stock symbols list'}), 400
            
            fetching_latest = data.get('loadLatestData', False)
            
            # Verify all symbols exist in database
            for symbol in symbols:
                stock = Stock.query.filter_by(symbol=symbol).first()
                if not stock:
                    return jsonify({'error': f'Stock {symbol} not found in database'}), 404
                
            if fetching_latest:
                new_symbols = symbols
            else:
                # reuse existing stock stats if already available in stock_stats table
                new_symbols = []
                for symbol in symbols:
                    stock_stat = StockStats.query.filter_by(symbol=symbol).first()
                    if stock_stat:
                        if stock_stat not in current_user.stock_stats:
                            current_user.stock_stats.append(stock_stat)
                    else:
                        new_symbols.append(symbol)
                db.session.commit()
            
            # scrape data for any new symbols
            if len(new_symbols) > 0:
                process_stock_list(new_symbols, current_user)
            
            return jsonify({
                'success': True,
                'message': f'Successfully fetched data for {len(new_symbols)} stocks {", ".join(new_symbols)}'
            })
            
        except Exception as e:
            print(f"Error in fetch_stock_data: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/remove_stock_stats', methods=['POST'])
    @token_required
    def remove_stock_stats(current_user):
        try:
            data = request.get_json()
            if not data or 'symbols' not in data:
                return jsonify({'error': 'No stock symbols provided'}), 400
                
            symbols = data['symbols']
            if not symbols:
                return jsonify({'error': 'Empty stock symbols list'}), 400
            
            # Delete stats for each symbol
            for symbol in symbols:
                stats = StockStats.query.filter_by(symbol=symbol).first()
                if stats:
                    db.session.delete(stats)
            
            # Delete user_stock_stats for each symbol
            for symbol in symbols:
                user_stock_stat = db.session.query(user_stock_stats).filter_by(stock_symbol=symbol, user_id=current_user.id).first()
                if user_stock_stat:
                    db.session.delete(user_stock_stat)
            
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': f'Successfully removed stats for {len(symbols)} stocks'
            })
            
        except Exception as e:
            db.session.rollback()
            print(f"Error in remove_stock_stats: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/export_csv')
    @token_required
    def export_stocks(current_user):
        try:
            # Create CSV data
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write header
            writer.writerow(['Symbol', 'Name', 'Price', 'Market Cap', 'EPS', 'P/E', 'P/B', 'Last Updated'])
            
            stocks_with_stats = db.session.query(Stock)\
                .join(StockStats)\
                .join(user_stock_stats)\
                .filter(user_stock_stats.c.user_id == current_user.id)\
                .all()
                        
            for stock in stocks_with_stats:
                writer.writerow([
                    stock.symbol,
                    stock.name,
                    stock.stats.price,
                    stock.stats.market_cap,
                    stock.stats.eps,
                    stock.stats.pe,
                    stock.stats.pb,
                    stock.stats.last_updated.strftime('%Y-%m-%d %H:%M:%S')
                ])
            
            # Create response
            output.seek(0)
            return Response(
                output.getvalue(),
                mimetype='text/csv',
                headers={
                    'Content-Disposition': f'attachment; filename=stocks_{datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")}.csv'
                }
            )
            
        except Exception as e:
            print(f"Error exporting stocks: {str(e)}")
            return {'error': str(e)}, 500
    
    @app.route('/api/stocks/export_pdf')
    @token_required
    def export_stocks_pdf(current_user):
        try:
            # Get stocks with stats for current user
            stocks_with_stats = db.session.query(Stock).join(StockStats).join(user_stock_stats).filter(user_stock_stats.c.user_id == current_user.id).all()
            
            if not stocks_with_stats:
                return jsonify({'error': 'No stock stats found for export'}), 404

            # Create PDF buffer
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter)
            styles = getSampleStyleSheet()
            elements = []

            # Create centered title style
            centered_title_style = ParagraphStyle(
                'CenteredTitle',
                parent=styles['Heading1'],
                fontSize=24,
                spaceAfter=10,  # Reduced space after title
                alignment=1  # 1 = center alignment
            )

            # Create date style
            date_style = ParagraphStyle(
                'DateStyle',
                parent=styles['Normal'],
                fontSize=12,
                spaceAfter=30,  # Space after date
                alignment=1  # 1 = center alignment
            )

            centered_heading_style = ParagraphStyle(
                'CenteredHeading',
                parent=styles['Heading2'],
                fontSize=18,
                spaceAfter=10,
                alignment=1  # 1 = center alignment
            )

            # Add title and date
            elements.append(Paragraph("Stock Statistics Report", centered_title_style))
            elements.append(Paragraph(f"Generated on {datetime.now(timezone.utc).strftime('%B %d, %Y at %I:%M %p %Z')}", date_style))

            # Add detailed table first
            elements.append(Paragraph("Stock Statistics", centered_heading_style))
            elements.append(Spacer(1, 10))
            table_style = TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 14),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 12),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ])            
            table_data = [['Symbol', 'Price', 'Market Cap', 'EPS', 'P/E', 'P/B', 'Last Updated']]
            for stock in stocks_with_stats:
                table_data.append([
                    stock.symbol,
                    f"{stock.stats.price:,.2f}",
                    f"{stock.stats.market_cap:,.0f}",
                    f"{stock.stats.eps:,.2f}",
                    f"{stock.stats.pe:,.2f}",
                    f"{stock.stats.pb:,.2f}",
                    stock.stats.last_updated.strftime('%Y-%m-%d %H:%M:%S')
                ])

            table = Table(table_data)
            table.setStyle(table_style)
            elements.append(table)
            
            # Add spacer    
            elements.append(Spacer(1, 20))
            
            # Add table for symbol and name
            elements.append(Paragraph("Stock Information", centered_heading_style))
            elements.append(Spacer(1, 10))
            table_data = [['Symbol', 'Name']]
            for stock in stocks_with_stats:
                table_data.append([
                    stock.symbol,
                    stock.name,
                ])
            table = Table(table_data)
            table.setStyle(table_style)
            elements.append(table)

            # Create bar charts with larger text and better styling
            plt.rcParams.update({
                'font.size': 16,
                'axes.titlesize': 20,
                'axes.labelsize': 16,
                'xtick.labelsize': 14,
                'ytick.labelsize': 14,
                'figure.facecolor': 'white',
                'axes.facecolor': 'white',
                'axes.grid': True,
                'grid.color': '#E0E0E0',
                'grid.linestyle': '--',
                'grid.alpha': 0.7
            })

            # Define a color palette for charts
            chart_colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEEAD']

            # Define chart configurations
            chart_configs = [
                {
                    'data': [stock.stats.price for stock in stocks_with_stats],
                    'title': 'Stock Prices',
                    'format': '{:,.2f}',
                    'ylabel': 'Price (x1000 VND)'
                },
                {
                    'data': [stock.stats.market_cap for stock in stocks_with_stats],
                    'title': 'Market Capitalization',
                    'format': '{:,.2f}',
                    'ylabel': 'Market Cap (Billion VND)'
                },
                {
                    'data': [stock.stats.eps for stock in stocks_with_stats],
                    'title': 'Earnings Per Share (EPS)',
                    'format': '{:,.2f}',
                    'ylabel': 'EPS (x1000 VND)'
                },
                {
                    'data': [stock.stats.pe for stock in stocks_with_stats],
                    'title': 'Price-to-Earnings Ratio (P/E)',
                    'format': '{:,.2f}',
                    'ylabel': 'P/E Ratio'
                },
                {
                    'data': [stock.stats.pb for stock in stocks_with_stats],
                    'title': 'Price-to-Book Ratio (P/B)',
                    'format': '{:,.2f}',
                    'ylabel': 'P/B Ratio'
                }
            ]

            # Create charts
            charts = []
            for i, config in enumerate(chart_configs):
                plt.figure(figsize=(12, 7))
                
                # Create 3D-like effect with shadow
                bars = plt.bar([stock.symbol for stock in stocks_with_stats], config['data'],
                             color=chart_colors[i % len(chart_colors)],
                             edgecolor='white',
                             linewidth=1.5,
                             alpha=0.8)
                
                # Add shadow effect
                for bar in bars:
                    bar.set_path_effects([
                        path_effects.withSimplePatchShadow(),
                        path_effects.Normal()
                    ])
                
                plt.title(config['title'], pad=20, fontweight='bold')
                plt.xlabel('')  # Remove x-axis label
                plt.ylabel(config['ylabel'], fontweight='bold')
                plt.xticks(rotation=45, ha='right')
                
                # Add value labels on top of bars with improved visibility
                for bar in bars:
                    height = bar.get_height()
                    plt.text(bar.get_x() + bar.get_width()/2., height,
                            config['format'].format(height),
                            ha='center', va='bottom',
                            fontsize=12,
                            fontweight='bold',
                            color='#2C3E50')
                
                # Add subtle background color
                plt.gca().set_facecolor('#F8F9FA')
                
                # Adjust layout to prevent label cutoff
                plt.tight_layout()
                
                # Add padding around the plot
                plt.subplots_adjust(top=0.9, bottom=0.15, left=0.1, right=0.95)
                
                chart_buffer = io.BytesIO()
                plt.savefig(chart_buffer, format='png', dpi=300, bbox_inches='tight')
                plt.close()
                chart_buffer.seek(0)
                charts.append((chart_buffer, config['title']))

            # Create a frame for centered content
            frame = Frame(
                doc.leftMargin,
                doc.bottomMargin,
                doc.width,
                doc.height,
                id='normal'
            )

            # Create a page template with the centered frame
            template = PageTemplate(id='centered', frames=[frame])
            doc.addPageTemplates([template])

            # Add page break before first chart to ensure it starts on a new page
            elements.append(PageBreak())

            for i, (chart_data, title) in enumerate(charts):
                if i > 0:  # Add page break before each chart except the first one
                    elements.append(PageBreak())
                elements.append(Paragraph(title, centered_heading_style))
                elements.append(Spacer(1, 5))  # Reduced space between title and chart
                
                # Calculate center position for the chart
                img = Image(chart_data, width=7*inch, height=4*inch)
                # Add spacer before chart to center it vertically
                elements.append(Spacer(1, 2*inch))  # Add space to push chart down
                elements.append(img)
                elements.append(Spacer(1, 2*inch))  # Add space after chart to maintain vertical centering

            # Build PDF
            doc.build(elements)

            # Create response
            buffer.seek(0)
            return Response(
                buffer.getvalue(),
                mimetype='application/pdf',
                headers={
                    'Content-Disposition': f'attachment; filename=stock_stats_{datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")}.pdf'
                }
            )

        except Exception as e:
            print(f"Error exporting stocks to PDF: {str(e)}")
            return jsonify({'error': str(e)}), 500 
    