import os
import time
import requests
from playwright.sync_api import sync_playwright

def scrape_and_sign():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # ไปที่เว็บไซต์ SET
        page.goto("https://www.set.or.th/th/market/statistics/investor-type", timeout=60000, wait_until="networkidle")
        
        # รอให้ตารางและข้อมูลภายในโหลดขึ้นมาจริงๆ (รออย่างน้อย 6 วินาที)
        page.wait_for_timeout(60000) # เผื่อเวลาให้ JavaScript ทำงานเสร็จ
        
        # ค้นหาตารางทั้งหมดในหน้าเว็บ
        tables = page.locator("table")
        all_rows_data = []
        
        print(f"พบตารางทั้งหมด {tables.count()} ตาราง")
        
        for i in range(tables.count()):
            table = tables.nth(i)
            # ดึงทุกแถว (ทั้ง tr, th, td) ในตารางนี้
            tr_elements = table.locator("tr")
            tr_count = tr_elements.count()
            
            if tr_count > 1: # เอาเฉพาะตารางที่มีมากกว่า 1 แถว (มีข้อมูล)
                table_has_data = False
                temp_table_rows = []
                
                for j in range(tr_count):
                    tr = tr_elements.nth(j)
                    cells = tr.locator("th, td")
                    row_values = [cells.nth(k).inner_text().strip() for k in range(cells.count())]
                    
                    if row_values:
                        temp_table_rows.append(row_values)
                        table_has_data = True
                
                if table_has_data:
                    all_rows_data.extend(temp_table_rows)
                    # เว้นบรรทัดแยกระหว่างตาราง
                    all_rows_data.append([]) 

        browser.close()

    if not all_rows_data:
        raise Exception("ไม่สามารถดึงข้อมูลตารางจากหน้าเว็บได้")

    # ส่งข้อมูลไปยัง Google Apps Script Web App
    web_app_url = os.environ["WEB_APP_URL"]
    response = requests.post(web_app_url, json=all_rows_data)
    print("Response from Google Sheets:", response.text)

if __name__ == "__main__":
    scrape_and_sign()
