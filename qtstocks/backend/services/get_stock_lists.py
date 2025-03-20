import requests
import json
import pandas as pd
import odf
from datetime import datetime

def get_stock_list():
    url = 'https://scanner.tradingview.com/global/scan?label-product=symbols-components'
    
    headers = {
        'accept': 'application/json',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36'
    }
    
    data = {
        "columns": [
            "name", "description", "logoid", "update_mode", "type", "typespecs",
            "market_cap_basic", "fundamental_currency_code", "close", "pricescale",
            "minmov", "fractional", "minmove2", "currency", "change", "volume",
            "relative_volume_10d_calc", "price_earnings_ttm", "earnings_per_share_diluted_ttm",
            "earnings_per_share_diluted_yoy_growth_ttm", "dividends_yield_current",
            "sector.tr", "market", "sector", "recommendation_mark"
        ],
        "ignore_unknown_fields": False,
        "options": {"lang": "en"},
        "range": [0, 1000],
        "sort": {"sortBy": "name", "sortOrder": "desc"},
        "symbols": {"symbolset": ["SYML:HOSE;VNINDEX"]},
        "preset": "index_components_market_pages"
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
                        'Symbol': d[0],
                        'Name': d[1],
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
        from app import app, db
        from models import Stock
        from datetime import datetime
        
        with app.app_context():
            # Process each stock
            for stock_info in stocks_data:
                # Check if stock already exists
                stock = Stock.query.filter_by(symbol=stock_info['Symbol']).first()
                
                if stock:
                    # Update existing stock
                    stock.name = stock_info['Name']
                    stock.last_updated = datetime.strptime(stock_info['Last Updated'], '%Y-%m-%d %H:%M:%S')
                else:
                    # Create new stock
                    stock = Stock(
                        symbol=stock_info['Symbol'],
                        name=stock_info['Name'],
                        last_updated=datetime.strptime(stock_info['Last Updated'], '%Y-%m-%d %H:%M:%S')
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
