import json
import sqlite3
import re

conn = sqlite3.connect("db/hotels.db")
cursor = conn.cursor()
hotels = json.load(open("hotels.json", encoding="utf8"))
'''
col1 = ['ten_ks','so_sao','danh_gia','dia_chi']
col2 = ['ho_ten', 'ngay_thang', 'cam_nhan_kh', 'nhan_xet', 'so_sao_dg']
'''

months = {"tháng một": "01", "tháng hai": "02", "tháng ba": "03", "tháng tư": "04", "tháng năm": "05", "tháng sáu": "06", "tháng bảy": "07", "tháng tám": "08", "tháng chín": "09", "tháng mười": "10", "tháng mười một": "11", "tháng mười hai": "12"}

def reformat(date):
    day = re.search("\s[0-9]{2}\s",date).group().strip()
    year = re.search("\s[0-9]{4}",date).group().strip()
    for test in months.keys():
        temp = re.search(date, test)
        if temp != "":
            month = months[test]
            break
    combined_date = (day, month, year)
    return "/".join(combined_date)

for ht in hotels:
    ten = re.sub("\(.*\)", "", ht['ten_ks']).replace("\'","\'\'")
    cursor.execute(f"SELECT 1 FROM hotels WHERE ten_ks LIKE '%{ten}%'")
    if cursor.fetchone() is None:
        diem = ht['so_sao'].replace(",",".")
        dg = ht['danh_gia'].replace(" bài đánh giá", "")
        dc = ht['dia_chi'].replace("\'","\'\'")
        cursor.execute(f"INSERT INTO hotels (ten_ks, so_sao, danh_gia, dia_chi) VALUES ('{ten}', '{diem}', '{dg}', '{dc}')")
        hotel_id = cursor.lastrowid
        for cm in ht['binh_luan']:
            name = cm['ho_ten']
            impr = cm['cam_nhan_kh'].replace("\'","\'\'")
            dt = reformat(cm['ngay_thang'])
            rev = cm['nhan_xet'].replace("\'","\'\'")
            pt = cm['so_sao_dg'].replace(",",".")+"/10"
            cursor.execute(f"INSERT INTO binh_luan (hotel_id, ho_ten, ngay_thang, cam_nhan_kh, nhan_xet, so_sao_dg) VALUES ({hotel_id},'{name}','{dt}','{impr}','{rev}','{pt}')")
conn.commit()
conn.close()