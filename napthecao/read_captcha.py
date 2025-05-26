from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import time
from PIL import Image
import io
import hashlib


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
    
    for attempt in range(max_attempts):
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
            print(f"❌ Error capturing CAPTCHA: {str(e)}")
            if os.path.exists("temp_screenshot.png"):
                os.remove("temp_screenshot.png")
            time.sleep(0.5)
    
    print("❌ Failed to capture CAPTCHA image")
    return None
    