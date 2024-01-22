import json
import sqlite3
import re

conn = sqlite3.connect("db/hotels.db")
cursor = conn.cursor()
hotels = json.load(open("hotels.json", encoding="utf8"))
col1 = ['ten_ks','so_sao','danh_gia','dia_chi']
col2 = ['ho_ten', 'ngay_thang', 'cam_nhan_kh', 'nhan_xet', 'so_sao_dg']
for ht in hotels:
    ten = re.sub(ht['ten_ks'], "%\(.*\)%", "")
    diem = ht['so_sao']
    dg = ht['danh_gia'].replace(" bài đánh giá", "")
    dc = ht['dia_chi']
    cursor.execute(f"INSERT INTO hotels (ten_ks, so_sao, danh_gia, dia_chi) VALUES ('{ten}', '{diem}', '{dg}', '{dc}')")
    hotel_id = cursor.lastrowid
    for cm in ht['binh_luan']:
        name = cm['ho_ten']
        impr = cm['cam_nhan_kh']
        rev = cm['nhan_xet']
        pt = cm['so_sao_dg'].replace(",",".")
        cursor.execute(f"INSERT INTO binh_luan (hotel_id, ho_ten, cam_nhan_kh, nhan_xet) VALUES ({hotel_id},'{name}','{impr}','{rev}')")
conn.commit()
conn.close()