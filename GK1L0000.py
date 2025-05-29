from flask import Flask, render_template, request, redirect, url_for, session
import os
import GK1S0001
from datetime import timedelta

app = Flask(__name__)
app.secret_key = "your_fixed_secret_key_here"  # 固定のキーを使用
app.config['SESSION_PERMANENT'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)  # セッション有効期限30分

# ログインページ
@app.route('/', methods=['GET', 'POST'])
def GK_login():
    if request.method == 'POST':
        in_password = request.form['password']
        in_user = request.form['user']
        login_ret, info = GK1S0001.login_check(in_user, in_password)
        if login_ret == 0:
            session.permanent = True
            session['logged_in'] = True
            session['user_id'] = in_user
            session['authority'] = info
            return redirect(url_for('GK_menu01'))
        else:
            return 'ログイン失敗。ユーザー名またはパスワードが違います。'
    return render_template('GK_login.html')

# メニュー画面
@app.route('/GK_menu01', methods=['GET', 'POST'])
def GK_menu01():
    if not session.get('logged_in'):
        return redirect(url_for('GK_login'))
    
    user_id = session.get('user_id')  # ユーザーIDを取得

    if request.method == 'POST':
        shorikbn = request.form['selection']
        if shorikbn == "practice":
            session.pop(f"user_{user_id}_mondai_list", None)
            session.pop(f"user_{user_id}_ix1", None)
            session[f"user_{user_id}_ix1"] = 0  
            bunya = request.form['bunya']
            mondai = GK1S0001.get_mondai(bunya)
            session[f"user_{user_id}_mondai_list"] = mondai
            return redirect(url_for('GK_practice01'))
    
    return render_template('GK_menu01.html')

# 練習問題（問題表示）
@app.route('/GK_practice01', methods=['GET', 'POST']) 
def GK_practice01():
    if not session.get('logged_in'):
        return redirect(url_for('GK_login'))
    
    user_id = session.get('user_id')

    if f"user_{user_id}_mondai_list" not in session:
        return redirect(url_for('GK_menu01'))
    
    question_index = session[f"user_{user_id}_ix1"]
    question = session[f"user_{user_id}_mondai_list"][question_index][3].replace("\n", "<br>")  # 改行適用

    if request.method == 'POST':
        return redirect(url_for('GK_practice02'))

    return render_template('GK_practice01.html', question=question)

# 練習問題（解答表示）
@app.route('/GK_practice02', methods=['GET', 'POST'])
def GK_practice02():
    if not session.get('logged_in'):
        return redirect(url_for('GK_login'))
    
    user_id = session.get('user_id')

    if f"user_{user_id}_mondai_list" not in session:
        return redirect(url_for('GK_menu01'))
    
    question_index = session[f"user_{user_id}_ix1"]
    question = session[f"user_{user_id}_mondai_list"][question_index][3]
    answer = session[f"user_{user_id}_mondai_list"][question_index][4].replace("\n", "<br>")  # 改行適用

    if request.method == 'POST':
        session[f"user_{user_id}_ix1"] += 1  # **次の問題へ進む**

        if session[f"user_{user_id}_ix1"] >= 5:
            session.pop(f"user_{user_id}_ix1", None)
            session.pop(f"user_{user_id}_mondai_list", None)
            return redirect(url_for('GK_menu01'))

        return redirect(url_for('GK_practice01'))

    return render_template('GK_practice02.html', answer=answer, question=question)

# ログアウト
@app.route('/GK_logout')
def GK_logout():
    user_id = session.get('user_id')
    session.pop('logged_in', None)
    session.pop('authority', None)
    session.pop(f"user_{user_id}_mondai_list", None)
    session.pop('user_id', None)
    session.pop(f"user_{user_id}_ix1", None)
    return redirect(url_for('GK_login'))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)