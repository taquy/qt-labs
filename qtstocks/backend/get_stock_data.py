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

class StockDataScraper:
    def __init__(self):
        self.driver = None

    def create_driver(self):
        """Create and configure a Chrome WebDriver instance."""
        try:
            chrome_options = Options()
            chrome_options.add_argument('--headless')  # Run in headless mode
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            
            self.driver = webdriver.Chrome(options=chrome_options)
            return self.driver
        except Exception as e:
            print(f"Error creating WebDriver: {str(e)}")
            sys.exit(1)

    def get_stock_url(self, stock_symbol):
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

    def scrape_stock_data_with_driver(self, stock_symbol):
        metrics_map = {}
        try:
            # Get the stock details URL
            stock_url = self.get_stock_url(stock_symbol)
            if not stock_url:
                raise Exception(f"Could not find URL for stock symbol {stock_symbol}")
                
            # Give the page a moment to load dynamic content
            time.sleep(2)
            
            # Get the stock price
            try:
                price_element = self.driver.find_element(By.ID, 'price__0')
                if price_element:
                    metrics_map['Price'] = price_element.text.strip()
            except NoSuchElementException:
                print(f"Could not find price element for {stock_symbol}")
                metrics_map['Price'] = ''
                
            # Get the market cap
            try:
                dltl_other_elements = self.driver.find_elements(By.CLASS_NAME, 'dltl-other')
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
            metrics_elements = self.driver.find_elements(By.CLASS_NAME, "dlt-left-half")
            
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
    

    def clean_number(self, value):
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

    def process_stock_list(self, symbols):
        """Process a list of stock symbols and update their data in the database."""
        self.driver = self.create_driver()
        
        try:
            for symbol in symbols:
                try:
                    print(f"\nProcessing stock symbol: {symbol}")
                    metrics = self.scrape_stock_data_with_driver(symbol)
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
                        stats.price = self.clean_number(price_str)
                        stats.market_cap = self.clean_number(market_cap_str)
                        stats.eps = self.clean_number(eps_str)
                        stats.pe = self.clean_number(pe_str)
                        stats.pb = self.clean_number(pb_str)
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
            if self.driver:
                self.driver.quit()

# Create a singleton instance
scraper = StockDataScraper()

# Function to be called from app.py
def process_stock_list(symbols):
    """Wrapper function to maintain backward compatibility."""
    return scraper.process_stock_list(symbols)
