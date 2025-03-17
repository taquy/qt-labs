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
from models import Stock, StockStats
from extensions import db
from bs4 import BeautifulSoup

def create_driver():
    """Create and configure a Chrome WebDriver instance."""
    try:
        chrome_options = Options()
        chrome_options.add_argument('--headless')  # Run in headless mode
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        
        driver = webdriver.Chrome(options=chrome_options)
        return driver
    except Exception as e:
        print(f"Error creating WebDriver: {str(e)}")
        sys.exit(1)

def get_stock_url(stock_symbol):
    """Get the stock details URL using CafeF search API."""
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
            if value and 'documents' in value and len(value['documents']) > 0:
                redirect_url = value['documents'][0]['document']['redirectUrl']
                if redirect_url:
                    return f"https://cafef.vn{redirect_url}"
        
        raise Exception(f"Stock symbol {stock_symbol} not found in search results")
        
    except Exception as e:
        print(f"Error finding stock URL: {str(e)}")
        return None

def clean_number(value):
    """Clean and convert a string number to float."""
    if not value:
        return None
    # Keep only digits, dots, and commas
    cleaned = ''.join(c for c in value if c.isdigit() or c in '.,')
    # Convert comma decimal separator to dot
    cleaned = cleaned.replace(',', '.')
    try:
        return float(cleaned)
    except ValueError:
        return None

def scrape_stock_data(url):
    """Scrape stock data from the given URL."""
    try:
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Failed to fetch URL {url}: Status code {response.status_code}")
            return None
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract data using CSS selectors
        price_element = soup.select_one('#stockprice')
        market_cap_element = soup.select_one('#CafeF_ThongKeGiaoDich_VonHoa')
        eps_element = soup.select_one('#CafeF_ThongKeGiaoDich_EPS')
        pe_element = soup.select_one('#CafeF_ThongKeGiaoDich_PE')
        pb_element = soup.select_one('#CafeF_ThongKeGiaoDich_PB')
        
        # Clean and convert the values
        data = {
            'price': clean_number(price_element.text if price_element else None),
            'market_cap': clean_number(market_cap_element.text if market_cap_element else None),
            'eps': clean_number(eps_element.text if eps_element else None),
            'pe': clean_number(pe_element.text if pe_element else None),
            'pb': clean_number(pb_element.text if pb_element else None)
        }
        
        return data
        
    except Exception as e:
        print(f"Error scraping data: {str(e)}")
        return None

def process_stock_list(symbols):
    """Process a list of stock symbols and update their data in the database."""
    driver = create_driver()
    
    try:
        for symbol in symbols:
            try:
                print(f"\nProcessing stock symbol: {symbol}")
                metrics = scrape_stock_data_with_driver(driver, symbol)
                if not metrics:
                    print(f"No metrics found for {symbol}")
                    continue

                # Find the stock in database
                stock = Stock.query.filter_by(symbol=symbol).first()
                if not stock:
                    print(f"Stock {symbol} not found in database")
                    continue

                # Find or create StockStats for this stock
                stats = StockStats.query.filter_by(stock_id=stock.id).first()
                if not stats:
                    stats = StockStats(stock_id=stock.id)
                    db.session.add(stats)

                # Convert and update metrics
                try:
                    # Remove any spaces and commas from numbers
                    price_str = metrics.get('Price', '').replace(',', '').replace(' ', '')
                    market_cap_str = metrics.get('MarketCap', '').replace(',', '').replace(' ', '')
                    eps_str = metrics.get('EPS', '').replace(',', '').replace(' ', '')
                    pe_str = metrics.get('P/E', '').replace(',', '').replace(' ', '')
                    pb_str = metrics.get('P/B', '').replace(',', '').replace(' ', '')

                    # Convert to float, handling empty strings
                    stats.price = float(price_str) if price_str else None
                    stats.market_cap = float(market_cap_str) if market_cap_str else None
                    stats.eps = float(eps_str) if eps_str else None
                    stats.pe = float(pe_str) if pe_str else None
                    stats.pb = float(pb_str) if pb_str else None
                    stats.last_updated = datetime.utcnow()

                    # Commit the changes
                    db.session.commit()
                    print(f"Successfully updated metrics for {symbol}:")
                    print(f"  Price: {stats.price}")
                    print(f"  Market Cap: {stats.market_cap}")
                    print(f"  EPS: {stats.eps}")
                    print(f"  P/E: {stats.pe}")
                    print(f"  P/B: {stats.pb}")

                except ValueError as ve:
                    print(f"Error converting metrics for {symbol}: {str(ve)}")
                    db.session.rollback()
                    continue

                # Add a delay between requests
                time.sleep(2)

            except Exception as e:
                print(f"Error processing stock {symbol}: {str(e)}")
                db.session.rollback()
                continue

    except Exception as e:
        print(f"Error in process_stock_list: {str(e)}")
        db.session.rollback()
        raise
    finally:
        driver.quit()

def scrape_stock_data_with_driver(driver, stock_symbol):
    """Scrape stock data using Selenium WebDriver."""
    try:
        # Get the stock details URL
        stock_url = get_stock_url(stock_symbol)
        if not stock_url:
            raise Exception(f"Could not find URL for stock symbol {stock_symbol}")
            
        print(f"Navigating to URL: {stock_url}")
        driver.get(stock_url)
        
        # Wait for the main content to load
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "dltl-other")))
        
        # Extract metrics
        metrics_map = {}
        
        # Price
        try:
            price_element = driver.find_element(By.CSS_SELECTOR, ".r_time .price")
            metrics_map['Price'] = price_element.text.strip()
        except:
            print("Could not find price element")
        
        # Market Cap
        try:
            market_cap_element = driver.find_element(By.CSS_SELECTOR, ".dltl-other tr:nth-child(1) td:nth-child(2)")
            metrics_map['MarketCap'] = market_cap_element.text.strip()
        except:
            print("Could not find market cap element")
        
        # EPS
        try:
            eps_element = driver.find_element(By.CSS_SELECTOR, ".dltl-other tr:nth-child(2) td:nth-child(2)")
            metrics_map['EPS'] = eps_element.text.strip()
        except:
            print("Could not find EPS element")
        
        # P/E
        try:
            pe_element = driver.find_element(By.CSS_SELECTOR, ".dltl-other tr:nth-child(3) td:nth-child(2)")
            metrics_map['P/E'] = pe_element.text.strip()
        except:
            print("Could not find P/E element")
        
        # P/B
        try:
            pb_element = driver.find_element(By.CSS_SELECTOR, ".dltl-other tr:nth-child(4) td:nth-child(2)")
            metrics_map['P/B'] = pb_element.text.strip()
        except:
            print("Could not find P/B element")
        
        return metrics_map
        
    except Exception as e:
        print(f"Error scraping data for {stock_symbol}: {str(e)}")
        return None
        