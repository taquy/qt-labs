import boto3
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import os
import json

def read_card_code(file_path):
    # Create Textract client
    textract = boto3.client('textract', region_name='us-east-1')  # Change region if needed

    # Read local image
    with open(file_path, "rb") as image_file:
        image_bytes = image_file.read()

    # Call AWS Textract
    response = textract.detect_document_text(Document={'Bytes': image_bytes})

    for item in response["Blocks"]:
        if item["BlockType"] == "LINE":
            text = item["Text"]
            # Find all numbers in the text
            numbers = re.findall(r'\d+', text)
            for number in numbers:
                if len(str(number)) == 15:
                    return number
        
def check_if_card_code_exists(card_codes, image_path):
    for card_code in card_codes:
        if card_code["image_path"] == image_path:
            return True
    return False
    
def read_card_and_save_to_file(card_dir):
    print(f"Reading card codes from {card_dir}")
    card_codes = []
    
    # check if the image is already OCR read
    if os.path.exists("card_code.json"):
        with open("card_code.json", "r") as file:
            card_codes = json.load(file)
        print(f"Found {len(card_codes)} card codes in the file")
    else:
        print("No card code file found, will read all cards")

            
    card_files = os.listdir(card_dir)
    if not card_files:
        print(f"No card files found in {card_dir}")
        return
    
    for filename in card_files:
        if filename.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp")):
            print(f"Reading card code from {filename}")
            image_path = os.path.join(card_dir, filename)
            if check_if_card_code_exists(card_codes, image_path):
                continue
            card_code = read_card_code(image_path)
            card_codes.append({ 
                "image_path": image_path,
                "card_code": card_code
            })
    with open("card_code.json", "w") as file:
        json.dump(card_codes, file)

# print(read_card_code("cards/IMG_7779.PNG"))
