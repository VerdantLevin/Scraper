import sqlite3
import matplotlib.pyplot as plt

dbname = "/db/hotels.db"
hotels = []

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
    plt.savefig("./summary/SBScore.png")
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
    plt.savefig("./summary/SBReview.png")
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
    plt.savefig("./summary/SBDistrict.png")
    plt.show()
    
if __name__ == "__main__":
    conn = sqlite3.connect(dbname)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM hotels")
    hotels = cursor.fetchall()
    summarize_by_score()
    summarize_by_districts()
    summarize_by_reviews()