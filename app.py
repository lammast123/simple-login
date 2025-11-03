from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = "secret123"

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == "admin" and password == "123456":
            flash("Đăng nhập thành công!", "success")
            return redirect(url_for('welcome', username=username))
        else:
            flash("Sai tên đăng nhập hoặc mật khẩu!", "danger")
            return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/welcome')
def welcome():
    username = request.args.get('username', 'Khách')
    return render_template('welcome.html', username=username)


if __name__ == '__main__':
    # Cho phép chạy cả local và Render
    app.run(host='0.0.0.0', port=5000)
