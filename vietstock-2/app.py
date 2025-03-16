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