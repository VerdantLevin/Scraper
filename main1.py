from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import re
import json
import os
import sqlite3

class BinhLuan:
    def __init__(self, ho_ten, ngay_thang, cam_nhan_kh, nhan_xet, so_sao_dg):
        self.ho_ten = ho_ten
        self.ngay_thang = ngay_thang
        self.cam_nhan_kh = cam_nhan_kh
        self.nhan_xet = nhan_xet
        self.so_sao_dg = so_sao_dg
    
    def to_dict(self):
        return {
            'ho_ten': self.ho_ten,
            'ngay_thang': self.ngay_thang,
            'cam_nhan_kh': self.cam_nhan_kh,
            'nhan_xet': self.nhan_xet,
            'so_sao_dg': self.so_sao_dg
        }

class Hotel:
    def __init__(self, ten_ks, so_sao, danh_gia, dia_chi):
        self.ten_ks = ten_ks
        self.so_sao = so_sao
        self.danh_gia = danh_gia
        self.dia_chi = dia_chi
        self.binh_luan = []  # List to store comments

    def to_dict(self):
        return {
            'ten_ks': self.ten_ks,
            'so_sao': self.so_sao,
            'danh_gia': self.danh_gia,
            'dia_chi': self.dia_chi,
            'binh_luan': [bl.to_dict() for bl in self.binh_luan]
        }    
hotels = []

driver = webdriver.Firefox()  # or webdriver.Chrome(), depending on the browser you want to use

# Navigate to the URL
driver.get("https://www.agoda.com/vi-vn/search?city=2758&ds=PXwtKGwWe71gI0kf")

for i in range(10):
# Wait for the web page to load
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.Box-sc-kv6pi1-0.hRUYUu.JacketContent.JacketContent--Empty')))

    # Scroll to the middle of the page
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 2);")
    time.sleep(3)
    # Scroll down to the bottom of the page
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(3)

    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(3)

    # Parse the web page content
    soup = BeautifulSoup(driver.page_source, "html.parser")

    # Find all divs with the specified class, then find 'a' tags within those divs
    divs = soup.findAll('div', class_="Box-sc-kv6pi1-0 hRUYUu JacketContent JacketContent--Empty")
    links = [div.find('a').attrs["href"] for div in divs if div.find('a') and "href" in div.find('a').attrs]
    
    # Open a new tab
    driver.execute_script("window.open('');")

    # Switch to the new tab (it's always the last one)
    driver.switch_to.window(driver.window_handles[-1])
    
    for link in links:
        # print("zzz")
        try:
            driver.get("https://www.agoda.com" + link)
            
            waits = WebDriverWait(driver, 80)
            waits.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.Review-comment-bodyText')))
            soup = BeautifulSoup(driver.page_source, "html.parser")

            ten_ks = soup.find('p', class_="HeaderCerebrum__Name").text

            dg = soup.find('p', class_="Typographystyled__TypographyStyled-sc-j18mtu-0 Hkrzy kite-js-Typography").text
            # danh_gia = re.search(r'\d+', dg).group()

            so_sao_div = soup.find('p', class_="sc-jrAGrp sc-kEjbxe fzPhrN gOeEsn").text
            # so_sao = so_sao_div.split('\n', 2)[1]

            dia_chi_div = soup.find('span', class_="Spanstyled__SpanStyled-sc-16tp9kb-0 gwICfd kite-js-Span HeaderCerebrum__Address").text
            # dia_chi = dia_chi_div.split('\n', 2)[1]

            hotel = Hotel(ten_ks, so_sao_div, dg, dia_chi_div)
            
            reviews = soup.find_all('div', class_='Review-comment')
            for review in reviews:
                # ho_ten = review.find('strong').text
                ho_ten_element = review.find('strong')
                if ho_ten_element is not None:
                    ho_ten = ho_ten_element.text
                else:
                    ho_ten = ""
                # ngay_thang_div = review.find('span', class_='Review-statusBar-date').text
                ngay_thang_element = review.find('span', class_='Review-statusBar-date')
                if ngay_thang_element is not None:
                    ngay_thang_div = ngay_thang_element.text
                else:
                    ngay_thang_div = ""
                # ngay_thang = ngay_thang_div.split('\n',2)[0]
                # cam_nhan_kh_div = review.find('h3', class_='Review-comment-bodyTitle').text
                cam_nhan_element = review.find('h3', class_='Review-comment-bodyTitle')
                if cam_nhan_element is not None:
                    cam_nhan_kh_div = cam_nhan_element.text
                else:
                    cam_nhan_kh_div = ""
                # cam_nhan_kh = cam_nhan_kh_div.split('\n', 2)[0]
                nhan_xet_element = review.find('p', class_='Review-comment-bodyText')
                if nhan_xet_element is not None:
                    nhan_xet_div = nhan_xet_element.text
                else:
                    nhan_xet_div = ""
                # nhan_xet = nhan_xet_div.split('\n', 2)[0]
                # so_sao_div1 = review.find('div', class_='Review-comment-leftScore').text
                so_sao_element = review.find('div', class_='Review-comment-leftScore')
                if so_sao_element is not None:
                    so_sao_div1 = so_sao_element.text
                else:
                    so_sao_div1 = ""
                # so_sao_dg = so_sao_div1.split('\n', 2)[1]
                binh_luan = BinhLuan(ho_ten, ngay_thang_div, cam_nhan_kh_div, nhan_xet_div, so_sao_div1)
                hotel.binh_luan.append(binh_luan)
            # Nhap thong tin khach san vao class Hotel
            hotels.append(hotel)
        except Exception:
            continue
    driver.close()

    time.sleep(1)
    # Switch back to the original tab
    driver.switch_to.window(driver.window_handles[0])

    # Find the next page button by its CSS selector (replace 'css_selector' with the actual CSS selector)
    next_page_button = driver.find_element(By.ID, 'paginationNext')
    if next_page_button:
        next_page_button.click()
    else:
        break


'''
# Check if the file exists and is not empty
if os.path.exists('hotels.json') and os.path.getsize('hotels.json') > 0:
    # Read the existing data
    with open('hotels.json', 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            # If the file contains invalid JSON, initialize an empty list
            data = []
else:
    # If the file doesn't exist or is empty, initialize an empty list
    data = []

# Add the new data
new_hotels = [hotel.to_dict() for hotel in hotels]
data.extend(new_hotels)

# Write the updated data back to the file
with open('hotels.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=4)

print("Đã lưu file hotels.json thành công!")

# Don't forget to close the browser when you're done
driver.quit()
'''

conn = sqlite3.connect("db/hotels.db")
cursor = conn.cursor()
for hotel in hotels:
    cursor.execute(f"SELECT 1 FROM hotels WHERE ten_ks = '{hotel.ten_ks}'")
    if cursor.rowcount==0:
        conn.execute(f"INSERT INTO hotels (ten_ks, so_sao, danh_gia, dia_chi) VALUES ('{hotel.ten_ks}','{hotel.so_sao}','{hotel.danh_gia}','{hotel.dia_chi}')")
conn.commit()    