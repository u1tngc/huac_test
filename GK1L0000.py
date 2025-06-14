#PGM-ID:GK1L0000
#PGM-NAME:GK自家用オンラインメイン
#最終更新日:

from datetime import timedelta
import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
import pytz


import GK1S0000
import GK1S0040


app = Flask(__name__)
app.secret_key = "your_fixed_secret_key_here"  # 固定のキーを使用
app.config['SESSION_PERMANENT'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=10)  # セッション有効期限30分

# ログインページ
@app.route('/', methods=['GET', 'POST'])
def GK_login():
    if request.method == 'POST':
        japan_tz = pytz.timezone('Asia/Tokyo')
        now = datetime.datetime.now(japan_tz)
        if now.weekday() == 6 and now.hour == 0 and now.minute < 60:
            flash("日曜日の午前0時から午前1時まではメンテナンス時間です。")
            return redirect(url_for('GK_login'))
        in_password = request.form['password']
        in_user = request.form['user']
        login_ret, info = GK1S0000.login_check(in_user, in_password)
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
            bunya = request.form['bunya']
            mondai_num = int(request.form['mondai_num'])
            session.pop(f"{user_id}_mondai_list", None)
            session.pop(f"{user_id}_ix1", None)
            session[f"{user_id}_ix1"] = 0  
            session[f'{user_id}_mondaiNum'] = mondai_num
            mondai = GK1S0000.get_mondai(bunya, mondai_num)
            session[f"{user_id}_mondai_list"] = mondai
            return redirect(url_for('GK_practice01'))
        elif shorikbn == "test":
            err, test = GK1S0000.check01(user_id)
            if err:
                flash("今週の小テストは完了しています。")
                return redirect(url_for('GK_menu01'))
            else:
                session.pop(f'{user_id}_testList',None)
                session.pop(f'{user_id}_test',None)
                session[f'{user_id}_test'] = test
                session[f'{user_id}_end'] = 0
            return redirect(url_for('GK_test01'))
        elif shorikbn == "db_show":
            db_kbn = request.form['db_kbn1']
            if db_kbn == "1":
                gakuseiList = GK1S0040.get_gakuseiAll()
                return render_template('GK_db001.html',gakuseiList=gakuseiList)     
            elif db_kbn == "2":
                session.pop(f"{user_id}_gakuseiName", None)
                session.pop(f"{user_id}_gakuseiID", None) 
                session.pop(f"{user_id}_rireki", None)
                if session.get('authority') in [7,8,9]:
                    gakuseiName = GK1S0040.get_gakuseiInfo()
                    session[f"{user_id}_gakuseiName"] = gakuseiName
                    return render_template('GK_db021.html', gakuseiName=gakuseiName) 
                else:
                    array = GK1S0040.get_rireki(user_id)
                    if not array:
                        flash("照会するデータがありません。")
                        return redirect(url_for('GK_menu01')) 
                    return render_template('GK_db020.html',rireki=array)       
        elif shorikbn == "db_edit":
            db_kbn = request.form['db_kbn2']
            if db_kbn == "1":
                return redirect(url_for('GK_db002',err=""))
            elif db_kbn == "2":
                return redirect(url_for('GK_db004',err=""))
        elif shorikbn == "password":
                return redirect(url_for('GK_db010',err=""))

    return render_template('GK_menu01.html')


# 練習問題（問題表示）
@app.route('/GK_practice01', methods=['GET', 'POST']) 
def GK_practice01():
    if not session.get('logged_in'):
        return redirect(url_for('GK_login'))
    user_id = session.get('user_id')
    if f"{user_id}_mondai_list" not in session:
        return redirect(url_for('GK_menu01'))    

    if session[f"{user_id}_ix1"] == session[f'{user_id}_mondaiNum']:
        end = 1
    else:
        end = 0
        question_index = session[f"{user_id}_ix1"]
        question = session[f"{user_id}_mondai_list"][question_index][3].replace("\n", "<br>")  # 改行適用
    if request.method == 'POST':
        return redirect(url_for('GK_practice02', end=end))

    return render_template('GK_practice01.html', question=question)


# 練習問題（解答表示）
@app.route('/GK_practice02', methods=['GET', 'POST'])
def GK_practice02():
    if not session.get('logged_in'):
        return redirect(url_for('GK_login'))   
    user_id = session.get('user_id')
    if f"{user_id}_mondai_list" not in session:
        return redirect(url_for('GK_menu01'))   
     
    question_index = session[f"{user_id}_ix1"]
    question = session[f"{user_id}_mondai_list"][question_index][3].replace("\n", "<br>")  # 改行適用
    answer = session[f"{user_id}_mondai_list"][question_index][4].replace("\n", "<br>")  # 改行適用

    # 最後の問題かどうかを判定
    if session[f"{user_id}_ix1"] + 1 >= session[f'{user_id}_mondaiNum']:
        err = 1  # 最後の問題
    else:
        err = 0  
    if request.method == 'POST':
        session[f"{user_id}_ix1"] += 1  
        return redirect(url_for('GK_practice01'))

    return render_template('GK_practice02.html', answer=answer, question=question, err=err)


