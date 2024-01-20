from flask import Flask, render_template
import sqlite3

app = Flask(__name__)
app.secret_key = "vevdvwfwefw".encode("utf8")
app.template_folder = "templates"
app.static_folder = "static"
dbname = "db/hotels.db"

#Tao trang chinh  
@app.route("/", methods = ["GET","POST"])
def index():
    conn = sqlite3.connect(dbname)
    cursor = conn.cursor()
    cmline = f"SELECT * FROM hotels"
    cursor.execute(cmline)
    hotels = cursor.fetchall()
    conn.close()
    return render_template("index.html", hotels = hotels)
    
#Tao trang cho tung khach san
@app.route("/details/<int:id>", methods = ["GET"])
def details(id):
    conn = sqlite3.connect(dbname)
    cursor = conn.cursor()
    cursor.execute(f'select * from hotels where id = {id}')
    detail = cursor.fetchone()
    cursor.execute(f'select * from binh_luan where hotel_id = {id}')
    comments = cursor.fetchall()
    conn.close()
    return render_template("detail.html", detail = detail, comments = comments)

if __name__ == "__main__":
    app.run()