from flask import Flask, render_template, jsonify, request, Response, send_file, redirect, url_for, flash, session
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate
import pandas as pd
import plotly
import plotly.express as px
import json
from scrape import process_stock_list
import threading
import queue
from datetime import datetime, timedelta
import io
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from models import db, User, Stock
from config import Config
import requests
from bs4 import BeautifulSoup
from get_stock_lists import get_stock_list

app = Flask(__name__)
app.config.from_object(Config)

# Initialize Flask-Login and CSRF protection
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'

csrf = CSRFProtect(app)

# Initialize database and migrations
db.init_app(app)
migrate = Migrate(app, db)

# Queue for SSE messages
message_queue = queue.Queue()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/login', methods=['GET', 'POST'])
def login():
    try:
        # Redirect if user is already logged in
        if current_user.is_authenticated:
            return redirect(url_for('index'))
            
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            
            if not username or not password:
                flash('Please enter both username and password.', 'error')
                return render_template('login.html')
            
            user = User.query.filter_by(username=username).first()
            if user and check_password_hash(user.password_hash, password):
                login_user(user)
                next_page = request.args.get('next')
                if not next_page or not next_page.startswith('/'):
                    next_page = url_for('index')
                flash('Logged in successfully.', 'success')
                return redirect(next_page)
            
            flash('Invalid username or password.', 'error')
        
        return render_template('login.html')
    except Exception as e:
        print(f"Login error: {str(e)}")
        flash('An error occurred during login. Please try again.', 'error')
        return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('login'))

def load_stock_data():
    try:
        stocks = Stock.query.all()
        data = [stock.to_dict() for stock in stocks]
        df = pd.DataFrame(data)
        
        # Convert column names to match frontend expectations
        column_mapping = {
            'symbol': 'Symbol',
            'name': 'Name',
            'price': 'Price',
            'market_cap': 'MarketCap',
            'eps': 'EPS',
            'pe_ratio': 'P/E',
            'pb_ratio': 'P/B'
        }
        
        df = df.rename(columns=column_mapping)
        return df
    except Exception as e:
        print(f"Error loading data: {str(e)}")
        return None

def scrape_stocks_async(symbols, force_update=False):
    try:
        # If force_update is True, scrape all symbols, otherwise only new ones
        if force_update:
            new_symbols = symbols
            message = f'Updating data for {len(symbols)} stocks'
        else:
            # Filter out symbols that already have data
            existing_symbols = [stock.symbol for stock in Stock.query.all()]
            new_symbols = [s for s in symbols if s not in existing_symbols]
            
            if not new_symbols:
                message_queue.put(json.dumps({
                    'status': 'completed',
                    'message': 'All stocks already have data',
                    'total_processed': 0
                }))
                return
            message = f'Found {len(new_symbols)} new stocks to scrape'
        
        total_stocks = len(new_symbols)
        message_queue.put(json.dumps({
            'status': 'info',
            'message': message
        }))
        
        # Process stocks one by one and send progress updates
        for idx, symbol in enumerate(new_symbols, 1):
            try:
                # Send progress update
                message_queue.put(json.dumps({
                    'status': 'progress',
                    'message': f'Scraping {symbol} ({idx}/{total_stocks})',
                    'current': idx,
                    'total': total_stocks,
                    'symbol': symbol
                }))
                
                # Process the stock
                result = process_stock_list([symbol])[0]  # Get single stock result
                
                # Update or create stock in database
                stock = Stock.query.filter_by(symbol=symbol).first()
                if stock:
                    # Update existing stock
                    stock.name = result.get('Name')
                    stock.price = result.get('Price')
                    stock.market_cap = result.get('MarketCap')
                    stock.eps = result.get('EPS')
                    stock.pe_ratio = result.get('P/E')
                    stock.pb_ratio = result.get('P/B')
                    stock.last_updated = datetime.utcnow()
                else:
                    # Create new stock
                    stock = Stock.from_dict(result)
                    db.session.add(stock)
                
                db.session.commit()
                
            except Exception as e:
                print(f"Error processing {symbol}: {str(e)}")
                db.session.rollback()
        
        print("Scraping completed successfully")
        # Send completion message to queue
        message_queue.put(json.dumps({
            'status': 'completed',
            'total_processed': total_stocks
        }))
    except Exception as e:
        print(f"Error during scraping: {str(e)}")
        # Send error message to queue
        message_queue.put(json.dumps({
            'status': 'error',
            'message': str(e)
        }))

@app.route('/stream')
@login_required
def stream():
    def event_stream():
        while True:
            try:
                # Get message from queue with timeout
                message = message_queue.get(timeout=30)
                yield f"data: {message}\n\n"
            except queue.Empty:
                # Send keepalive message
                yield f"data: {json.dumps({'status': 'keepalive'})}\n\n"
    
    return Response(event_stream(), mimetype='text/event-stream')

