import os
import requests
from playwright.sync_api import sync_playwright

def scrape_and_send():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://www.set.or.th/th/market/statistics/investor-type", timeout=60000, wait_until="networkidle")
        page.wait_for_timeout(5000) 
        
        all_rows_data = []
        tables = page.locator("table")
        
        # วนลูปดึงข้อมูลจากทุกตารางที่มีในหน้าเว็บ
        for i in range(tables.count()):
            table = tables.nth(i)
            text_content = table.inner_text()
            
            # กรองเอาเฉพาะตารางที่เกี่ยวกับกลุ่มนักลงทุน
            if "นักลงทุน" in text_content or "สถาบันในประเทศ" in text_content:
                tr_elements = table.locator("tr")
                for j in range(tr_elements.count()):
                    tds = tr_elements.nth(j).locator("th, td")
                    row_values = [tds.nth(k).inner_text().strip() for k in range(tds.count())]
                    if row_values:
                        all_rows_data.append(row_values)
                
                # เว้น 1 แถวระหว่างตาราง เพื่อให้ Google Sheets แยกตารางสวยงาม
                all_rows_data.append([]) 
                
        browser.close()

    if not all_rows_data:
        raise Exception("ไม่พบข้อมูลตารางในเว็บไซต์")

    # ส่งข้อมูลทั้งหมดไปยัง Apps Script Web App
    web_app_url = os.environ["WEB_APP_URL"]
    response = requests.post(web_app_url, json=all_rows_data)
    print("Response from Google Sheets:", response.text)

if __name__ == "__main__":
    scrape_and_send()
