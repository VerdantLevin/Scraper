import requests
from bs4 import BeautifulSoup
import re
import matplotlib.pyplot as plt
from flask import Flask, render_template

app = Flask(__name__)
app.secret_key = "vevdvwfwefw".encode("utf8")
app.template_folder = "templates"
app.static_folder = "static"

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
        

#lay ra toan bo so trang trong web
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
    
# Summarize hotels by score
def summarize_by_score():
    scores = {}
    for hotel in hotels:
        score_k = int(float(hotel.so_sao))
        if score_k not in scores:
            scores.update({score_k:1})
        else:
            score_v = scores[score_k]
            scores.update({score_k: score_v+1})
    x = scores.keys()
    y = scores.values()
    plt.bar(x, y)
    plt.xlabel("Điểm")
    plt.ylabel("Số lượng")
    plt.title("Thống kê khách sạn theo điểm")
    plt.savefig("./SBScore.png")
    plt.show()

# Summarize hotels by number of reviews
def summarize_by_reviews():
    rev_num = {}
    for hotel in hotels:
        rev_k = int(hotel.danh_gia)
        if rev_k not in rev_num:
            rev_num.update({rev_k:1})
        else:
            rev_num.update({rev_k: rev_num[rev_k]+1})
    x = rev_num.keys()
    y = rev_num.values()
    plt.bar(x,y)
    plt.xlabel("Số đánh giá")
    plt.ylabel("Số lượng")
    plt.title("Thống kê khách sạn theo đánh giá")
    plt.savefig("./SBReview.png")
    plt.show()
        
# Summarize hotels by districts
def summarize_by_districts():
    count = 0
    total = 0
    districts = {"Hoàn Kiếm": 0, "Đống Đa": 0, "Tây Hồ": 0, "Hai Bà Trưng": 0, "Ba Đình": 0, "Cầu Giấy": 0, "Từ Liêm": 0, "Hà Đông": 0, "Khác": 0}
    for hotel in hotels:
        total += 1
        for key in districts:
            if key in hotel.dia_chi:
                districts.update({key: districts[key]+1})
                count += 1
                break
    districts.update({"Khác": total-count})
    x = districts.keys()
    y = districts.values()
    plt.bar(x,y)
    plt.xlabel("Quận")
    plt.xticks(rotation=45,ha='right')
    plt.ylabel("Số lượng")
    plt.title("Thống kê khách sạn theo khu vực")
    plt.savefig("./SBDistrict.png")
    plt.show()
    
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

#Tao trang web hien thi   
@app.route("/", methods = ["GET","POST"])
def index():
    return render_template("index.html", hotels = hotels)
    
if __name__ == "__main__":
    url1 = "https://khachsan.chudu24.com/t.hanoi.html"
    so_trang = get_pagination(url1)
    # Call the function
    for st in so_trang:
        crawl(st, "https://khachsan.chudu24.com/t.hanoi.html?page=")
    hotels = sorted(hotels, key=lambda hotel: int(hotel.danh_gia), reverse=True)
    #summarize_by_score()
    #summarize_by_reviews()
    #summarize_by_districts()
    app.run()
