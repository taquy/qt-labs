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
        'price': fields.Float(description='Current price'),
        'market_cap': fields.Float(description='Market capitalization'),
        'eps': fields.Float(description='Earnings per share'),
        'pe': fields.Float(description='Price-to-earnings ratio'),
        'pb': fields.Float(description='Price-to-book ratio'),
        'last_updated': fields.DateTime(readonly=True, description='Last update timestamp')
    })

    stock_exchange_model = stocks_ns.model('StockExchange', {
        'exchange': fields.String(required=True, description='Stock exchange name')
    })

    pull_stats_request_model = stocks_ns.model('PullStatsRequest', {
        'selectedStocks': fields.List(fields.String, required=True, description='List of stock symbols to update'),
        'loadLatestData': fields.Boolean(required=True, description='Whether to load latest data')
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
                
                # Query with pagination
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
        @stocks_ns.marshal_with(stock_stats_model)
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
                print(e)
                return jsonify({'error': str(e)}), 500
    

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
        @token_required
        def get(self, current_user):
            """Export stock data to PDF with charts"""
            try:
                # Get all stocks with their stats
                stocks = Stock.query.all()
                stocks_with_stats = []
                for stock in stocks:
                    stats = StockStats.query.get(stock.symbol)
                    if stats:
                        stocks_with_stats.append((stock, stats))
                
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
                        'data': [stats.price / 1000 for _, stats in stocks_with_stats],  # Convert to thousands
                        'title': 'Stock Prices',
                        'format': '{:,.2f}',
                        'ylabel': 'Price (x1000 VND)'
                    },
                    {
                        'data': [stats.market_cap / 1_000_000_000 for _, stats in stocks_with_stats],  # Convert to billions
                        'title': 'Market Capitalization',
                        'format': '{:,.2f}',
                        'ylabel': 'Market Cap (Billion VND)'
                    },
                    {
                        'data': [stats.eps / 1000 for _, stats in stocks_with_stats],  # Convert to thousands
                        'title': 'Earnings Per Share (EPS)',
                        'format': '{:,.2f}',
                        'ylabel': 'EPS (x1000 VND)'
                    },
                    {
                        'data': [stats.pe for _, stats in stocks_with_stats],
                        'title': 'Price-to-Earnings Ratio (P/E)',
                        'format': '{:,.2f}',
                        'ylabel': 'P/E Ratio'
                    },
                    {
                        'data': [stats.pb for _, stats in stocks_with_stats],
                        'title': 'Price-to-Book Ratio (P/B)',
                        'format': '{:,.2f}',
                        'ylabel': 'P/B Ratio'
                    }
                ]

                # Create charts
                charts = []
                for i, config in enumerate(chart_configs):
                    fig = plt.figure(figsize=(12, 7))
                    ax = fig.add_subplot(111, projection='3d')
                    
                    # Create 3D bars
                    x = np.arange(len([stock.symbol for stock, _ in stocks_with_stats]))
                    y = np.ones_like(x)
                    z = config['data']
                    
                    dx = dy = 0.8
                    bars = ax.bar3d(x, y, np.zeros_like(z), dx, dy, z,
                                  color=chart_colors[i % len(chart_colors)],
                                  alpha=0.8,
                                  edgecolor='white',
                                  linewidth=1.5)
                    
                    # Customize the 3D view
                    ax.view_init(elev=20, azim=45)
                    
                    # Set labels and title
                    ax.set_title(config['title'], pad=20, fontweight='bold')
                    ax.set_xlabel('')
                    ax.set_ylabel('')
                    ax.set_zlabel(config['ylabel'], fontweight='bold')
                    
                    # Set x-axis ticks
                    ax.set_xticks(x)
                    ax.set_xticklabels([stock.symbol for stock, _ in stocks_with_stats], rotation=45, ha='right')
                    
                    # Add value labels on top of bars
                    for j, height in enumerate(z):
                        ax.text(x[j] + dx/2,
                               1 + dy/2,
                               height + 0.1,
                               config['format'].format(height),
                               ha='center', va='bottom',
                               fontsize=12,
                               fontweight='bold',
                               color='#2C3E50')
                    
                    # Add subtle background color
                    ax.set_facecolor('#F8F9FA')
                    
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

                # Add charts to PDF (1 per page)
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
                output.seek(0)
                
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
        @token_required
        def post(self, current_user):
            """Remove all stock statistics"""
            try:
                StockStats.query.delete()
                db.session.commit()
                return {'message': 'All stock statistics removed successfully'}
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