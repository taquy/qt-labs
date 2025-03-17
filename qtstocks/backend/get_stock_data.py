from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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
    return webdriver.Chrome(options=chrome_options)

def get_stock_url(symbol):
    search_url = f"https://www.vietstock.vn/api/search/search?keyword={symbol}"
    response = requests.get(search_url)
    data = response.json()
    
    if data and len(data) > 0:
        stock_data = data[0]
        if stock_data.get('Code') == symbol:
            return f"https://www.vietstock.vn/stock/{stock_data['Code']}.htm"
    return None

def scrape_stock_data(driver, url):
    try:
        driver.get(url)
        time.sleep(2)  # Wait for page to load
        
        # Wait for the price element to be present
        price_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "span.price"))
        )
        
        # Get other elements
        market_cap_element = driver.find_element(By.CSS_SELECTOR, "span.market-cap")
        eps_element = driver.find_element(By.CSS_SELECTOR, "span.eps")
        pe_element = driver.find_element(By.CSS_SELECTOR, "span.pe")
        pb_element = driver.find_element(By.CSS_SELECTOR, "span.pb")
        
        # Extract values
        price = float(price_element.text.replace(',', ''))
        market_cap = float(market_cap_element.text.replace(',', ''))
        eps = float(eps_element.text.replace(',', ''))
        pe = float(pe_element.text.replace(',', ''))
        pb = float(pb_element.text.replace(',', ''))
        
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
    driver = create_driver()
    results = []
    
    try:
        for symbol in symbols:
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
                
    finally:
        driver.quit()
    
    return results
        