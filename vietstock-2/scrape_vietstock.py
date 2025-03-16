from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException, NoSuchElementException
import time
import sys
import platform
import requests
import json
import csv
import pandas as pd
from datetime import datetime
import odf  # Required for reading ODS files

def create_driver():
    chrome_options = Options()
    chrome_options.add_argument('--headless=new')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    chrome_options.add_argument('--window-size=1920,1080')
    
    try:
        service = Service()
        driver = webdriver.Chrome(service=service, options=chrome_options)
        return driver
    except Exception as e:
        print(f"Failed to create Chrome driver: {str(e)}")
        sys.exit(1)

def get_stock_url(driver, stock_symbol):
    try:
        # Use the search API to get stock details
        search_url = f"https://search.cafef.vn/api/searching/v1/Companies/SearchByKeyWord?keyword={stock_symbol}"
        print(f"Searching for stock: {stock_symbol}")
        
        # Make API request
        response = requests.get(search_url)
        data = json.loads(response.text)
        
        # Get the redirectUrl from the first document
        if data and isinstance(data, dict) and 'value' in data:
            value = data['value']
            redirect_url = value['documents'][0]['document']['redirectUrl']
            if redirect_url:
                stock_url = f"https://cafef.vn{redirect_url}"
                # Verify the URL works
                driver.get(stock_url)
                wait = WebDriverWait(driver, 10)
                wait.until(EC.presence_of_element_located((By.CLASS_NAME, "dltl-other")))
                
                return stock_url
        
        raise Exception(f"Stock symbol {stock_symbol} not found in search results")
                
    except Exception as e:
        print(f"Error finding stock URL: {str(e)}")
        return None

def scrape_stock_data(stock_symbol):
    driver = create_driver()
    metrics_map = {}
    
    try:
        # Get the stock details URL
        stock_url = get_stock_url(driver, stock_symbol)
        if not stock_url:
            raise Exception(f"Could not find URL for stock symbol {stock_symbol}")
            
        # Give the page a moment to load dynamic content
        time.sleep(2)
        
        # Find all elements with class dlt-left-half
        metrics_elements = driver.find_elements(By.CLASS_NAME, "dlt-left-half")
        if len(metrics_elements) == 0:
            # Print all classes in the page for debugging
            all_elements = driver.find_elements(By.CSS_SELECTOR, "*")
            classes_found = set()
            for elem in all_elements:
                try:
                    class_name = elem.get_attribute("class")
                    if class_name:
                        classes_found.add(class_name)
                except:
                    continue
            for class_name in sorted(classes_found):
                print(f"Class found: {class_name}")
        
        # Process each element to find metrics
        for i, element in enumerate(metrics_elements):
            text = element.text.strip()
            lines = text.split('\n')
            # Process pairs of lines (key, value)
            for j in range(0, len(lines), 2):
                if j + 1 < len(lines):  # Make sure we have both key and value
                    key = lines[j].strip()
                    value = lines[j + 1].strip()
                    # Store metrics we're interested in
                    if "EPS" in key:
                        metrics_map['EPS'] = value
                    elif "P/E" in key:
                        metrics_map['P/E'] = value
                    elif "P/B" in key:
                        metrics_map['P/B'] = value
            
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        
    finally:
        driver.quit()
        
    return metrics_map

