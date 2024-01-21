import requests
from bs4 import BeautifulSoup
import re
import json
import sqlite3

def create_database():
    with sqlite3.connect('db/hotels.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS hotels (
                id INTEGER PRIMARY KEY,
                ten_ks TEXT,
                so_sao TEXT,
                danh_gia TEXT,
                dia_chi TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS binh_luan (
                id INTEGER PRIMARY KEY,
                hotel_id INTEGER,
                ho_ten TEXT,
                ngay_thang TEXT,
                cam_nhan_kh TEXT,
                nhan_xet TEXT,
                so_sao_dg TEXT,
                FOREIGN KEY(hotel_id) REFERENCES hotels(id)
            )
        ''')

        conn.commit()


def insert_data_into_db(hotel):
    with sqlite3.connect('db/hotels.db') as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO hotels (ten_ks, so_sao, danh_gia, dia_chi) VALUES (?, ?, ?, ?)",
                       (hotel.ten_ks, hotel.so_sao, hotel.danh_gia, hotel.dia_chi))
        hotel_id = cursor.lastrowid

        for binh_luan in hotel.binh_luan:
            cursor.execute(
                "INSERT INTO binh_luan (hotel_id, ho_ten, ngay_thang, cam_nhan_kh, nhan_xet, so_sao_dg) VALUES (?, ?, "
                "?, ?, ?, ?)",
                (hotel_id, binh_luan.ho_ten, binh_luan.ngay_thang, binh_luan.cam_nhan_kh, binh_luan.nhan_xet,
                 binh_luan.so_sao_dg))
        conn.commit()

class BinhLuan:
    def __init__(self, ho_ten, ngay_thang, cam_nhan_kh, nhan_xet, so_sao_dg):
        self.ho_ten = ho_ten
        self.ngay_thang = ngay_thang
        self.cam_nhan_kh = cam_nhan_kh
        self.nhan_xet = nhan_xet
        self.so_sao_dg = so_sao_dg

class Hotel:
    def __init__(self, ten_ks, so_sao, danh_gia, dia_chi):
        self.ten_ks = ten_ks
        self.so_sao = so_sao
        self.danh_gia = danh_gia
        self.dia_chi = dia_chi
        self.binh_luan = []  # List to store comments

hotels = []
def crawl(so_trang, url):
    response = requests.get(url+str(so_trang))
    soup = BeautifulSoup(response.content, "html.parser")

    titles = soup.findAll('h2')
    links = [link.find('a').attrs["href"] for link in titles if link.find('a') and "href" in link.find('a').attrs]

    
    for link in links:
        news = requests.get("https:"+ link)
        soup = BeautifulSoup(news.content, "html.parser")

        ten_ks = soup.find('a', id="lnkhotelname").text

        dg = soup.find('a', href="#CustomerReviews").text
        danh_gia = re.search(r'\d+', dg).group()

        so_sao_div = soup.find('span', class_="rtp").text
        so_sao = so_sao_div.split('\n', 2)[1]

        dia_chi_div = soup.find('p', style="float: left; margin: 0px 0px;").text
        dia_chi = dia_chi_div.split('\n', 2)[1]


        hotel = Hotel(ten_ks, so_sao, danh_gia, dia_chi)

        # thong tin cac danh gia
        reviews = soup.find_all('div', class_='listrote ri')
        for review in reviews:
            ho_ten = review.find('span', class_='nameauthor').text
            ngay_thang_div = review.find('span', class_='date').text
            ngay_thang = ngay_thang_div.split('\n',2)[0]
            cam_nhan_kh_div = review.find('span', class_='green').text
            cam_nhan_kh = cam_nhan_kh_div.split('\n', 2)[0]
            nhan_xet_div = review.find('span', class_='italic').text
            nhan_xet = nhan_xet_div.split('\n', 2)[0]
            so_sao_div1 = review.find('div', class_='customerrate').text
            so_sao_dg = so_sao_div1.split('\n', 2)[1]
            binh_luan = BinhLuan(ho_ten, ngay_thang, cam_nhan_kh, nhan_xet, so_sao_dg)
            hotel.binh_luan.append(binh_luan)

        # Nhap thong tin khach san vao class Hotel
        hotels.append(hotel)
        

#Get the number of pages
def get_pagination(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    # Find the pagination element - this will depend on the website's structure
    pagination = soup.find('div', class_='paging')

    if pagination:
        # Get all the page links in the pagination
        page_links = pagination.find_all('a')

        # Return the pagination links as a list of strings
        return [link.text for link in page_links if link.text.isdigit()]

    # If there's no pagination element, return an empty list
    return []
    
    
def convert_to_dict(obj):
    if isinstance(obj, BinhLuan):
        return obj.__dict__
    raise TypeError(f"Không thể chuyển đổi {obj} sang từ điển.")


def save_to_json(data):
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, default=convert_to_dict, ensure_ascii=False, indent=4)
    
def print_to_text():
    # Open the file for writing
    with open('./hotels.txt', 'w', encoding='utf-8') as f:
        f.write("Danh sách khách sạn khu vực Hà Nội: "+'\n')
        for hotel in hotels:
            # Write the information of each hotel to the file
            f.write("● Tên khách sạn: "+hotel.ten_ks+'\n')
            f.write("  Số sao: "+hotel.so_sao+'\n')
            f.write("  Đánh giá: "+hotel.danh_gia+" lượt đánh giá"+'\n')
            f.write("  Địa chỉ: "+hotel.dia_chi+'\n')
            f.write("  Chi tiết đánh giá của khách hàng:"+'\n')
            i=0
            for bl in hotel.binh_luan:
                i+=1
                f.write("    " +str(i)+",")
                f.write("Họ tên: " +bl.ho_ten+'\n')
                f.write("      Ngày tháng: "+bl.ngay_thang+'\n')
                f.write("      Cảm nhận khách hàng: "+bl.cam_nhan_kh+'\n')
                f.write("      Số sao đánh giá: "+bl.so_sao_dg+'\n')
                f.write("      Nhận xét: "+bl.nhan_xet+'\n')
            f.write('\n')
    print("Đã lưu file hotels.txt thành công!")

if __name__ == "__main__":
    create_database()
    url1 = "https://khachsan.chudu24.com/t.hanoi.html"
    so_trang = get_pagination(url1)
    hotels = []
    for st in so_trang:
        crawl(st, "https://khachsan.chudu24.com/t.hanoi.html?page=")
    for hotel in hotels:
        insert_data_into_db(hotel)
    hotels_data = [hotel.__dict__ for hotel in hotels]
    save_to_json(hotels_data)
