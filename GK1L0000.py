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
    if not session.get('logged_in'):
        return redirect(url_for('GK_login'))
    if request.method == 'POST':
        shorikbn = request.form['selection']
        if shorikbn == "practice":
            # 練習問題用のセッション変数を初期化
            session.pop('mondai_list', None)
            session.pop('ix1', None)  # 既存の ix1 を削除
            session['ix1'] = 0        # 新しく 0 で初期化
            bunya = request.form['bunya']
            mondai = GK1S0001.get_mondai(bunya)
            session['mondai_list'] = mondai
            return redirect(url_for('GK_practice01'))  # redirectを使用

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
@app.route('/GK_practice01', methods=['GET', 'POST'])  # メソッド名を大文字に修正
def GK_practice01():
    if not session.get('logged_in'):
        return redirect(url_for('GK_login'))
    
    # mondai_listが存在しない場合はメニューに戻る
    if 'mondai_list' not in session or not session['mondai_list']:
        return redirect(url_for('GK_menu01'))
    
    if request.method == 'POST':
        return redirect(url_for('GK_practice02'))  # redirectを使用
    return render_template('GK_practice01.html')

# 練習問題解答
@app.route('/GK_practice02', methods=['GET', 'POST'])  # メソッド名を大文字に修正
def GK_practice02():
    if not session.get('logged_in'):
        return redirect(url_for('GK_login'))
    
    # ix1が存在しない場合の処理
    if 'ix1' not in session:
        session['ix1'] = 0
    
    session['ix1'] = session['ix1'] + 1
    
    if session['ix1'] >= 5:  # >= を使用してより安全に
        # セッション変数をクリア
        session.pop('ix1', None)
        session.pop('mondai_list', None)
        return redirect(url_for('GK_menu01'))  # redirectを使用
    
    return redirect(url_for('GK_practice01'))  # redirectを使用

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
    #app.run(debug=True)
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)