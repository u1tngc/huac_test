#PGM-ID:GK1L00000
#PGM-NAME:GK自家用学科ウェブメイン

from flask import Flask, render_template, request, redirect, url_for, session
import os

import GK1S0001

app = Flask(__name__)
app.secret_key = os.urandom(24)  # 毎回ランダムなキーを生成


# ログインページの表示
@app.route('/', methods=['GET', 'POST'])
def GK_login():
    if request.method == 'POST':
        in_password = request.form['password']
        in_user = request.form['user']
        login_ret, info = GK1S0001.login_check(in_user, in_password)
        if login_ret == 0:
            session['logged_in'] = True
            session['user_id'] = in_user
            session['authority'] = info
            return redirect(url_for('GK_menu01'))
        else:
            return 'ログイン失敗。ユーザー名またはパスワードが違います。'
    return render_template('GK_login.html')

# メニュー画面の表示
@app.route('/GK_menu01', methods=['GET', 'POST'])
def GK_menu01():
    session.pop('mondai_list', None)
    session['ix1'] = 0
    if not session.get('logged_in'):
        return redirect(url_for('GK_login'))
    if request.method == 'POST':
        shorikbn = request.form['selection']
        if shorikbn == "practice":
            bunya = request.form['bunya']
            mondai = GK1S0001.get_mondai(bunya)
            session['mondai_list'] = mondai
            return render_template('GK_practice01.html')

        elif shorikbn == "nigate":
            pass
        elif shorikbn == "test":
            pass
        elif shorikbn == "analysis":
            pass
        elif shorikbn == "db":
            pass
        elif shorikbn == "pass":
            pass
    return render_template('GK_menu01.html')

# 練習問題
@app.route('/GK_practice01', methods=['get', 'post'])
def GK_practice01():
    if not session.get('logged_in'):
        return redirect(url_for('GK_login'))
    if request.method == 'POST':
        return render_template('GK_practice02.html')
    return render_template('GK_practice02.html')

# 練習問題解答
@app.route('/GK_practice02', methods=['get', 'post'])
def GK_practice02():
    if not session.get('logged_in'):
        return redirect(url_for('GK_login'))
    session['ix1'] = session['ix1'] + 1
    if session['ix1'] == 5:
        return render_template('GK_menu01.html')
    return render_template('GK_practice01.html')

# ログアウト
@app.route('/GK_logout')
def GK_logout():
    session.pop('logged_in', None)
    session.pop('authority', None)
    session.pop('mondai_list', None)
    session.pop('user_id', None)
    session.pop('ix1', None)
    return redirect(url_for('GK_login'))

if __name__ == "__main__":
    app.run(debug=True)