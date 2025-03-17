from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import requests
import json
import time
from datetime import datetime
from extensions import db
from models import Stock, StockStats

def create_driver():
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=chrome_options)

def get_stock_url(symbol):
    try:
        return f"https://s.cafef.vn/Lich-su-giao-dich-{symbol}-1.chn"
    except Exception as e:
        print(f"Error getting stock URL for {symbol}: {str(e)}")
        return None

def scrape_stock_data(driver, url):
    try:
        driver.get(url)
        time.sleep(2)  # Wait for page to load
        
        # Wait for the price element to be present
        price_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#stockprice"))
        )
        
        # Get other elements
        market_cap_element = driver.find_element(By.CSS_SELECTOR, "#CafeF_ThongKeGiaoDich_VonHoa")
        eps_element = driver.find_element(By.CSS_SELECTOR, "#CafeF_ThongKeGiaoDich_EPS")
        pe_element = driver.find_element(By.CSS_SELECTOR, "#CafeF_ThongKeGiaoDich_PE")
        pb_element = driver.find_element(By.CSS_SELECTOR, "#CafeF_ThongKeGiaoDich_PB")
        
        # Extract values and handle potential formatting issues
        def clean_number(text):
            # Remove any non-numeric characters except dots and commas
            cleaned = ''.join(c for c in text if c.isdigit() or c in '.,')
            # Replace comma with dot for decimal point
            cleaned = cleaned.replace(',', '.')
            # Convert to float
            return float(cleaned)
        
        try:
            price = clean_number(price_element.text)
            market_cap = clean_number(market_cap_element.text)
            eps = clean_number(eps_element.text)
            pe = clean_number(pe_element.text)
            pb = clean_number(pb_element.text)
        except ValueError as e:
            print(f"Error converting values: {str(e)}")
            return None
        
        return {
            'price': price,
            'market_cap': market_cap,
            'eps': eps,
            'pe_ratio': pe,
            'pb_ratio': pb
        }
    except Exception as e:
        print(f"Error scraping data: {str(e)}")
        return None

def process_stock_list(symbols):
    driver = None
    try:
        driver = create_driver()
        results = []
        
        for symbol in symbols:
            try:
                url = get_stock_url(symbol)
                if not url:
                    print(f"Could not find URL for {symbol}")
                    continue
                    
                data = scrape_stock_data(driver, url)
                if data:
                    data['Symbol'] = symbol
                    results.append(data)
                    
                    # Update or create StockStats record
                    stock = Stock.query.filter_by(symbol=symbol).first()
                    if stock:
                        stats = StockStats.query.filter_by(stock_id=stock.id).first()
                        if stats:
                            stats.price = data['price']
                            stats.market_cap = data['market_cap']
                            stats.eps = data['eps']
                            stats.pe_ratio = data['pe_ratio']
                            stats.pb_ratio = data['pb_ratio']
                            stats.created_at = datetime.utcnow()
                        else:
                            stats = StockStats(
                                stock_id=stock.id,
                                price=data['price'],
                                market_cap=data['market_cap'],
                                eps=data['eps'],
                                pe_ratio=data['pe_ratio'],
                                pb_ratio=data['pb_ratio']
                            )
                            db.session.add(stats)
                        db.session.commit()
                    print(f"Successfully processed {symbol}")
            except Exception as e:
                print(f"Error processing stock {symbol}: {str(e)}")
                continue
                
        return results
    except Exception as e:
        print(f"Error in process_stock_list: {str(e)}")
        return []
    finally:
        if driver:
            driver.quit()
        