import os
import requests
from playwright.sync_api import sync_playwright

def scrape_and_send():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://www.set.or.th/th/market/statistics/investor-type", timeout=60000, wait_until="networkidle")
        page.wait_for_timeout(5000) 
        
        rows_data = []
        tables = page.locator("table")
        
        # วนลูปหาตารางที่มีข้อมูลกลุ่มนักลงทุนอยู่ข้างใน
        for i in range(tables.count()):
            table = tables.nth(i)
            text_content = table.inner_text()
            if "นักลงทุน" in text_content or "สถาบันในประเทศ" in text_content:
                tr_elements = table.locator("tr")
                for j in range(tr_elements.count()):
                    tds = tr_elements.nth(j).locator("th, td")
                    row_values = [tds.nth(k).inner_text().strip() for k in range(tds.count())]
                    if row_values:
                        rows_data.append(row_values)
                break # เจอแล้วหยุดวนลูป
                
        browser.close()

    if not rows_data:
        raise Exception("ไม่พบตารางข้อมูลนักลงทุนที่ต้องการ")

    # ส่งข้อมูลไปยัง Apps Script Web App
    web_app_url = os.environ["WEB_APP_URL"]
    response = requests.post(web_app_url, json=rows_data)
    print("Response from Google Sheets:", response.text)

if __name__ == "__main__":
    scrape_and_send()
