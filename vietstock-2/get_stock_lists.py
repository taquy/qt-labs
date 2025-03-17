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
                        'Type': d[4],
                        'Market Cap (USD)': d[6],
                        'Last Price': d[8],
                        'Currency': d[13],
                        'Change %': d[14] * 100 if d[14] is not None else None,
                        'Volume': d[15],
                        'P/E Ratio': d[17],
                        'EPS': d[18],
                        'EPS Growth %': d[19] * 100 if d[19] is not None else None,
                        'Dividend Yield %': d[20] * 100 if d[20] is not None else None,
                        'Sector': d[21],
                        'Last Updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
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

def save_to_ods(stocks_data):
    try:
        # Create DataFrame from stocks data
        new_df = pd.DataFrame(stocks_data)
        
        try:
            # Try to read existing file
            with pd.ExcelFile('stocks.ods', engine='odf') as xls:
                # Read all existing sheets
                sheets = {}
                for sheet_name in xls.sheet_names:
                    if sheet_name != 'Available Stocks':  # Skip the sheet we're going to update
                        sheets[sheet_name] = pd.read_excel(xls, sheet_name=sheet_name, engine='odf')
        except FileNotFoundError:
            sheets = {}
        
        # Create a new Excel writer
        with pd.ExcelWriter('stocks.ods', engine='odf') as writer:
            # Write all existing sheets except 'Available Stocks'
            for sheet_name, df in sheets.items():
                df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            # Write the new 'Available Stocks' sheet
            new_df.to_excel(writer, sheet_name='Available Stocks', index=False)
        
        print(f"Successfully saved {len(stocks_data)} stocks to stocks.ods")
        return True
    except Exception as e:
        print(f"Error saving to ODS file: {e}")
        return False

if __name__ == "__main__":
    # Get the stock list
    stocks_data = get_stock_list()
    
    if stocks_data:
        print(f"Found {len(stocks_data)} stocks")
        # Save to ODS file
        save_to_ods(stocks_data)
    else:
        print("No stocks data to save")
