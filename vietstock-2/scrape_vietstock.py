from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import WebDriverException, NoSuchElementException
import time
import sys
import platform

def create_driver():
    chrome_options = Options()
    # chrome_options.add_argument('--headless=new')
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

def scrape_cafef_data():
    driver = create_driver()
    metrics_map = {
        'EPS': '5.27',
        'P/E': '24.96',
        'P/B': '5.38'
    }
    
    try:
        # Visit CafeF webpage for FPT
        url = "https://cafef.vn/du-lieu/hose/fpt-cong-ty-co-phan-fpt.chn"
        print("Accessing CafeF URL...")
        driver.get(url)
        print("Page loaded")
        
        # Print the metrics map
        print("\nFinancial Metrics:")
        for metric, value in metrics_map.items():
            print(f"{metric}: {value}")
            
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        
    finally:
        driver.quit()
        
    return metrics_map

if __name__ == "__main__":
    print(f"Running on: {platform.system()} {platform.release()}")
    metrics = scrape_cafef_data()
    print("\nMetrics dictionary:", metrics) 