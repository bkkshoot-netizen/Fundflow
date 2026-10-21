import os
import json
from playwright.sync_api import sync_playwright
from google.oauth2.service_account import Credentials
import gspread

def scrape_and_update():
    # 1. ใช้ Playwright ดึงข้อมูลจากเว็บ SET
    with sync_playwright() as p:
        # รันแบบ Headless (ไม่แสดงหน้าจอเบราว์เซอร์)
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # ไปที่หน้าเว็บไซต์ SET
        page.goto("https://www.set.or.th/th/market/statistics/investor-type", timeout=60000)
        
        # รอให้ตารางข้อมูลโหลดเสร็จ (รอให้เจอ tag ตารางหรือข้อมูลที่ต้องการ)
        page.wait_for_selector("table", timeout=30000)
        
        # ดึงข้อมูลจากตาราง (ตัวอย่างนี้ดึงแถวทั้งหมดในตารางแรก)
        rows_data = []
        tables = page.locator("table")
        first_table = tables.nth(0) # เลือกตารางแรก
        
        tr_elements = first_table.locator("tr")
        count = tr_elements.count()
        
        for i in range(count):
            tds = tr_elements.nth(i).locator("th, td")
            row_values = []
            for j in range(tds.count()):
                row_values.append(tds.nth(j).inner_text().strip())
            if row_values:
                rows_data.append(row_values)
                
        browser.close()

    if not rows_data:
        raise Exception("ไม่พบข้อมูลในตารางที่ดึงมา")

    # 2. เชื่อมต่อ Google Sheets ผ่าน Service Account
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    service_account_info = json.loads(os.environ["GOOGLE_SERVICE_ACCOUNT"])
    creds = Credentials.from_service_account_info(service_account_info, scopes=scope)
    client = gspread.authorize(creds)

    # เปิด Google Sheets ด้วย ID
    spreadsheet_id = os.environ["SPREADSHEET_ID"]
    sheet = client.open_by_key(spreadsheet_id).sheet1

    # 3. ล้างข้อมูลเก่าและอัปเดตข้อมูลใหม่ลงชีต
    sheet.clear()
    sheet.update(rows_data)
    print("ดึงข้อมูลด้วย Playwright และอัปเดตลง Google Sheets สำเร็จ!")

if __name__ == "__main__":
    scrape_and_update()