# 小テスト問題（問題表示）
@app.route('/GK_test01', methods=['GET', 'POST']) 
def GK_test01():
    if not session.get('logged_in'):
        return redirect(url_for('GK_login'))
    user_id = session.get('user_id')
    if f"{user_id}_test" not in session:
        return redirect(url_for('GK_menu01')) 
    
    err, test = GK1S0000.check01(user_id)      
    session[f'{user_id}_test' ] = test
    numbers = [4, 6, 8, 10, 12]
    column = ["解答結果１", "解答結果２", "解答結果３", "解答結果４", "解答結果５"]
    ix1 = 0
    eof_flg = 0
    while eof_flg == 0:
        if test[numbers[ix1]] == 0:
            mondai = GK1S0000.get_testMondai(test[numbers[ix1]-1])
            mondai.append(column[ix1])
            session[f'{user_id}_testList'] = mondai
            question = mondai[3].replace("\n", "<br>") 
            eof_flg = 1
            if ix1 == 5:
                session[f'{user_id}_end'] = 1
        ix1 = ix1 + 1
        if ix1 == 6:
            eof_flg = 1
    if request.method == 'POST':
        return redirect(url_for('GK_test02'))
    
    return render_template('GK_test01.html', question=question)


# 小テスト問題（解答表示）
@app.route('/GK_test02', methods=['GET', 'POST'])
def GK_test02():
    if not session.get('logged_in'):
        return redirect(url_for('GK_login'))   
    user_id = session.get('user_id')
    if f"{user_id}_test" not in session:
        return redirect(url_for('GK_menu01')) 
       
    question = session[f"{user_id}_testList"][3].replace("\n", "<br>")  # 改行適用
    answer = session[f"{user_id}_testList"][4].replace("\n", "<br>")  # 改行適用

    if request.method == 'POST':
        result = request.form["result"]
        shoriYMD = session[f'{user_id}_test'][1]
        mondai_no = session[f'{user_id}_testList'][0] + session[f'{user_id}_testList'][1] + session[f'{user_id}_testList'][2]
        column =session[f'{user_id}_testList'][5]
        GK1S0000.update_rireki01(user_id, shoriYMD, mondai_no,column, result)
        if column == "解答結果５":
            session[f'{user_id}_end'] = 1
            GK1S0000.update_rireki02(user_id, shoriYMD)
        if session[f'{user_id}_end'] == 1:
            flash("今週のテストは完了しました。")
            return redirect(url_for('GK_menu01'))  
        else:
            return redirect(url_for('GK_test01'))

    return render_template('GK_test02.html', answer=answer, question=question)


#学生管理セグ・照会
@app.route('/GK_db001', methods=['GET', 'POST'])
def GK_db001():
    user_id = session.get('user_id')
    if not session.get('logged_in'):
        return redirect(url_for('GK_login'))
    if not session.get('authority') in [6,7,8,9]:
        return redirect(url_for('GK_menu01'))
    
    return render_template('GK_db001.html')


#学生管理セグ訂正・照会
@app.route('/GK_db002', methods=['GET', 'POST'])
def GK_db002():
    user_id = session.get('user_id')
    if not session.get('logged_in'):
        return redirect(url_for('GK_login'))
    if not session.get('authority') in [7,9]:
        return redirect(url_for('GK_menu01'))
    
    if request.method == 'POST':
        id = request.form['id']
        name = request.form['name']
        err = GK1S0040.check01(id,name)
        if err:
            return render_template('GK_db002.html', err=err)
        gakusei_list, err = GK1S0040.get_gakusei(id,name,session.get('authority'))
        if err:  
            return render_template('GK_db002.html', err=err)
        session[f'{user_id}_gakusei'] = gakusei_list
        return redirect(url_for('GK_db003', gakusei=session.get(f'{user_id}_gakusei'), err=""))
    
    return render_template('GK_db002.html')


