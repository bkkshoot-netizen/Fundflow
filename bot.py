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
    # ตั้งค่าให้ Chrome รันแบบ Headless (ไม่แสดงหน้าจอ) บน GitHub Actions
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    # เปิดใช้งาน WebDriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    all_rows_data = []
    try:
        # ไปที่เว็บไซต์ SET
        driver.get("https://www.set.or.th/th/market/statistics/investor-type")
        
        # รอจนกว่าตารางจะปรากฏขึ้นมาในหน้าเว็บ (รอสูงสุด 30 วินาที)
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.TAG_NAME, "table"))
        )
        
        # หน่วงเวลาเพิ่มอีกสักนิดเพื่อให้ข้อมูลในตารางโหลดครบสมบูรณ์
        time.sleep(5)
        
        # ค้นหาตารางทั้งหมดในหน้าเว็บ
        tables = driver.find_elements(By.TAG_NAME, "table")
        print(f"พบตารางทั้งหมด {len(tables)} ตาราง")
        
        for table in tables:
            text_content = table.text
            # เลือกเฉพาะตารางที่มีข้อมูลกลุ่มนักลงทุน
            if "นักลงทุน" in text_content or "สถาบันในประเทศ" in text_content:
                rows = table.find_elements(By.TAG_NAME, "tr")
                temp_table_rows = []
                
                for row in rows:
                    cells = row.find_elements(By.TAG_NAME, "th") + row.find_elements(By.TAG_NAME, "td")
                    row_values = [cell.text.strip() for cell in cells]
                    if row_values:
                        temp_table_rows.append(row_values)
                
                if temp_table_rows:
                    all_rows_data.extend(temp_table_rows)
                    all_rows_data.append([]) # เว้นบรรทัดแยกระหว่างตาราง
                    
    finally:
        driver.quit()

    if not all_rows_data:
        raise Exception("ไม่สามารถดึงข้อมูลตารางด้วย Selenium ได้")

    # ส่งข้อมูลไปยัง Google Apps Script Web App ที่ตั้งค่าไว้
    web_app_url = os.environ["WEB_APP_URL"]
    response = requests.post(web_app_url, json=all_rows_data)
    print("Response from Google Sheets:", response.text)

if __name__ == "__main__":
    scrape_and_send()
