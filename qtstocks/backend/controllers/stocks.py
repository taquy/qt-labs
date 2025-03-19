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
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
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

            # Add title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                spaceAfter=30
            )
            elements.append(Paragraph("Stock Statistics Report", title_style))

            # Create bar charts
            symbols = [stock.symbol for stock in stocks_with_stats]
            prices = [stock.stats.price for stock in stocks_with_stats]
            market_caps = [stock.stats.market_cap for stock in stocks_with_stats]
            eps_values = [stock.stats.eps for stock in stocks_with_stats]
            pe_values = [stock.stats.pe for stock in stocks_with_stats]
            pb_values = [stock.stats.pb for stock in stocks_with_stats]

            # Create price chart
            plt.figure(figsize=(10, 6))
            plt.bar(symbols, prices)
            plt.title('Stock Prices')
            plt.xticks(rotation=45)
            plt.tight_layout()
            price_chart = io.BytesIO()
            plt.savefig(price_chart, format='png')
            plt.close()
            price_chart.seek(0)

            # Create market cap chart
            plt.figure(figsize=(10, 6))
            plt.bar(symbols, market_caps)
            plt.title('Market Capitalization')
            plt.xticks(rotation=45)
            plt.tight_layout()
            market_cap_chart = io.BytesIO()
            plt.savefig(market_cap_chart, format='png')
            plt.close()
            market_cap_chart.seek(0)

            # Create EPS chart
            plt.figure(figsize=(10, 6))
            plt.bar(symbols, eps_values)
            plt.title('Earnings Per Share (EPS)')
            plt.xticks(rotation=45)
            plt.tight_layout()
            eps_chart = io.BytesIO()
            plt.savefig(eps_chart, format='png')
            plt.close()
            eps_chart.seek(0)

            # Create P/E chart
            plt.figure(figsize=(10, 6))
            plt.bar(symbols, pe_values)
            plt.title('Price-to-Earnings Ratio (P/E)')
            plt.xticks(rotation=45)
            plt.tight_layout()
            pe_chart = io.BytesIO()
            plt.savefig(pe_chart, format='png')
            plt.close()
            pe_chart.seek(0)

            # Create P/B chart
            plt.figure(figsize=(10, 6))
            plt.bar(symbols, pb_values)
            plt.title('Price-to-Book Ratio (P/B)')
            plt.xticks(rotation=45)
            plt.tight_layout()
            pb_chart = io.BytesIO()
            plt.savefig(pb_chart, format='png')
            plt.close()
            pb_chart.seek(0)

            # Add charts to PDF
            from reportlab.platypus import Image
            for chart_data, title in [
                (price_chart, "Stock Prices"),
                (market_cap_chart, "Market Capitalization"),
                (eps_chart, "Earnings Per Share (EPS)"),
                (pe_chart, "Price-to-Earnings Ratio (P/E)"),
                (pb_chart, "Price-to-Book Ratio (P/B)")
            ]:
                elements.append(Paragraph(title, styles['Heading2']))
                img = Image(chart_data, width=7*inch, height=4*inch)
                elements.append(img)
                elements.append(Spacer(1, 20))

            # Add detailed table
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
            table_data = [['Symbol', 'Name']]
            for stock in stocks_with_stats:
                table_data.append([
                    stock.symbol,
                    stock.name,
                ])
            table = Table(table_data)
            table.setStyle(table_style)
            elements.append(table)

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
    