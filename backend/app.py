# backend/app.py
import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import mysql.connector
from mysql.connector import errorcode
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

# load .env
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "secret123")

# ================= DATABASE CONFIG (từ .env) =================
db_config = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASS", ""),
    "database": os.getenv("DB_NAME", "railway"),
    "port": int(os.getenv("DB_PORT", 3306)),
    "raise_on_warnings": True
}

# ================= INIT DATABASE (chỉ tạo bảng) =================
def init_db():
    try:
        # Kết nối trực tiếp tới database đã có trên Railway
        conn = mysql.connector.connect(
            host=db_config["host"],
            user=db_config["user"],
            password=db_config["password"],
            database=db_config["database"],
            port=db_config["port"]
        )
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                email VARCHAR(100) NOT NULL,
                username VARCHAR(50) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)
        conn.commit()
        cursor.close()
        conn.close()
        print("✅ Table 'users' checked/created successfully on Railway.")
    except mysql.connector.Error as err:
        # Hiển thị lỗi rõ ràng
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("❌ Lỗi: Sai username hoặc password MySQL.")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("❌ Database không tồn tại trên server (kiểm tra DB_NAME trong .env).")
        else:
            print("❌ Lỗi MySQL:", err)
    except Exception as e:
        print("❌ Lỗi khi khởi tạo DB:", e)

# ================= ROUTES =================
@app.route('/')
def home():
    return redirect(url_for('login'))

# ---- Đăng ký ----
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
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

        conn = None
        cursor = None
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
            # duplicate username
            if request.is_json:
                return jsonify({"success": False, "message": "Tên người dùng đã tồn tại!"}), 400
            flash("Tên người dùng đã tồn tại!", "danger")
            return redirect(url_for('register'))
        except Exception as e:
            print("❌ Error in register:", e)
            if request.is_json:
                return jsonify({"success": False, "message": "Lỗi server"}), 500
            flash("Lỗi server", "danger")
            return redirect(url_for('register'))
        finally:
            if cursor:
                cursor.close()
            if conn:
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

        conn = None
        cursor = None
        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()
            cursor.execute("SELECT password FROM users WHERE username=%s", (username,))
            row = cursor.fetchone()
        except Exception as e:
            print("❌ Error in login DB:", e)
            row = None
        finally:
            if cursor:
                cursor.close()
            if conn:
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

# ---- Welcome page ----
@app.route('/welcome')
def welcome():
    username = request.args.get('username', 'Khách')
    return render_template('welcome.html', username=username)

# ================= MAIN =================
if __name__ == '__main__':
    # chỉ init bảng (không tạo database) — Railway đã có database
    init_db()
    port = int(os.getenv('PORT', 5000))
    debug_mode = os.getenv("FLASK_ENV", "production") == "development"
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
