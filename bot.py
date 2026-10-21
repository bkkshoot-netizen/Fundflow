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
    
    all_rows_data = []
    try:
        driver.get("https://www.set.or.th/th/market/statistics/investor-type")
        
        # รอให้ตารางโหลดขึ้นมา
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.TAG_NAME, "table"))
        )
        time.sleep(6) # รอให้ข้อมูลตัวเลขวิ่งครบ
        
        tables = driver.find_elements(By.TAG_NAME, "table")
        print(f"พบตารางทั้งหมด {len(tables)} ตาราง")
        
        # เลือกตารางที่สอง (Index ที่ 1) ซึ่งคือตาราง "มูลค่าการซื้อขายสุทธิ ตามกลุ่มนักลงทุน"
        if len(tables) >= 2:
            target_table = tables[1] 
            rows = target_table.find_elements(By.TAG_NAME, "tr")
            
            for row in rows:
                # ดึงข้อมูลจากทุกเซลล์ในแถว (ทั้ง th และ td)
                cells = row.find_elements(By.TAG_NAME, "th") + row.find_elements(By.TAG_NAME, "td")
                row_values = [cell.text.strip() for cell in cells]
                if row_values:
                    all_rows_data.append(row_values)
                    
    finally:
        driver.quit()

    if not all_rows_data:
        raise Exception("ไม่สามารถดึงข้อมูลตารางสุทธิได้")

    # ส่งข้อมูลไปยัง Google Apps Script Web App
    web_app_url = os.environ["WEB_APP_URL"]
    response = requests.post(web_app_url, json=all_rows_data)
    print("Response from Google Sheets:", response.text)

if __name__ == "__main__":
    scrape_and_send()
