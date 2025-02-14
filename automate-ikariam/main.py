from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Path to Chrome user profile directory (update with your correct macOS username)
chrome_profile_path = "/Users/YourUsername/Library/Application Support/Google/Chrome"

# Choose the profile name (replace with the correct profile name from chrome://version/)
profile_name = "Profile 2"  # Change to "Default" if it's the main profile

# Set up Chrome options
options = webdriver.ChromeOptions()
options.add_argument(f"--user-data-dir={chrome_profile_path}")  # Use existing Chrome user data
options.add_argument(f"--profile-directory={profile_name}")  # Use specific profile

# Initialize WebDriver with profile
driver = webdriver.Chrome(options=options)

try:
    # Open Ikariam website
    driver.get("https://www.ikariam.com/")

    # Wait for the page to fully load
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )

    # Find the first button containing "Play" text
    play_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Play')]"))
    )

    # Click the Play button
    play_button.click()
    print("Successfully clicked the Play button!")

except Exception as e:
    print(f"Error: {e}")

finally:
    input("Press Enter to close the browser...")
    driver.quit()