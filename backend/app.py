from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import mysql.connector
from mysql.connector import errorcode
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.secret_key = "secret123"

# ================= DATABASE CONFIG =================
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "11111",
    "database": "simple_login"
}

# ================= INIT DATABASE =================
def init_db():
    try:
        # --- 1️⃣ Kết nối MySQL (chưa có database) ---
        conn = mysql.connector.connect(
            host=db_config["host"],
            user=db_config["user"],
            password=db_config["password"]
        )
        cursor = conn.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS simple_login CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
        print("✅ Database 'simple_login' checked/created.")
        cursor.close()
        conn.close()

        # --- 2️⃣ Kết nối lại MySQL với database vừa tạo ---
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # --- 3️⃣ Tạo bảng users nếu chưa có ---
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                email VARCHAR(100) NOT NULL,
                username VARCHAR(50) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        cursor.close()
        conn.close()
        print("✅ Table 'users' checked/created successfully!")

    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("❌ Lỗi: Sai username hoặc password MySQL.")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("❌ Database không tồn tại và không thể tạo.")
        else:
            print("❌ Lỗi MySQL:", err)

# ================= ROUTES =================
@app.route('/')
def home():
    return redirect(url_for('login'))

# ---- Đăng ký ----
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Hỗ trợ cả form HTML và JSON từ frontend Node.js
        if request.is_json:
            data = request.get_json()
            email = data.get('email', '').strip()
            username = data.get('username', '').strip()
            password = data.get('password', '').strip()
        else:
            email = request.form.get('email', '').strip()
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '').strip()

        if not email or not username or not password:
            if request.is_json:
                return jsonify({"success": False, "message": "Vui lòng nhập đầy đủ thông tin!"}), 400
            flash("Vui lòng nhập đầy đủ thông tin!", "danger")
            return redirect(url_for('register'))

        hashed_pw = generate_password_hash(password)

        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (email, username, password) VALUES (%s, %s, %s)",
                (email, username, hashed_pw)
            )
            conn.commit()
            if request.is_json:
                return jsonify({"success": True, "message": "Đăng ký thành công!"})
            flash("Đăng ký thành công! Mời bạn đăng nhập.", "success")
            return redirect(url_for('login'))
        except mysql.connector.IntegrityError:
            if request.is_json:
                return jsonify({"success": False, "message": "Tên người dùng đã tồn tại!"}), 400
            flash("Tên người dùng đã tồn tại!", "danger")
            return redirect(url_for('register'))
        finally:
            cursor.close()
            conn.close()

    return render_template('register.html')

# ---- Đăng nhập ----
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()
            username = data.get('username', '').strip()
            password = data.get('password', '').strip()
        else:
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '').strip()

        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("SELECT password FROM users WHERE username=%s", (username,))
        row = cursor.fetchone()
        cursor.close()
        conn.close()

        if row and check_password_hash(row[0], password):
            if request.is_json:
                return jsonify({"success": True, "message": "Đăng nhập thành công!", "username": username})
            flash("Đăng nhập thành công!", "success")
            return redirect(url_for('welcome', username=username))
        else:
            if request.is_json:
                return jsonify({"success": False, "message": "Sai tên đăng nhập hoặc mật khẩu!"}), 401
            flash("Sai tên đăng nhập hoặc mật khẩu!", "danger")
            return redirect(url_for('login'))

    return render_template('login.html')

# ---- Trang chào mừng ----
@app.route('/welcome')
def welcome():
    username = request.args.get('username', 'Khách')
    return render_template('welcome.html', username=username)

# ================= MAIN =================
if __name__ == '__main__':
    init_db()  # ✅ tự tạo database + bảng nếu chưa có
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
