## 使用Flask做前後端整合 ##
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mysqldb import MySQL
# 加密密碼用
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# 配置 MySQL 資料庫
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '1234'
app.config['MYSQL_DB'] = 'product_test'

# 初始化 MySQL
mysql = MySQL(app)

# 設定密鑰以便於使用 Flask 的 session
app.secret_key = 'your_secret_key'

@app.route('/')
def index():
    return render_template('login.html')

# 登入
@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    cur = mysql.connection.cursor()
    cur.execute("SELECT password FROM users WHERE username = %s", (username,))
    result = cur.fetchone()
    
    if result and check_password_hash(result[0], password):
        flash('登入成功！', 'success')
        return redirect(url_for('index'))
    else:
        flash('用戶名稱或密碼錯誤！', 'danger')
        return redirect(url_for('index'))

# 註冊
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # 加密用
        hashed_password = generate_password_hash(password)

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed_password))
        mysql.connection.commit()
        cur.close()
        flash('註冊成功！請登入。', 'success')
        return redirect(url_for('index'))
    return render_template('register.html')

# 修改密碼
@app.route('/change', methods=['GET', 'POST'])
def change_password():
    if request.method == 'POST':
        username = request.form['username']
        old_password = request.form['old_password']
        new_password = request.form['new_password']
        
        cur = mysql.connection.cursor()
        cur.execute("SELECT password FROM users WHERE username = %s", (username,))
        result = cur.fetchone()
        # 先確認有此使用者
        if result is None:
            flash('使用者名稱不存在！', 'danger')
        else:
            # 確認舊密碼不存在
            if check_password_hash(result[0], old_password):
                # 確認新舊密碼不同
                if new_password == old_password:
                    flash('舊密碼不得與新密碼相同', 'danger')
                else:
                    # 以上都成立 修改成功
                    hashed_new_password = generate_password_hash(new_password)
                    cur.execute("UPDATE users SET password = %s WHERE username = %s", (hashed_new_password, username))
                    mysql.connection.commit()
                    flash('密碼修改成功！', 'success')
            else:
                flash('舊密碼不正確！', 'danger')

        cur.close()
        return redirect(url_for('change_password'))
    
    return render_template('change.html')



if __name__ == '__main__':
    app.run(debug=True)

