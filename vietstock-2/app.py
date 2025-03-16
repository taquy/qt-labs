from flask import Flask, render_template, jsonify, request, Response
import pandas as pd
import plotly
import plotly.express as px
import json
from scrape import process_stock_list
import threading
import queue

app = Flask(__name__)

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

def scrape_stocks_async(symbols):
    try:
        # Load existing data
        existing_df = None
        try:
            existing_df = pd.read_excel('stocks.ods', engine='odf')
        except:
            existing_df = pd.DataFrame(columns=['Symbol'])
        
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
        
        total_stocks = len(new_symbols)
        message_queue.put(json.dumps({
            'status': 'info',
            'message': f'Found {total_stocks} new stocks to scrape'
        }))
        
        # Process new stocks one by one and send progress updates
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
        
        # Combine new results with existing data
        if results:
            new_df = pd.DataFrame(results)
            if existing_df.empty:
                final_df = new_df
            else:
                final_df = pd.concat([existing_df, new_df], ignore_index=True)
            
            # Save combined results
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
def stream():
    def event_stream():
        while True:
            try:
                # Get message from queue with timeout
                message = message_queue.get(timeout=1)
                yield f"data: {message}\n\n"
            except queue.Empty:
                # Send keepalive message
                yield f"data: {json.dumps({'status': 'keepalive'})}\n\n"
    
    return Response(event_stream(), mimetype='text/event-stream')

@app.route('/')
def index():
    df = load_stock_data()
    if df is None:
        return "Error loading stock data"
    
    metrics = ['Price', 'MarketCap', 'EPS', 'P/E', 'P/B']
    stocks = df['Symbol'].tolist()
    
    return render_template('index.html', metrics=metrics, stocks=stocks)

@app.route('/scrape_stocks', methods=['POST'])
def scrape_stocks():
    try:
        data = request.json
        symbols = data.get('symbols', [])
        
        if not symbols:
            return jsonify({'error': 'No stock symbols provided'})
        
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
def update_graph():
    df = load_stock_data()
    if df is None:
        return jsonify({'error': 'Error loading stock data'})
    
    data = request.json
    selected_stocks = data.get('stocks', [])
    selected_metric = data.get('metric', 'Price')
    
    if not selected_stocks:
        return jsonify({'error': 'No stocks selected'})
    
    # Filter data for selected stocks
    filtered_df = df[df['Symbol'].isin(selected_stocks)]
    
    # Sort by metric value for better visualization
    filtered_df = filtered_df.sort_values(by=selected_metric, ascending=True)
    
    # Create bar chart
    fig = px.bar(
        filtered_df,
        x='Symbol',
        y=selected_metric,
        title=f'Comparison of {selected_metric} across Selected Stocks',
        labels={'Symbol': 'Stock Symbol', selected_metric: selected_metric},
        template='plotly_white',
        color='Symbol',  # Add colors for each stock
        color_discrete_sequence=px.colors.qualitative.Set3  # Use a nice color palette
    )
    
    # Update layout
    fig.update_layout(
        showlegend=True,
        plot_bgcolor='white',
        height=500,
        title_x=0.5,  # Center the title
        title_font_size=20,
        bargap=0.2,  # Adjust space between bars
        # Configure animations
        transition_duration=800,
        transition={
            'duration': 800,
            'easing': 'cubic-in-out'
        },
        # Update axes
        xaxis=dict(
            title_font=dict(size=14),
            tickfont=dict(size=12),
            gridcolor='lightgray'
        ),
        yaxis=dict(
            title_font=dict(size=14),
            tickfont=dict(size=12),
            gridcolor='lightgray',
            # Add animation for axis range
            autorange=True,
            rangemode='normal'
        )
    )
    
    # Add hover template with formatted values
    if selected_metric in ['Price', 'MarketCap']:
        value_format = ",.0f"  # No decimals for these metrics
    else:
        value_format = ",.2f"  # 2 decimals for other metrics
    
    fig.update_traces(
        hovertemplate="<b>%{x}</b><br>" +
                     f"{selected_metric}: %{{y:{value_format}}}<br>" +
                     "<extra></extra>",  # Remove secondary box
        textposition='auto',  # Show values on bars
    )
    
    # Convert plot to JSON
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return jsonify(graphJSON)

if __name__ == '__main__':
    app.run(debug=True) 