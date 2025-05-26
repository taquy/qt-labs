from selenium.webdriver.support.ui import WebDriverWait
import os
import io
from show_image import show_image_and_prompt, show_retry_popup
from read_card import read_card_and_save_to_file
import shutil
from chrome_driver import setup_driver, fill_input_text
from read_captcha import wait_for_image_stability

CARD_DIR = "cards"

def form_fill_and_submit(driver, card_code):
    driver.refresh()
    WebDriverWait(driver, 10).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )
    fill_input_text(driver, card_code, "//input[@placeholder='Nhập mã thẻ*']")
    image = wait_for_image_stability(driver)
    if image is None:
        print("❌ Failed to capture CAPTCHA image")
        return False
    captcha_text = show_image_and_prompt(image)
    if captcha_text is None:
        print("❌ No CAPTCHA text entered")
        return False
    fill_input_text(driver, captcha_text, "//input[@placeholder='Nhập mã bảo mật*']")
    driver.find_element("css selector", "div.payment-online__btn-2column a.button.button--primary").click()
    
    action = show_retry_popup()
    if action == "continue":
        return True
    elif action == "retry":
        return form_fill_and_submit(driver, card_code)
    elif action == "stop":
        return False

def visit_page():
    card_codes = read_card_and_save_to_file(CARD_DIR)
    driver = setup_driver()
    driver.get("https://vietteltelecom.vn/nap-the")
    for card_code in card_codes:
        code = card_code['card_code']
        if not form_fill_and_submit(driver, code):
            break
        dst_dir = "processed_cards"
        os.makedirs(dst_dir, exist_ok=True)
        # Move the file
        image_path = card_code['image_path']
        filename = image_path.split("/")[-1]
        shutil.move(image_path, os.path.join(dst_dir, filename))
        print(f"✅ Card processed successfully: {image_path}")
    driver.quit()
        
if __name__ == "__main__":
    visit_page()
    