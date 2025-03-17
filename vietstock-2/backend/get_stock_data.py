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
from datetime import datetime
from models import db, Stock, StockStats
from app import app

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

def process_stock_list(stock_symbols):
    results = []
    driver = create_driver()
    
    try:
        with app.app_context():
            for symbol in stock_symbols:
                try:
                    print(f"\nProcessing stock symbol: {symbol}")
                    metrics = scrape_stock_data_with_driver(driver, symbol)
                    
                    # Convert string values to float, handling empty strings and invalid values
                    price = float(metrics.get('Price', '').replace(',', '')) if metrics.get('Price') else None
                    market_cap = float(metrics.get('MarketCap', '').replace(',', '')) if metrics.get('MarketCap') else None
                    eps = float(metrics.get('EPS', '').replace(',', '')) if metrics.get('EPS') else None
                    pe_ratio = float(metrics.get('P/E', '').replace(',', '')) if metrics.get('P/E') else None
                    pb_ratio = float(metrics.get('P/B', '').replace(',', '')) if metrics.get('P/B') else None
                    
                    # Check if stock exists in Stock table
                    stock = Stock.query.filter_by(symbol=symbol).first()
                    if not stock:
                        print(f"Stock {symbol} not found in database")
                        continue
                    
                    # Update or create StockStats
                    stock_stats = StockStats.query.filter_by(symbol=symbol).first()
                    if stock_stats:
                        # Update existing record
                        stock_stats.price = price
                        stock_stats.market_cap = market_cap
                        stock_stats.eps = eps
                        stock_stats.pe_ratio = pe_ratio
                        stock_stats.pb_ratio = pb_ratio
                        stock_stats.last_updated = datetime.utcnow()
                    else:
                        # Create new record
                        stock_stats = StockStats(
                            symbol=symbol,
                            price=price,
                            market_cap=market_cap,
                            eps=eps,
                            pe_ratio=pe_ratio,
                            pb_ratio=pb_ratio,
                            last_updated=datetime.utcnow()
                        )
                        db.session.add(stock_stats)
                    
                    # Commit changes
                    db.session.commit()
                    print(f"Successfully updated stats for {symbol}")
                    
                    # Add a delay between requests
                    time.sleep(2)
                    
                except Exception as e:
                    print(f"Error processing symbol {symbol}: {str(e)}")
                    db.session.rollback()
                    
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
        