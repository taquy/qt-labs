from flask import jsonify, request, current_app, send_file
from models import Stock, StockStats, db, User, StockExchanges
from datetime import datetime, timezone
from functools import wraps
from flask_restx import Resource, fields
import pandas as pd
import plotly
import plotly.express as px
import json
import threading
import queue
import io
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.patheffects as path_effects
import numpy as np
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, Frame, PageTemplate
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from services.get_stock_data import process_stock_list
from services.get_stock_lists import pull_stock_list

def init_stock_routes(app, token_required, stocks_ns):
    # Define models for Swagger documentation
    stock_model = stocks_ns.model('Stock', {
        'symbol': fields.String(required=True, description='Stock symbol'),
        'name': fields.String(required=True, description='Stock name'),
        'icon': fields.String(description='Stock icon URL'),
        'exchange': fields.String(description='Stock exchange'),
        'last_updated': fields.DateTime(readonly=True, description='Last update timestamp')
    })

    paginated_stock_model = stocks_ns.model('PaginatedStock', {
        'items': fields.List(fields.Nested(stock_model), description='List of stocks'),
        'total': fields.Integer(description='Total number of stocks'),
        'pages': fields.Integer(description='Total number of pages'),
        'current_page': fields.Integer(description='Current page number'),
        'has_next': fields.Boolean(description='Whether there is a next page'),
        'has_prev': fields.Boolean(description='Whether there is a previous page')
    })

    stock_stats_model = stocks_ns.model('StockStats', {
        'symbol': fields.String(required=True, description='Stock symbol'),
        'name': fields.String(required=True, description='Stock name'),
        'icon': fields.String(description='Stock icon URL'),
        'exchange': fields.String(description='Stock exchange'),
        'price': fields.Float(description='Current price'),
        'market_cap': fields.Float(description='Market capitalization'),
        'eps': fields.Float(description='Earnings per share'),
        'pe': fields.Float(description='Price-to-earnings ratio'),
        'pb': fields.Float(description='Price-to-book ratio'),
        'last_updated': fields.String(description='Last update timestamp')
    })

    stock_exchange_model = stocks_ns.model('StockExchange', {
        'exchange': fields.String(required=True, description='Stock exchange name')
    })

    pull_stats_request_model = stocks_ns.model('PullStatsRequest', {
        'selectedStocks': fields.List(fields.String, required=True, description='List of stock symbols to update'),
        'loadLatestData': fields.Boolean(required=True, description='Whether to load latest data')
    })

    remove_stats_request_model = stocks_ns.model('RemoveStatsRequest', {
        'symbols': fields.List(fields.String, required=True, description='List of stock symbols to remove')
    })

    @stocks_ns.route('')
    class StockList(Resource):
        @stocks_ns.doc('list_stocks', security='Bearer')
        @stocks_ns.param('page', 'Page number (1-based)', type=int, default=1)
        @stocks_ns.param('per_page', 'Items per page', type=int, default=10)
        @stocks_ns.param('search', 'Search by symbol or name (partial match, UTF-8 supported)', type=str)
        @stocks_ns.param('exchanges', 'Filter by exchanges (comma-separated list)', type=str)
        @stocks_ns.marshal_with(paginated_stock_model)
        @token_required
        def get(self, current_user):
            """List all stocks with pagination, search and filter"""
            try:
                page = request.args.get('page', 1, type=int)
                per_page = request.args.get('per_page', 10, type=int)
                search = request.args.get('search', '').strip()
                exchanges = [ex.strip() for ex in request.args.get('exchanges', '').split(',') if ex.strip()]
                
                # Build query
                query = Stock.query
                
                # Apply search filter if provided
                if search:
                    search_term = f"%{search}%"
                    # Use unaccent for better UTF-8 support
                    query = query.filter(
                        db.or_(
                            Stock.symbol.ilike(search_term),
                            db.func.unaccent(Stock.name).ilike(db.func.unaccent(search_term))
                        )
                    )
                
                # Apply exchanges filter if provided
                if exchanges:
                    query = query.filter(Stock.exchange.in_(exchanges))
                    
                # Filter out stocks that are already in user's stock_stats
                user_stock_symbols = [stat.symbol for stat in current_user.stock_stats]
                query = query.filter(~Stock.symbol.in_(user_stock_symbols))
                
                # Query with pagination
                # Sort by market_cap in descending order, handling NULL values last
                query = query.order_by(db.desc(db.func.coalesce(Stock.market_cap, 0)))
                pagination = query.paginate(
                    page=page,
                    per_page=per_page,
                    error_out=False
                )
                
                return {
                    'items': pagination.items,
                    'total': pagination.total,
                    'pages': pagination.pages,
                    'current_page': page,
                    'has_next': pagination.has_next,
                    'has_prev': pagination.has_prev
                }
            except Exception as e:
                stocks_ns.abort(500, message=str(e))

    @stocks_ns.route('/pull_stock_list')
    class PullStockLists(Resource):
        @stocks_ns.doc('pull_stock_list', security='Bearer')
        @token_required
        def get(self, current_user):
            """Pull stock lists"""
            message, error = pull_stock_list()
            if error:
                stocks_ns.abort(500, message)
            return {'message': message}
            
    @stocks_ns.route('/<string:symbol>')
    @stocks_ns.param('symbol', 'The stock symbol')
    class StockResource(Resource):
        @stocks_ns.doc('get_stock', security='Bearer')
        @stocks_ns.marshal_with(stock_model)
        @token_required
        def get(self, current_user, symbol):
            """Get a stock by symbol"""
            return Stock.query.get_or_404(symbol)

    @stocks_ns.route('/stats')
    @stocks_ns.param('symbol', 'The stock symbol')
    class StockStatsResource(Resource):
        @stocks_ns.doc('get_stock_stats', security='Bearer')
        @stocks_ns.marshal_list_with(stock_stats_model)
        @token_required
        def get(self, current_user):
            """Get stats for all stocks in user's portfolio"""
            try:
                # Query stocks that have stats
                user_stock_symbols = [stock.symbol for stock in current_user.stock_stats]
                stocks_with_stats = db.session.query(Stock)\
                    .join(StockStats, Stock.symbol == StockStats.symbol)\
                    .filter(Stock.symbol.in_(user_stock_symbols))\
                    .all()
                return [
                    {
                        'symbol': stock.symbol,
                        'name': stock.name,
                        'icon': stock.icon,
                        'exchange': stock.exchange,
                        'last_updated': stock.stats.last_updated.strftime('%Y-%m-%d %H:%M:%S'),
                        'price': stock.stats.price,
                        'market_cap': stock.stats.market_cap,
                        'eps': stock.stats.eps,
                        'pe': stock.stats.pe,
                        'pb': stock.stats.pb
                    } for stock in stocks_with_stats
                ]
            except Exception as e:
                stocks_ns.abort(500, message=str(e))
    

    @stocks_ns.route('/pull_stock_stats')
    class UpdateStockStats(Resource):
        @stocks_ns.doc('pull_stock_stats', security='Bearer')
        @stocks_ns.expect(pull_stats_request_model)
        @token_required
        def post(self, current_user):
            """Pull stock statistics for selected stocks"""
            try:
                data = request.get_json()
                selected_stocks = data.get('selectedStocks', [])
                load_latest_data = data.get('loadLatestData', False)

                if not selected_stocks:
                    stocks_ns.abort(400, message="No stocks selected")
                    
                if not load_latest_data:
                    stock_stats = db.session.query(StockStats.symbol).all();
                    existed_symbols = [stock_stat.symbol for stock_stat in stock_stats]
                    selected_stocks = [symbol for symbol in selected_stocks if symbol not in existed_symbols]
                    # Add any existing symbols to user's stock_stats if not already present
                    for symbol in existed_symbols:
                        # Get the existing stats
                        stats = StockStats.query.filter_by(symbol=symbol).first()
                        if stats and stats not in current_user.stock_stats:
                            current_user.stock_stats.append(stats)
                    db.session.commit()
                process_stock_list(selected_stocks, current_user)
                return {'message': 'Stock statistics updated successfully'}
            except Exception as e:
                db.session.rollback()
                stocks_ns.abort(500, f"Error updating stock statistics: {str(e)}")

    @stocks_ns.route('/export')
    class StockExport(Resource):
        @stocks_ns.doc('export_stocks', security='Bearer')
        @token_required
        def get(self, current_user):
            """Export stock data to CSV"""
            try:
                stocks = Stock.query.all()
                data = []
                for stock in stocks:
                    stats = StockStats.query.get(stock.symbol)
                    if stats:
                        data.append({
                            'Symbol': stock.symbol,
                            'Name': stock.name,
                            'Price': stats.price,
                            'Market Cap': stats.market_cap,
                            'EPS': stats.eps,
                            'P/E': stats.pe,
                            'P/B': stats.pb
                        })
                
                df = pd.DataFrame(data)
                output = io.StringIO()
                df.to_csv(output, index=False)
                output.seek(0)
                
                return send_file(
                    io.BytesIO(output.getvalue().encode('utf-8')),
                    mimetype='text/csv',
                    as_attachment=True,
                    download_name='stocks.csv'
                )
            except Exception as e:
                stocks_ns.abort(500, f"Error exporting stocks: {str(e)}")

    @stocks_ns.route('/export/pdf')
    class StockPDFExport(Resource):
        @stocks_ns.doc('export_stocks_pdf', security='Bearer')
        @stocks_ns.param('symbols', 'Comma-separated list of stock symbols to include in the report')
        @token_required
        def get(self, current_user):
            """Export stock data to PDF with charts"""
            try:
                # Get symbols from query parameter
                symbols_param = request.args.get('symbols', '')
                if not symbols_param:
                    stocks_ns.abort(400, message="No symbols provided")
                
                symbols = [s.strip() for s in symbols_param.split(',') if s.strip()]
                if not symbols:
                    stocks_ns.abort(400, message="No valid symbols provided")
                
                # Get stocks with their stats for the specified symbols
                user_stock_symbols = [stock.symbol for stock in current_user.stock_stats]
                # Filter symbols to only include those in user's portfolio
                symbols = [symbol for symbol in symbols if symbol in user_stock_symbols]
                if not symbols:
                    stocks_ns.abort(400, message="None of the provided symbols are in your portfolio")
                
                # Get stocks with their stats
                stocks_with_stats = []
                for symbol in symbols:
                    stock = Stock.query.get(symbol)
                    if stock:
                        stats = StockStats.query.get(symbol)
                        if stats:
                            stocks_with_stats.append((stock, stats))
                
                if not stocks_with_stats:
                    stocks_ns.abort(404, message="No valid stocks found for the provided symbols")
                
                # Create PDF document
                output = io.BytesIO()
                doc = SimpleDocTemplate(output, pagesize=letter)
                elements = []
                
                # Create styles
                styles = getSampleStyleSheet()
                centered_title_style = ParagraphStyle(
                    'CenteredTitle',
                    parent=styles['Heading1'],
                    fontSize=24,
                    alignment=TA_CENTER,
                    spaceAfter=30
                )
                centered_heading_style = ParagraphStyle(
                    'CenteredHeading',
                    parent=styles['Heading2'],
                    fontSize=18,
                    alignment=TA_CENTER,
                    spaceAfter=10
                )
                date_style = ParagraphStyle(
                    'Date',
                    parent=styles['Normal'],
                    fontSize=12,
                    alignment=TA_CENTER,
                    spaceAfter=30
                )
                
                # Add title and date
                elements.append(Paragraph("Stock Statistics Report", centered_title_style))
                elements.append(Paragraph(f"Generated on {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}", date_style))
                
                # Create tables
                table_data = [['Symbol', 'Price', 'Market Cap', 'EPS', 'P/E', 'P/B']]
                for stock, stats in stocks_with_stats:
                    table_data.append([
                        stock.symbol,
                        f"{stats.price:,.2f}",
                        f"{stats.market_cap:,.0f}",
                        f"{stats.eps:,.2f}",
                        f"{stats.pe:,.2f}",
                        f"{stats.pb:,.2f}"
                    ])
                
                # Create tables with titles
                for i in range(0, len(table_data), 15):  # Split into chunks of 15 rows
                    elements.append(Paragraph("Stock Statistics", centered_heading_style))
                    table = Table(table_data[i:i+15])
                    table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, 0), 12),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                        ('FONTSIZE', (0, 1), (-1, -1), 10),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black)
                    ]))
                    elements.append(table)
                    elements.append(Spacer(1, 20))
                
                # Create bar charts with clean styling
                plt.rcParams.update({
                    'font.size': 10,
                    'axes.titlesize': 14,
                    'axes.labelsize': 12,
                    'xtick.labelsize': 10,
                    'ytick.labelsize': 10,
                    'figure.facecolor': 'white',
                    'axes.facecolor': 'white',
                    'axes.grid': True,
                    'grid.color': '#E0E0E0',
                    'grid.linestyle': '--',
                    'grid.alpha': 0.5
                })

                # Define a color palette for charts
                chart_colors = ['#4ECDC4', '#45B7D1', '#96CEB4', '#FFEEAD', '#FF6B6B']

                # Define chart configurations
                chart_configs = []
                
                # Only add charts if there's data to show
                if stocks_with_stats:
                    # Stock Price chart
                    price_data = [stats.price if stats.price else 0 for _, stats in stocks_with_stats]
                    if any(price_data):  # Only add if there's at least one non-zero value
                        chart_configs.append({
                            'data': price_data,
                            'title': 'Stock Prices',
                            'format': '{:,.2f}',
                            'ylabel': 'Price (VND)'
                        })
                    
                    # Market Cap chart
                    market_cap_data = [stats.market_cap if stats.market_cap else 0 for _, stats in stocks_with_stats]
                    if any(market_cap_data):
                        chart_configs.append({
                            'data': market_cap_data,
                            'title': 'Market Capitalization',
                            'format': '{:,.0f}',
                            'ylabel': 'Market Cap (VND)'
                        })
                    
                    # EPS chart
                    eps_data = [stats.eps if stats.eps else 0 for _, stats in stocks_with_stats]
                    if any(eps_data):
                        chart_configs.append({
                            'data': eps_data,
                            'title': 'Earnings Per Share (EPS)',
                            'format': '{:,.2f}',
                            'ylabel': 'EPS (VND)'
                        })
                    
                    # PE Ratio chart
                    pe_data = [stats.pe if stats.pe else 0 for _, stats in stocks_with_stats]
                    if any(pe_data):
                        chart_configs.append({
                            'data': pe_data,
                            'title': 'Price-to-Earnings Ratio (P/E)',
                            'format': '{:,.2f}',
                            'ylabel': 'P/E Ratio'
                        })
                    
                    # PB Ratio chart
                    pb_data = [stats.pb if stats.pb else 0 for _, stats in stocks_with_stats]
                    if any(pb_data):
                        chart_configs.append({
                            'data': pb_data,
                            'title': 'Price-to-Book Ratio (P/B)',
                            'format': '{:,.2f}',
                            'ylabel': 'P/B Ratio'
                        })

                # Create charts
                charts = []
                for i, config in enumerate(chart_configs):
                    # Create figure with reduced size
                    fig, ax = plt.subplots(figsize=(8, 7.5))  # Increased height from 5 to 7.5
                    
                    # Create bars
                    x = np.arange(len([stock.symbol for stock, _ in stocks_with_stats]))
                    bars = ax.bar(x, config['data'],
                                color=chart_colors[i % len(chart_colors)],
                                alpha=0.7)
                    
                    # Customize the chart
                    ax.set_title(config['title'], pad=10)
                    ax.set_xlabel('')
                    ax.set_ylabel(config['ylabel'])
                    
                    # Set x-axis ticks
                    ax.set_xticks(x)
                    ax.set_xticklabels([stock.symbol for stock, _ in stocks_with_stats], rotation=45, ha='right')
                    
                    # Add value labels inside bars
                    for bar in bars:
                        height = bar.get_height()
                        if height > 0:  # Only add labels to bars with values
                            text = config['format'].format(height)
                            # Calculate text width in data coordinates
                            text_width = len(text) * 0.1  # Approximate width based on character count
                            bar_width = bar.get_width()
                            
                            # Position text in middle of bar
                            x_pos = bar.get_x() + bar.get_width()/2.
                            y_pos = height/2
                            
                            # If text is too wide for the bar, place it above
                            if text_width > bar_width:
                                y_pos = height + 5  # Position above bar
                                va = 'bottom'
                            else:
                                va = 'center'
                            
                            # Add text with black border effect
                            text_obj = ax.text(x_pos, y_pos, text,
                                             ha='center', va=va,
                                             fontsize=9,
                                             color='white',
                                             fontweight='bold')
                            
                            # Add black border effect
                            text_obj.set_path_effects([
                                path_effects.Stroke(linewidth=2, foreground='black'),
                                path_effects.Normal()
                            ])
                    
                    # Adjust layout
                    plt.tight_layout()
                    
                    chart_buffer = io.BytesIO()
                    plt.savefig(chart_buffer, 
                              format='png', 
                              dpi=100,
                              bbox_inches='tight')
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

                # Add page break before first chart
                elements.append(PageBreak())

                # Add charts to PDF (1 per page)
                for i, (chart_data, title) in enumerate(charts):
                    if i > 0:  # Add page break before each chart except the first one
                        elements.append(PageBreak())
                    elements.append(Paragraph(title, centered_heading_style))
                    elements.append(Spacer(1, 5))
                    
                    # Add chart with increased height
                    img = Image(chart_data, width=7*inch, height=6*inch)  # Increased height from 4 to 6
                    elements.append(Spacer(1, 1*inch))  # Reduced spacing
                    elements.append(img)
                    elements.append(Spacer(1, 1*inch))  # Reduced spacing

                # Build PDF
                doc.build(elements)
                output.seek(0)
                
                # Return the PDF file
                return send_file(
                    output,
                    mimetype='application/pdf',
                    as_attachment=True,
                    download_name='stocks_report.pdf'
                )
            except Exception as e:
                stocks_ns.abort(500, f"Error generating PDF: {str(e)}")

    @stocks_ns.route('/remove_stats')
    class RemoveStockStats(Resource):
        @stocks_ns.doc('remove_stock_stats', security='Bearer')
        @stocks_ns.expect(remove_stats_request_model)
        @token_required
        def post(self, current_user):
            """Remove stocks from user's portfolio"""
            try:
                data = request.get_json()
                symbols = data.get('symbols', [])

                if not symbols:
                    stocks_ns.abort(400, message="No symbols provided")

                # Remove stocks from user's portfolio
                for symbol in symbols:
                    stock_stats = StockStats.query.get(symbol)
                    if stock_stats and current_user in stock_stats.users:
                        current_user.stock_stats.remove(stock_stats)

                db.session.commit()
                return {'message': 'Stocks removed successfully'}
            except Exception as e:
                db.session.rollback()
                stocks_ns.abort(500, f"Error removing stock statistics: {str(e)}")

    @stocks_ns.route('/exchanges')
    class StockExchangesResource(Resource):
        @stocks_ns.doc('get_exchanges', security='bearer')
        @token_required
        def get(self, current_user):
            """Get all distinct stock exchanges"""
            try:
                exchanges = [exchange.exchange for exchange in StockExchanges.query.all()]
                return exchanges
            except Exception as e:
                stocks_ns.abort(500, message=str(e)) 