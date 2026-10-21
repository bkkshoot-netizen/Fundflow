import os
import requests
from playwright.sync_api import sync_playwright

def scrape_and_send():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # ไปที่หน้าเว็บและรอจนกว่าการโหลดเครือข่ายจะสงบลง (ป้องกันหน้าเว็บโหลดไม่ทัน)
        page.goto("https://www.set.or.th/th/market/statistics/investor-type", timeout=60000, wait_until="networkidle")
        
        # รอให้ตารางข้อมูลตัวเลขแสดงขึ้นมา (เจาะจงรอคลาสของตาราง หรือรออย่างน้อย 5 วินาทีให้ข้อมูลวิ่งเสร็จ)
        page.wait_for_timeout(5000) 
        
        rows_data = []
        # ค้นหาตารางทั้งหมดในหน้าเว็บ
        tables = page.locator("table")
        
        if tables.count() > 0:
            # ดึงข้อมูลจากตารางแรกที่เจอ
            first_table = tables.nth(0)
            tr_elements = first_table.locator("tr")
            
            for i in range(tr_elements.count()):
                tds = tr_elements.nth(i).locator("th, td")
                row_values = [tds.nth(j).inner_text().strip() for j in range(tds.count())]
                if row_values:
                    rows_data.append(row_values)
                    
        browser.close()

    if not rows_data:
        raise Exception("ไม่พบข้อมูลในตารางหลังจากโหลดหน้าเว็บ")

    # ส่งข้อมูลไปยัง Apps Script Web App
    web_app_url = os.environ["WEB_APP_URL"]
    response = requests.post(web_app_url, json=rows_data)
    print("Response from Google Sheets:", response.text)

if __name__ == "__main__":
    scrape_and_send()
