from flask import Flask, render_template, jsonify, request, Response, send_file, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf.csrf import CSRFProtect
import pandas as pd
import plotly
import plotly.express as px
import json
from scrape import process_stock_list
import threading
import queue
from datetime import datetime
import io
from plotly.subplots import make_subplots
import plotly.graph_objects as go

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this to a secure secret key
app.config['WTF_CSRF_ENABLED'] = True
app.config['WTF_CSRF_SECRET_KEY'] = 'csrf-secret-key'  # Change this in production

# Initialize Flask-Login and CSRF protection
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'

csrf = CSRFProtect(app)

# User model
class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username

    def get_id(self):
        return str(self.id)  # Convert id to string for Flask-Login

# In-memory user storage (replace with database in production)
users = {
    'admin': {
        'id': 1,
        'username': 'admin',
        'password': generate_password_hash('admin123')  # Change this password in production
    }
}

@login_manager.user_loader
def load_user(user_id):
    # Find user by id
    for username, user_data in users.items():
        if str(user_data['id']) == user_id:
            return User(user_data['id'], user_data['username'])
    return None

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
            
            if username in users and check_password_hash(users[username]['password'], password):
                user = User(users[username]['id'], users[username]['username'])
                login_user(user)
                next_page = request.args.get('next')
                if not next_page or not next_page.startswith('/'):
                    next_page = url_for('index')
                flash('Logged in successfully.', 'success')
                return redirect(next_page)
            
            flash('Invalid username or password.', 'error')
        
        return render_template('login.html')
    except Exception as e:
        print(f"Login error: {str(e)}")  # Log the error
        flash('An error occurred during login. Please try again.', 'error')
        return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('login'))

# Queue for SSE messages
message_queue = queue.Queue()

def load_stock_data():
    try:
        df = pd.read_excel('stocks.ods', engine='odf')
        
        # Convert numeric columns
        numeric_columns = ['Price', 'MarketCap', 'EPS', 'P/E', 'P/B']
        for col in numeric_columns:
            if col in df.columns:
                # Convert column to string first
                df[col] = df[col].astype(str)
                # Remove currency and percentage symbols, and commas
                df[col] = df[col].str.replace(',', '').str.replace('₫', '').str.replace('%', '')
                # Convert to numeric, invalid values become NaN
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        return df
    except Exception as e:
        print(f"Error loading data: {str(e)}")
        return None

def scrape_stocks_async(symbols, force_update=False):
    try:
        # Load existing data
        existing_df = None
        try:
            existing_df = pd.read_excel('stocks.ods', engine='odf')
        except:
            existing_df = pd.DataFrame(columns=['Symbol'])
        
        # If force_update is True, scrape all symbols, otherwise only new ones
        if force_update:
            new_symbols = symbols
            message = f'Updating data for {len(symbols)} stocks'
        else:
            # Filter out symbols that already have data
            existing_symbols = existing_df['Symbol'].tolist() if not existing_df.empty else []
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
        results = []
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
                results.append(result)
                
            except Exception as e:
                print(f"Error processing {symbol}: {str(e)}")
                results.append({
                    'Symbol': symbol,
                    'Error': str(e)
                })
        
        # Update or combine results
        if results:
            new_df = pd.DataFrame(results)
            if force_update:
                # For force update, replace existing data
                final_df = new_df
            else:
                # For normal scrape, combine with existing data
                if existing_df.empty:
                    final_df = new_df
                else:
                    final_df = pd.concat([existing_df, new_df], ignore_index=True)
            
            # Save results
            final_df.to_excel('stocks.ods', engine='odf', index=False)
        
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
    stocks = df['Symbol'].tolist() if df is not None else []
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

@app.route('/get_stocks')
def get_stocks():
    try:
        df = load_stock_data()
        if df is None:
            return jsonify({'error': 'Error loading stock data'})
        
        stocks = df['Symbol'].tolist()
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
        df = load_stock_data()
        if df is None or df.empty:
            return jsonify({'error': 'No stocks found to update'})
        
        symbols = df['Symbol'].tolist()
        
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
                    text=text_values,  # Show formatted values on bars
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
            height=300 * len(metrics),  # Adjust height based on number of metrics
            width=1000,
            showlegend=False,
            plot_bgcolor='white',
            title={
                'text': 'Stock Comparison Analysis',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 24}
            },
            margin=dict(t=100, b=50),  # Adjust margins
            bargap=0.2,
            paper_bgcolor='white'  # Set paper background color
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
        print(f"Error in export_pdf: {str(e)}")  # Add detailed error logging
        return jsonify({'error': str(e)}), 500  # Return 500 status code for server errors

if __name__ == '__main__':
    app.run(debug=True) 