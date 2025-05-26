import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def setup_driver():
    chrome_options = Options()
    user_profile = os.path.expanduser("~/ChromeProfiles/selenium")
    
    # Add options to persist session and prevent browser from closing
    chrome_options.add_argument(f"user-data-dir={user_profile}")
    chrome_options.add_argument("--no-first-run")
    chrome_options.add_argument("--no-default-browser-check")
    chrome_options.add_argument("--disable-popup-blocking")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_experimental_option("detach", True)  # Prevents browser from closing
    
    # Initialize the Chrome driver with the specified options
    driver = webdriver.Chrome(options=chrome_options)
    # Maximize window
    driver.maximize_window()
    return driver

# fill input text
def fill_input_text(driver, text, xpath):
    captcha_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, xpath))
    )
    captcha_input.clear()
    captcha_input.send_keys(text)