def process_stock_list(stock_symbols):
    results = []
    driver = create_driver()
    
    try:
        for symbol in stock_symbols:
            try:
                print(f"\nProcessing stock symbol: {symbol}")
                metrics = scrape_stock_data_with_driver(driver, symbol)
                metrics['Symbol'] = symbol
                metrics['Timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                results.append(metrics)
                
                # Add a delay between requests to be respectful to the server
                time.sleep(2)
                
            except Exception as e:
                print(f"Error processing symbol {symbol}: {str(e)}")
                results.append({
                    'Symbol': symbol,
                    'Error': str(e),
                    'Timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                })
                
    finally:
        driver.quit()
        
    return results

def scrape_stock_data_with_driver(driver, stock_symbol):
    metrics_map = {}
    
    try:
        # Get the stock details URL
        stock_url = get_stock_url(driver, stock_symbol)
        if not stock_url:
            raise Exception(f"Could not find URL for stock symbol {stock_symbol}")
            
        # Give the page a moment to load dynamic content
        time.sleep(2)
        
        # Get the stock price
        try:
            price_element = driver.find_element(By.ID, 'price__0')
            if price_element:
                metrics_map['Price'] = price_element.text.strip()
        except NoSuchElementException:
            print(f"Could not find price element for {stock_symbol}")
            metrics_map['Price'] = ''
            
        # Get the market cap
        try:
            dltl_other_elements = driver.find_elements(By.CLASS_NAME, 'dltl-other')
            if len(dltl_other_elements) >= 3:  # Make sure we have at least 3 elements
                market_cap_element = dltl_other_elements[2]  # Get the 3rd element (index 2)
                clearfix_elements = market_cap_element.find_elements(By.CLASS_NAME, 'clearfix')
                print(clearfix_elements)
                if len(clearfix_elements) >= 4:  # Make sure we have at least 4 clearfix elements
                    clearfix_element = clearfix_elements[3]  # Get the 4th element (index 3)
                    value_element = clearfix_element.find_element(By.CLASS_NAME, 'r')
                    if value_element:
                        metrics_map['MarketCap'] = value_element.text.strip()
        except NoSuchElementException:
            print(f"Could not find market cap element for {stock_symbol}")
            metrics_map['MarketCap'] = ''
        
        # Find all elements with class dlt-left-half
        metrics_elements = driver.find_elements(By.CLASS_NAME, "dlt-left-half")
        
        # Process each element to find metrics
        for element in metrics_elements:
            text = element.text.strip()
            lines = text.split('\n')
            # Process pairs of lines (key, value)
            for j in range(0, len(lines), 2):
                if j + 1 < len(lines):  # Make sure we have both key and value
                    key = lines[j].strip()
                    value = lines[j + 1].strip()
                    # Store metrics we're interested in
                    if "EPS" in key:
                        metrics_map['EPS'] = value
                    elif "P/E" in key:
                        metrics_map['P/E'] = value
                    elif "P/B" in key:
                        metrics_map['P/B'] = value
            
    except Exception as e:
        print(f"An error occurred while scraping {stock_symbol}: {str(e)}")
        raise
        
    return metrics_map

if __name__ == "__main__":
    print(f"Running on: {platform.system()} {platform.release()}")
    
    # Read stock symbols from ODS file
    try:
        # Read existing ODS file
        df = pd.read_excel('stocks.ods', engine='odf', header=None)
        
        # Ensure we have enough columns (at least 8 columns: Symbol, Price, MarketCap, EPS, P/E, P/B, Timestamp, Error)
        required_columns = 8
        current_columns = len(df.columns)
        if current_columns < required_columns:
            # Add missing columns
            for i in range(current_columns, required_columns):
                df[i] = ''
        
        stock_symbols = df.iloc[1:, 0].dropna().tolist()  # Get first column starting from second row, remove empty values
        
        if not stock_symbols:
            print("No stock symbols found in the ODS file.")
            sys.exit(1)
            
        print(f"Found {len(stock_symbols)} stock symbols to process")
        
        # Process all stocks
        results = process_stock_list(stock_symbols)
        
        # Convert results to DataFrame
        df_results = pd.DataFrame(results)
        
        # Update the original ODS file
        # Set headers for the metrics columns
        df.iloc[0, 0] = 'Symbol'     # Column A
        df.iloc[0, 1] = 'Price'      # Column B
        df.iloc[0, 2] = 'MarketCap'  # Column C
        df.iloc[0, 3] = 'EPS'        # Column D
        df.iloc[0, 4] = 'P/E'        # Column E
        df.iloc[0, 5] = 'P/B'        # Column F
        df.iloc[0, 6] = 'Timestamp'  # Column G
        df.iloc[0, 7] = 'Error'      # Column H
        
        # Update data for each stock
        for index, row in df_results.iterrows():
            # Find the corresponding row in original DataFrame
            matching_rows = df[df.iloc[:, 0] == row['Symbol']].index
            if len(matching_rows) > 0:
                df_index = matching_rows[0]
                
                # Update the metrics
                df.iloc[df_index, 1] = row.get('Price', '')
                df.iloc[df_index, 2] = row.get('MarketCap', '')
                df.iloc[df_index, 3] = row.get('EPS', '')
                df.iloc[df_index, 4] = row.get('P/E', '')
                df.iloc[df_index, 5] = row.get('P/B', '')
                df.iloc[df_index, 6] = row.get('Timestamp', '')
                df.iloc[df_index, 7] = row.get('Error', '')
        
        # Save back to the ODS file
        df.to_excel('stocks.ods', engine='odf', index=False, header=False)
        print("\nUpdated stocks.ods with the new metrics")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1) 