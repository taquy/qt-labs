import requests
import json
import pandas as pd
import odf
from datetime import datetime
from models import Stock, db
def get_stock_list():
    url = 'https://scanner.tradingview.com/vietnam/scan?label-product=markets-screener'
    
    headers = {
        'accept': 'application/json',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36'
    }
    
    data = {
        "columns": [
            "name", "description", "logoid", "update_mode", "type"
        ],
        "ignore_unknown_fields": False,
        "options": {"lang": "vi"},
        "range": [0, 2000],
        "sort": {"sortBy": "name", "sortOrder": "desc"},
        "preset": "all_stocks"
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        # Parse the JSON response
        result = response.json()
        
        # Extract stock data from the response
        if 'data' in result:
            stocks_data = []
            for item in result['data']:
                d = item['d']
                # Only include regular stocks (exclude ETFs and funds)
                if d[4] == 'stock':
                    stock_info = {
                        'symbol': d[0],
                        'name': d[1],
                        'icon': f'https://s3-symbol-logo.tradingview.com/{d[2]}.svg',
                        'exchange': item['s'].split(':')[0]
                    }
                    stocks_data.append(stock_info)
            return stocks_data
        else:
            print("No data found in response")
            return []
            
    except requests.exceptions.RequestException as e:
        print(f"Error making request: {e}")
        return []
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON response: {e}")
        return []

def save_to_database(stocks_data):
    try:
        # Process each stock
        for stock_info in stocks_data:
            # Check if stock already exists
            stock = Stock.query.filter_by(symbol=stock_info['symbol']).first()
            if stock:
                # Update existing stock
                stock.name = stock_info['name']
                stock.last_updated = datetime.now()
            else:
                # Create new stock
                stock = Stock(
                    symbol=stock_info['symbol'],
                    name=stock_info['name'],
                    icon=stock_info['icon'],
                    exchange=stock_info['exchange'],
                    last_updated=datetime.now()
                )
                db.session.add(stock)
            
        # Commit all changes
        db.session.commit()
        print(f"Successfully saved {len(stocks_data)} stocks to database")
        return True
            
    except Exception as e:
        print(f"Error saving to database: {e}")
        if 'db' in locals():
            db.session.rollback()
        return False

def pull_stock_list():
    # Get the stock list
    stocks_data = get_stock_list()
    
    error = False
    if stocks_data:
        message = f"Found {len(stocks_data)} stocks"
        # Save to database
        save_to_database(stocks_data)
    else:   
        message = "No stocks data to save"
        error = True
    return message, error
