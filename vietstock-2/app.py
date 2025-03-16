from flask import Flask, render_template, jsonify, request
import pandas as pd
import plotly
import plotly.express as px
import json

app = Flask(__name__)

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

@app.route('/')
def index():
    df = load_stock_data()
    if df is None:
        return "Error loading stock data"
    
    metrics = ['Price', 'MarketCap', 'EPS', 'P/E', 'P/B']
    stocks = df['Symbol'].tolist()
    
    return render_template('index.html', metrics=metrics, stocks=stocks)

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
    
    # Create bar chart
    fig = px.bar(
        filtered_df,
        x='Symbol',
        y=selected_metric,
        title=f'Comparison of {selected_metric} across Selected Stocks',
        labels={'Symbol': 'Stock Symbol', selected_metric: selected_metric},
        template='plotly_white'
    )
    
    # Update layout
    fig.update_layout(
        showlegend=False,
        plot_bgcolor='white',
        height=500
    )
    
    # Convert plot to JSON
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return jsonify(graphJSON)

if __name__ == '__main__':
    app.run(debug=True) 