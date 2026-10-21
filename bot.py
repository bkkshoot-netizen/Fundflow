import os
import requests
from playwright.sync_api import sync_playwright

def scrape_and_send():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://www.set.or.th/th/market/statistics/investor-type", timeout=60000)
        page.wait_for_selector("table", timeout=30000)
        
        rows_data = []
        tables = page.locator("table")
        first_table = tables.nth(0)
        tr_elements = first_table.locator("tr")
        
        for i in range(tr_elements.count()):
            tds = tr_elements.nth(i).locator("th, td")
            row_values = [tds.nth(j).inner_text().strip() for j in range(tds.count())]
            if row_values:
                rows_data.append(row_values)
                
        browser.close()

    if not rows_data:
        raise Exception("ไม่พบข้อมูลในตาราง")

    # ดึง URL จาก GitHub Secrets ที่ตั้งค่าไว้ (ห้ามใส่ข้อความมั่วซ้ำซ้อน)
    web_app_url = os.environ["WEB_APP_URL"]
    
    response = requests.post(web_app_url, json=rows_data)
    print("Response from Google Sheets:", response.text)

if __name__ == "__main__":
    scrape_and_send()
