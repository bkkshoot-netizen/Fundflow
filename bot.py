import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

def scrape_and_send():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    raw_rows_data = []
    try:
        driver.get("https://www.set.or.th/th/market/statistics/investor-type")
        
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.TAG_NAME, "table"))
        )
        time.sleep(6)
        
        tables = driver.find_elements(By.TAG_NAME, "table")
        print(f"พบตารางทั้งหมด {len(tables)} ตาราง")
        
        if len(tables) >= 2:
            target_table = tables[1] 
            rows = target_table.find_elements(By.TAG_NAME, "tr")
            
            for row in rows:
                cells = row.find_elements(By.TAG_NAME, "th") + row.find_elements(By.TAG_NAME, "td")
                row_values = [cell.text.strip() for cell in cells]
                if row_values:
                    raw_rows_data.append(row_values)
                    
    finally:
        driver.quit()

    if not raw_rows_data:
        raise Exception("ไม่สามารถดึงข้อมูลตารางสุทธิได้")

    # --- จัดการปรับจำนวนคอลัมน์ใน Python ให้เท่ากันทุกแถว ---
    max_cols = max(len(row) for row in raw_rows_data)
    normalized_data = []
    for row in raw_rows_data:
        # เติมช่องว่าง ("") ให้แถวที่สั้นกว่า มีความยาวเท่ากับแถวที่ยาวที่สุด
        while len(row) < max_cols:
            row.append("")
        normalized_data.append(row)

    # ส่งข้อมูลที่จัดระเบียบแล้วไปยัง Google Apps Script Web App
    web_app_url = os.environ["WEB_APP_URL"]
    response = requests.post(web_app_url, json=normalized_data)
    print("Response from Google Sheets:", response.text)

if __name__ == "__main__":
    scrape_and_send()