@app.route('/')
@login_required
def index():
    df = load_stock_data()
    stocks = []
    if df is not None and not df.empty and 'Symbol' in df.columns:
        stocks = df['Symbol'].tolist()
    metrics = ['Price', 'MarketCap', 'EPS', 'P/E', 'P/B']
    return render_template('index.html', stocks=stocks, metrics=metrics)

@app.route('/scrape_stocks', methods=['POST'])
@login_required
def scrape_stocks():
    try:
        data = request.json
        symbols = data.get('symbols', [])
        
        if not symbols:
            return jsonify({'error': 'No symbols provided'})
        
        # Start scraping in a background thread
        thread = threading.Thread(target=scrape_stocks_async, args=(symbols,))
        thread.start()
        
        return jsonify({'message': 'Scraping started'})
    except Exception as e:
        return jsonify({'error': str(e)})

def get_stocks_list():
    """Helper function to get list of stocks from the database."""
    try:
        stocks = Stock.query.all()
        return [stock.symbol for stock in stocks]
    except Exception as e:
        print(f"Error getting stocks: {e}")
        return []

@app.route('/get_stocks')
@login_required
def get_stocks():
    try:
        stocks = get_stocks_list()
        return jsonify({'stocks': stocks})
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/update_graph', methods=['POST'])
@login_required
def update_graph():
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No data received'}), 400
            
        selected_stocks = data.get('stocks', [])
        selected_metric = data.get('metric', 'Price')
        
        if not selected_stocks:
            return jsonify({'error': 'No stocks selected'}), 400
            
        if not selected_metric:
            return jsonify({'error': 'No metric selected'}), 400
        
        print(f"Updating graph for stocks: {selected_stocks}, metric: {selected_metric}")
        
        df = load_stock_data()
        if df is None:
            return jsonify({'error': 'Error loading stock data'}), 500
        
        # Filter data for selected stocks
        filtered_df = df[df['Symbol'].isin(selected_stocks)]
        
        if filtered_df.empty:
            return jsonify({'error': 'No data found for selected stocks'}), 404
        
        # Sort by selected metric
        filtered_df = filtered_df.sort_values(by=selected_metric, ascending=True)
        
        # Create bar chart
        fig = px.bar(
            filtered_df,
            x='Symbol',
            y=selected_metric,
            title=f'Comparison of {selected_metric} across Selected Stocks',
            labels={'Symbol': 'Stock Symbol', selected_metric: selected_metric},
            template='plotly_white',
            color='Symbol',
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        
        # Update layout
        fig.update_layout(
            showlegend=True,
            plot_bgcolor='white',
            height=500,
            title_x=0.5,
            title_font_size=20,
            bargap=0.2,
            xaxis=dict(
                title_font=dict(size=14),
                tickfont=dict(size=12),
                gridcolor='lightgray'
            ),
            yaxis=dict(
                title_font=dict(size=14),
                tickfont=dict(size=12),
                gridcolor='lightgray'
            )
        )
        
        # Convert plot to JSON
        graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        return jsonify(graphJSON)
    except Exception as e:
        print(f"Error in update_graph: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/update_all_stocks', methods=['POST'])
def update_all_stocks():
    try:
        # Get all existing stocks
        stocks = Stock.query.all()
        if not stocks:
            return jsonify({'error': 'No stocks found to update'})
        
        symbols = [stock.symbol for stock in stocks]
        
        if not symbols:
            return jsonify({'error': 'No stocks found to update'})
        
        # Start scraping in a background thread with force_update=True
        thread = threading.Thread(target=scrape_stocks_async, args=(symbols, True))
        thread.start()
        
        return jsonify({'message': 'Update started'})
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/export_csv')
@login_required
def export_csv():
    try:
        # Load and prepare the data
        df = load_stock_data()
        if df is None:
            return jsonify({'error': 'Error loading stock data'})
        
        # Create a buffer to store the CSV
        buffer = io.StringIO()
        df.to_csv(buffer, index=False)
        buffer.seek(0)
        
        # Generate filename with current date
        filename = f"stock_data_{datetime.now().strftime('%Y%m%d')}.csv"
        
        # Send the file
        return send_file(
            io.BytesIO(buffer.getvalue().encode('utf-8')),
            mimetype='text/csv',
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/export_pdf', methods=['POST'])
@login_required
def export_pdf():
    try:
        df = load_stock_data()
        if df is None:
            return jsonify({'error': 'Error loading stock data'})
        
        data = request.json
        selected_stocks = data.get('stocks', [])
        
        if not selected_stocks:
            return jsonify({'error': 'No stocks selected'})
        
        # Filter data for selected stocks
        filtered_df = df[df['Symbol'].isin(selected_stocks)]
        
        # Create a list of all metrics
        metrics = ['Price', 'MarketCap', 'EPS', 'P/E', 'P/B']
        
        # Create subplots
        fig = make_subplots(
            rows=len(metrics),
            cols=1,
            subplot_titles=[f'Comparison of {metric} across Selected Stocks' for metric in metrics],
            vertical_spacing=0.1
        )
        
        # Add each metric as a subplot
        for idx, metric in enumerate(metrics, 1):
            # Sort by metric value
            metric_df = filtered_df.sort_values(by=metric, ascending=True)
            
            # Format values for display
            if metric in ['Price', 'MarketCap']:
                text_values = metric_df[metric].apply(lambda x: f'{x:,.0f}')
            else:
                text_values = metric_df[metric].apply(lambda x: f'{x:.2f}')
            
            # Add bar trace
            fig.add_trace(
                go.Bar(
                    x=metric_df['Symbol'],
                    y=metric_df[metric],
                    name=metric,
                    text=text_values,
                    textposition='auto',
                    marker_color=px.colors.qualitative.Set3[idx % len(px.colors.qualitative.Set3)],
                    showlegend=False,
                    hovertemplate="<b>%{x}</b><br>" +
                                f"{metric}: %{{y:,.2f}}<br>" +
                                "<extra></extra>"
                ),
                row=idx,
                col=1
            )
            
            # Update axes labels
            fig.update_xaxes(title_text="Stock Symbol", row=idx, col=1, gridcolor='lightgray')
            fig.update_yaxes(title_text=metric, row=idx, col=1, gridcolor='lightgray')
        
        # Update layout
        fig.update_layout(
            height=300 * len(metrics),
            width=1000,
            showlegend=False,
            plot_bgcolor='white',
            title={
                'text': 'Stock Comparison Analysis',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 24}
            },
            margin=dict(t=100, b=50),
            bargap=0.2,
            paper_bgcolor='white'
        )
        
        # Generate PDF bytes
        img_bytes = fig.to_image(format="pdf")
        
        # Generate filename with current date
        filename = f"stock_charts_{datetime.now().strftime('%Y%m%d')}.pdf"
        
        # Send the file
        return send_file(
            io.BytesIO(img_bytes),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        print(f"Error in export_pdf: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/save_stocks', methods=['POST'])
@login_required
def save_stocks():
    try:
        data = request.get_json()
        new_symbols = data.get('symbols', [])
        
        # Get current stocks from the database
        current_stocks = get_stocks_list()
        
        # Find stocks to remove (stocks that are in current_stocks but not in new_symbols)
        stocks_to_remove = set(current_stocks) - set(new_symbols)
        
        if stocks_to_remove:
            # Remove the stocks from the database
            Stock.query.filter(Stock.symbol.in_(stocks_to_remove)).delete(synchronize_session=False)
            db.session.commit()
            
            # Send message through queue
            message_queue.put(json.dumps({
                'status': 'info',
                'message': f'Removed {len(stocks_to_remove)} stocks: {", ".join(stocks_to_remove)}'
            }))
        
        # Find new stocks to add (stocks that are in new_symbols but not in current_stocks)
        stocks_to_add = set(new_symbols) - set(current_stocks)
        
        if stocks_to_add:
            # Start scraping process for new stocks
            thread = threading.Thread(target=scrape_stocks_async, args=(list(stocks_to_add),))
            thread.daemon = True
            thread.start()
        else:
            # If no new stocks to add, send completion message
            message_queue.put(json.dumps({
                'status': 'completed',
                'message': 'Stock list updated successfully',
                'total_processed': 0
            }))
        
        return jsonify({'status': 'success'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/get_available_stocks')
@login_required
def get_available_stocks():
    try:
        stocks = Stock.query.all()
        return jsonify({
            'stocks': [
                {
                    'symbol': stock.symbol,
                    'name': stock.name
                }
                for stock in stocks
            ]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download_stock_list')
@login_required
def download_stock_list():
    try:
        # Call get_stock_list function from get_stock_lists.py
        stocks = get_stock_list()
        
        # Store in database
        for stock_data in stocks:
            existing_stock = Stock.query.filter_by(symbol=stock_data['Symbol']).first()
            if not existing_stock:
                stock = Stock(
                    symbol=stock_data['Symbol'],
                    name=stock_data['Name'],
                    last_updated=datetime.utcnow()
                )
                db.session.add(stock)
        
        db.session.commit()
        
        # Convert to lowercase keys for frontend consistency
        stocks_for_frontend = [
            {
                'symbol': stock['Symbol'],
                'name': stock['Name']
            }
            for stock in stocks
        ]
        
        # Return the stock list as JSON
        return jsonify({
            'success': True,
            'stocks': stocks_for_frontend,
            'message': f'Successfully downloaded {len(stocks)} stocks'
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Error in download_stock_list: {str(e)}")  # Add logging
        return jsonify({'error': str(e)}), 500

def init_db():
    with app.app_context():
        db.create_all()
        # Create admin user if it doesn't exist
        admin = User.query.filter_by(username=Config.ADMIN_USERNAME).first()
        if not admin:
            admin = User(
                username=Config.ADMIN_USERNAME,
                password_hash=generate_password_hash(Config.ADMIN_PASSWORD)
            )
            db.session.add(admin)
            db.session.commit()

if __name__ == '__main__':
    init_db()
    app.run(debug=True) 