#学生管理セグ・訂正
@app.route('/GK_db003', methods=['GET', 'POST'])
def GK_db003():
    user_id = session.get('user_id')
    if not session.get('logged_in'):
        return redirect(url_for('GK_login'))
    if not session.get('authority') in [7,9]:
        return redirect(url_for('GK_menu01'))
    
    if request.method == 'POST':  
        name = request.form['name']
        status_cd = request.form['status_cd']
        kanri_cd = request.form['kanri_cd']
        answer_cd = request.form['answer_cd']
        err = GK1S0040.check02(name, status_cd, answer_cd)
        if err:
            return render_template('GK_db003.html', gakusei=session.get(f'{user_id}_gakusei'), err =err)   
        list = session.get(f'{user_id}_gakusei')
        id = list[0]
        update_gakusei = [id, name, int(status_cd),int(kanri_cd),int(answer_cd)]
        err = GK1S0040.update_gakusei(update_gakusei)
        flash("学生管理セグの訂正が完了しました。")
        return redirect(url_for('GK_menu01'))

    return render_template('GK_db003.html', gakusei=session.get(f'{user_id}_gakusei'), err ="")      


#学生管理セグ・登録
@app.route('/GK_db004', methods=['GET', 'POST'])
def GK_db004():
    user_id = session.get('user_id')
    if not session.get('logged_in'):
        return redirect(url_for('GK_login'))
    if not session.get('authority') in [7,9]:
        return redirect(url_for('GK_menu01'))
    
    if request.method == 'POST':  
        id = request.form['id']
        name = request.form['name']
        status_cd = request.form['status_cd']
        kanri_cd = request.form['kanri_cd']
        err = GK1S0040.check04(id, name, status_cd)
        if err:
            return render_template('GK_db004.html', err =err)   
        err = GK1S0040.insert_gakusei(id, name, status_cd, kanri_cd)
        if err:
            return render_template('GK_db004.html', err =err)   
        flash("学生管理セグの登録が完了しました。")
        return redirect(url_for('GK_menu01'))        

    return render_template('GK_db004.html', err="")  


#パスワード変更
@app.route('/GK_db010', methods=['GET', 'POST'])
def GK_db010():
    user_id = session.get('user_id')
    if not session.get('logged_in'):
        return redirect(url_for('GK_login'))
    
    if request.method == 'POST':  
        pass1 = request.form['pass1']
        pass2 = request.form['pass2']
        err = GK1S0040.check03(pass1, pass2)
        if err:
            return render_template('GK_db010.html', err =err)   
        err = GK1S0040.update_password(user_id,pass1)
        flash(f"{user_id}のパスワード変更が完了しました。")
        return redirect(url_for('GK_menu01'))

    return render_template('GK_db010.html', err ="")  


#履歴管理セグ・照会（学生用）
@app.route('/GK_db020', methods=['GET', 'POST'])
def GK_db020():
    if not session.get('logged_in'):
        return redirect(url_for('GK_login'))
    
    return render_template('GK_db020.html')
    

#履歴管理セグ・照会１（管理者用）
@app.route('/GK_db021', methods=['GET', 'POST'])
def GK_db021():
    user_id = session.get('user_id')
    if not session.get('logged_in'):
        return redirect(url_for('GK_login'))
    if f"{user_id}_gakuseiName" not in session:
        return redirect(url_for('GK_menu01'))  
    if not session.get('authority') in [7,8,9]:
        return redirect(url_for('GK_menu01'))
    
    if request.method == 'POST':
        gakuseiID = request.form['selected_student']
        session[f'{user_id}_gakuseiID'] = gakuseiID
        rireki = GK1S0040.get_rireki(gakuseiID)
        session[f'{user_id}_rireki'] = rireki
        return redirect(url_for('GK_db022'))
    
    return render_template('GK_db021.html', gakuseiName=session.get(f"{user_id}_gakuseiName"))


#履歴管理セグ・照会２（管理者用）
@app.route('/GK_db022', methods=['GET', 'POST'])
def GK_db022():
    user_id = session.get('user_id')
    if not session.get('logged_in'):
        return redirect(url_for('GK_login'))
    if f"{user_id}_gakuseiID" not in session:
        return redirect(url_for('GK_menu01'))
    if not session.get('authority') in [7,8,9]:
        return redirect(url_for('GK_menu01'))  
    
    if request.method == 'POST':
        return redirect(url_for('GK_menu01'))
    gakuseiName = GK1S0040.get_gakuseiName(session.get(f'{user_id}_gakuseiID'))
    rireki = session.get(f'{user_id}_rireki')
    
    return render_template('GK_db022.html', gakuseiName=gakuseiName, rireki=rireki)


# セッションの有効期限をリセット
@app.before_request
def refresh_session():
    session.modified = True  


# ログアウト
@app.route('/GK_logout')
def GK_logout():
    session.clear()
    return redirect(url_for('GK_login'))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)