from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import time
from datetime import datetime
from PIL import Image
import io
import hashlib
from show_image import show_image_and_prompt
from read_card import read_card_and_save_to_file
import shutil
from chrome_driver import setup_driver, fill_input_text

CARD_DIR = "cards"



def get_image_hash(img):
    # Convert image to bytes and calculate hash
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()
    return hashlib.md5(img_byte_arr).hexdigest()

def get_scaled_coordinates(driver, element):
    """Get coordinates adjusted for screen scaling"""
    # Get device pixel ratio
    pixel_ratio = driver.execute_script("return window.devicePixelRatio;")
    
    # Get element location and size
    location = element.location
    size = element.size
    
    # Calculate scaled coordinates
    x = location['x'] * pixel_ratio
    y = location['y'] * pixel_ratio
    width = size['width'] * pixel_ratio
    height = size['height'] * pixel_ratio
    
    return x, y, width, height

def wait_for_image_stability(driver, max_attempts=3, stability_time=1):
    """Wait for the image to be stable (not changing) for a period of time"""
    last_hash = None
    stable_count = 0
    
    for _ in range(max_attempts):
        try:
            # Scroll to top of the page
            driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(0.5)  # Wait for scroll to complete
            
            # Wait for the element to be visible
            captcha_element = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.CLASS_NAME, "form-capcha__images"))
            )
            
            # Get scaled coordinates
            x, y, width, height = get_scaled_coordinates(driver, captcha_element)
            
            # Take screenshot
            driver.save_screenshot("temp_screenshot.png")
            img = Image.open("temp_screenshot.png")
            
            # Crop to captcha with scaled coordinates
            left = max(0, int(x))
            top = max(0, int(y))
            right = int(x + width)
            bottom = int(y + height)
            
            # Add small padding
            padding = 2
            left = max(0, left - padding)
            top = max(0, top - padding)
            right = right + padding
            bottom = bottom + padding
            
            img = img.crop((left, top, right, bottom))
            
            # Get current hash
            current_hash = get_image_hash(img)
            
            # Check if image is stable
            if current_hash == last_hash:
                stable_count += 1
                if stable_count >= stability_time:
                    os.remove("temp_screenshot.png")
                    return img
            else:
                stable_count = 0
                last_hash = current_hash
            
            os.remove("temp_screenshot.png")
            time.sleep(0.5)  # Wait before next check
            
        except Exception as e:
            print(f"Error waiting for image stability: {e}")
            if os.path.exists("temp_screenshot.png"):
                os.remove("temp_screenshot.png")
            time.sleep(0.5)
    
    return None

def save_captcha_image(driver):
    image = wait_for_image_stability(driver)
    print(image)
    # captcha_text = show_image_and_prompt(filename)
    return ""

# def mobile_top_up(card_image_path, last_hash):
#     fill_input_text(driver, card_code, "//input[@placeholder='Nhập mã thẻ*']")
    
#     print("Starting to monitor for new captcha images...")
#     while True:
#         captcha_text, new_hash = save_captcha_image(driver, last_hash)
#         last_hash = new_hash
#         print(f"Hash: {new_hash}")
#         if captcha_text:
#             time.sleep(0.5)  # Add delay to ensure window has time to process
#             fill_input_text(driver, captcha_text, "//input[@placeholder='Nhập mã bảo mật*']")
#             print("New captcha image detected and saved")
            
#             # Click the "Nạp tiền" button
#             driver.find_element("css selector", "div.payment-online__btn-2column a.button.button--primary").click()
#             print("✅ Clicked on 'Nạp tiền' button")
            
#             # Wait for the API response with status 200
#             WebDriverWait(driver, 30).until(
#             lambda d: d.execute_script("""
#                     return window.performance.getEntries().some(entry => 
#                         entry.name.includes('/api/thanh-toan-online-v2') && 
#                         entry.responseStatus === 200
#                     );
#                 """)
#             )
#             print("✅ API request completed successfully with status 200")
            
            
#             # Remove jQuery modal blocker if present
#             try:
#                 driver.execute_script("""
#                     var modals = document.querySelectorAll('div.jquery-modal.blocker.current');
#                     modals.forEach(function(modal) {
#                         modal.remove();
#                     });
#                 """)
#                 print("✅ Removed jQuery modal blockers")
#             except Exception as e:
#                 print(f"❌ Error removing modal blockers: {e}")
                
#             time.sleep(2)
#             return True, last_hash
#         time.sleep(1)
    
def visit_page(callback_function):
    try:
        driver = setup_driver()
        driver.get("https://vietteltelecom.vn/nap-the")
        callback_function(driver)
        # while True:
        #     completed, last_hash = callback_function(driver)
        #     if completed:
        #         break
        #     time.sleep(1)  # Wait for 1 second before retrying
        # if completed:
        #     # Make sure the destination directory exists
        #     dst_dir = "processed_cards"
        #     os.makedirs(dst_dir, exist_ok=True)
        #     # Move the file
        #     shutil.move(image_path, os.path.join(dst_dir, filename))
        #     print(f"✅ Card processed successfully: {image_path}")
        # time.sleep(1)  # Wait for 1 second before next check
    except KeyboardInterrupt:
        print("\nScript terminated by user")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Only quit if explicitly requested
        if input("Do you want to close the browser? (y/n): ").lower() == 'y':
            driver.quit()
    
def fill_webpage_form(driver):
    for card_code in card_codes:
        fill_input_text(driver, card_code["card_code"], "//input[@placeholder='Nhập mã thẻ*']")
        
        save_captcha_image(driver)
        break
        
if __name__ == "__main__":
    card_codes = read_card_and_save_to_file(CARD_DIR)
    visit_page(fill_webpage_form)
    