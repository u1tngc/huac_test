#PGM-ID:GK1L0000
#PGM-NAME:GK自家用オンラインメイン
#最終更新日:2026/01/10

import csv
from datetime import timedelta
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash, Response
import io
import os
from zoneinfo import ZoneInfo


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
        now = datetime.now(ZoneInfo("Asia/Tokyo"))
        if now.weekday() == 6 and now.hour == 0 and now.minute < 15:
            flash("日曜日の午前0時から午前0時15分まではメンテナンス時間です。")
            return redirect(url_for('GK_login'))
        in_password = request.form['password']
        in_user = request.form['user']
        login_ret, info = GK1S0000.login_check(in_user, in_password)
        #if in_user not in ["16A3184","22A0134","22H9509","23H1019","24C3113","24X0077","25X0043","25X0155","99A0000"]:
        #    flash("緊急メンテナンス中")
        #    return redirect(url_for('GK_login'))
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
    #session.pop('_flashes', None)
    rireki_num = GK1S0000.check02(user_id)
    if rireki_num != 0:
        flash("未解答の小テストがあります。")
    init01(user_id)
    if request.method == 'POST':
        init07(user_id)
        shorikbn = request.form['selection']
        GK1S0000.print_seg(shorikbn, session.get('user_id'))
        if shorikbn == "practice":
            bunya = request.form['bunya']
            mondai_num = int(request.form['mondai_num'])
            init02(user_id)
            GK1S0040.insertLog(user_id,"A001",bunya)
            if bunya == "Z":
                print(f"学籍番号：{session.get('user_id')}")
            session[f"{user_id}_fukushu"] = []
            session[f"{user_id}_ix1"] = 0  
            session[f'{user_id}_mondaiNum'] = mondai_num
            mondai = GK1S0000.get_mondai(bunya, mondai_num)
            session[f"{user_id}_mondai_list"] = mondai
            return redirect(url_for('GK_practice01'))
        elif shorikbn == "test":
            err, test = GK1S0000.check01(user_id)
            if err:
                session.pop('_flashes', None)
                flash("今週の小テストは完了しています。")
                return redirect(url_for('GK_menu01'))
            else:
                init03(user_id)
                session[f'{user_id}_test'] = test
                session[f'{user_id}_end'] = 0
                GK1S0040.insertLog(user_id,"A011",bunya)
            return redirect(url_for('GK_test01'))
        elif shorikbn == "fukushu":
            init05(user_id)
            fukushu_num = request.form['fukushu_num']
            fukushu_kbn = request.form['kbn']
            fukushu_list, fukushu_num = GK1S0000.get_fukushuNum(user_id, fukushu_num, fukushu_kbn)
            if fukushu_list:
                session[f"{user_id}_fukushuList"] = fukushu_list
                session[f"{user_id}_fukushuNum"] = fukushu_num
                session[f"{user_id}_fukushu_ix1"] = 0
                session[f"{user_id}_fukushu_eof"] = 0
                GK1S0040.insertLog(user_id,"A021",fukushu_kbn)
                return redirect(url_for('GK_fukushu01', err=""))
            else:
                flash("復習対象の問題がありません。")
                return redirect(url_for('GK_menu01'))
            """    
            elif shorikbn == "nigate":
                ret_cd = GK1S0000.check_nigate(user_id)
                return render_template('GK_nigate01')
            """
        elif shorikbn == "db_show":
            db_kbn = request.form['db_kbn1']
            if db_kbn == "1":
                GK1S0040.insertLog(user_id,"B001","")
                gakuseiList = GK1S0040.get_gakuseiAll()
                return render_template('GK_db001.html',gakuseiList=gakuseiList)     
            elif db_kbn == "2":
                init04(user_id)
                GK1S0040.insertLog(user_id,"B011","")
                if session.get('authority') in [7,8,9]:
                    gakuseiName = GK1S0040.get_gakuseiInfo01()
                    session[f"{user_id}_gakuseiName"] = gakuseiName
                    return render_template('GK_db021.html', gakuseiName=gakuseiName) 
                else:
                    array = GK1S0040.get_rireki(user_id)
                    if not array:
                        flash("照会するデータがありません。")
                        return redirect(url_for('GK_menu01')) 
                    return render_template('GK_db020.html',rireki=array)    
            elif db_kbn == "3":
                GK1S0040.insertLog(user_id,"B021","")
                gakkaShikenList = GK1S0040.get_gakkaShikenAll()
                session[f"{user_id}_gakkaShikenList"] = gakkaShikenList
                return render_template('GK_db031.html',gakkaShikenList=gakkaShikenList)  
            elif db_kbn == "4":
                GK1S0040.insertLog(user_id,"B031","")
                if session.get('authority') in [6,7,8,9]:
                    chklist = GK1S0040.get_chkListAll()
                    return render_template('GK_db041.html',chklist=chklist)  
                else:
                    id = session.get('user_id')
                    chklist = GK1S0040.get_chkList(id,1)
                    return render_template('GK_db042.html',chklist=chklist)    
            elif db_kbn == "5":
                GK1S0040.insertLog(user_id,"B004","")
                wk51studentList = GK1S0040.get_renkyosei()
                session[f"{user_id}_wk51studentList"] = wk51studentList
                return render_template('GK_db051.html', studentList=wk51studentList,err1="")
            elif db_kbn == "6":
                GK1S0040.insertLog(user_id,"B005","")
                wk53yoseiSumAll = GK1S0040.get_yoseiSumAll()
                return render_template('GK_db053.html', wk53yoseiSumAll=wk53yoseiSumAll) 
        elif shorikbn == "db_edit":
            db_kbn = request.form['db_kbn2']
            if db_kbn == "1":
                GK1S0040.insertLog(user_id,"C001","")
                gakuseiData = GK1S0040.get_gakuseiInfo00(session.get('authority'))
                session[f"{user_id}_gakuseiData"] = gakuseiData
                return render_template('GK_db002.html', gakuseiData=gakuseiData, err1="") 
            elif db_kbn == "2":
                GK1S0040.insertLog(user_id,"C011","")
                return redirect(url_for('GK_db004',err=""))
            elif db_kbn == "3":
                GK1S0040.insertLog(user_id,"C021","")
                gakkaShiken_data = GK1S0040.get_gakkaShiken(session.get('user_id'))
                if gakkaShiken_data:
                    session[f"{user_id}_gakkaShiken_data"] = gakkaShiken_data
                    date_str = gakkaShiken_data[6]
                    if date_str == None:
                        limitdate = ""
                    else:
                        limitdate = f"{date_str[0:4]}-{date_str[4:6]}-{date_str[6:8]}"
                    session[f"{user_id}_limitdate"] = limitdate
                    return render_template('GK_db032.html', gakkaShiken1=gakkaShiken_data,limitdate1=limitdate, gakkaShiken2=gakkaShiken_data,limitdate2=limitdate, err1="") 
                else:
                    flash("学科試験のデータがありません。学科班に確認してください。")
                    return redirect(url_for('GK_menu01'))               
            elif db_kbn == "4":
                GK1S0040.insertLog(user_id,"C031","")
                gakuseiCHK = GK1S0040.get_renkyosei()
                session[f"{user_id}_gakuseiCHK"] = gakuseiCHK
                return render_template('GK_db043.html', gakuseiCHK=gakuseiCHK, err1="") 
            elif db_kbn == "5":
                GK1S0040.insertLog(user_id,"C041","")
                wk54yoseiKamoku = GK1S0040.get_yoseiKamokuAll()
                wk54yoseiStudent = GK1S0040.get_renkyosei()
                session[f"{user_id}_wk54yoseiKamoku"] = wk54yoseiKamoku
                session[f"{user_id}_wk54yoseiStudent"] = wk54yoseiStudent
                return render_template('GK_db054.html', wk54yoseiKamoku=wk54yoseiKamoku, wk54yoseiStudent=wk54yoseiStudent, err1="")
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
        session[f'{user_id}_mondaiNo'] = session[f"{user_id}_mondai_list"][question_index][0] + session[f"{user_id}_mondai_list"][question_index][1] + session[f"{user_id}_mondai_list"][question_index][2]
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
        result = request.form["result"]
        if result != "1":
            if session[f'{user_id}_mondaiNo'][0:1] == "Z":
                GK1S0000.update_fukushu(user_id, session[f'{user_id}_mondaiNo'], 3)         
            else:
                GK1S0000.update_fukushu(user_id, session[f'{user_id}_mondaiNo'], 2)
            session.pop(f"{user_id}_fukushu", None)
        if err == 0:
            return redirect(url_for('GK_practice01'))
        else:
            return redirect(url_for('GK_menu01'))  # 最後の問題の場合はメニューに戻る

    return render_template('GK_practice02.html', answer=answer, question=question, err=err)


# 復習問題（問題表示）
@app.route('/GK_fukushu01', methods=['GET', 'POST']) 
def GK_fukushu01():
    if not session.get('logged_in'):
        return redirect(url_for('GK_login'))
    user_id = session.get('user_id')
    if f"{user_id}_fukushuList" not in session:
        return redirect(url_for('GK_menu01'))    

    if session[f"{user_id}_fukushu_ix1"] + 1 == session[f'{user_id}_fukushuNum']:
        err = "この問題が最終問題です。"
        session[f"{user_id}_fukushu_eof"] = 1
    else:
        err = ""
    question_index = session[f"{user_id}_fukushu_ix1"]
    session[f'{user_id}_fukushuNo'] = session[f"{user_id}_fukushuList"][question_index][0] + session[f"{user_id}_fukushuList"][question_index][1] + session[f"{user_id}_fukushuList"][question_index][2]
    question = session[f"{user_id}_fukushuList"][question_index][3].replace("\n", "<br>")  # 改行適用
    if request.method == 'POST':
        return redirect(url_for('GK_fukushu02', err=err))

    return render_template('GK_fukushu01.html', question=question)


# 復習問題（解答表示）
@app.route('/GK_fukushu02', methods=['GET', 'POST'])
def GK_fukushu02():
    if not session.get('logged_in'):
        return redirect(url_for('GK_login'))   
    user_id = session.get('user_id')
    if f"{user_id}_fukushuList" not in session:
        return redirect(url_for('GK_menu01'))   
    if session[f"{user_id}_fukushu_eof"] == 0:
        err = ""
    else:
        err = "この問題が最終問題です。"     
    question_index = session[f"{user_id}_fukushu_ix1"]
    question = session[f"{user_id}_fukushuList"][question_index][3].replace("\n", "<br>")  # 改行適用
    answer = session[f"{user_id}_fukushuList"][question_index][4].replace("\n", "<br>")  # 改行適用
    if request.method == 'POST':
        session[f"{user_id}_fukushu_ix1"] += 1 
        result = request.form["result"]
        GK1S0000.update_fukushu1(user_id,session[f'{user_id}_fukushuNo'],result)
        if session[f"{user_id}_fukushu_eof"] == 0:
            return redirect(url_for('GK_fukushu01'))
        else:
            init05(user_id)
            return redirect(url_for('GK_menu01'))  # 最後の問題の場合はメニューに戻る

    return render_template('GK_fukushu02.html', answer=answer, question=question,err=err)


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
        if result != "1":
            GK1S0000.update_fukushu_test(user_id, mondai_no, 1)
        if column == "解答結果５":
            session[f'{user_id}_end'] = 1
            timezone = datetime.now(ZoneInfo("Asia/Tokyo"))
            kaito_ymd = timezone.strftime('%Y%m%d%H%M')
            GK1S0000.update_rireki02(user_id, shoriYMD, kaito_ymd)
        if session[f'{user_id}_end'] == 1:
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
        gakuseiInfo = request.form['selected_studentInfo']
        session[f'{user_id}_gakuseiInfo'] = gakuseiInfo
        ret_gakusei, err = GK1S0040.get_gakusei(gakuseiInfo,session.get('authority'))
        session[f'{user_id}_gakusei'] = ret_gakusei
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
        shikaku_cd = request.form['shikaku_cd']
        err = GK1S0040.check02(name, status_cd, shikaku_cd)
        if err:
            return render_template('GK_db003.html', gakusei=session.get(f'{user_id}_gakusei'), err =err)   
        list = session.get(f'{user_id}_gakusei')
        id = list[0]
        update_gakusei = [id, name, int(status_cd),int(kanri_cd),int(shikaku_cd)]
        err = GK1S0040.update_gakusei(update_gakusei)
        change_chk = GK1S0040.check05(list, update_gakusei)
        if change_chk == 1:
            err1 = GK1S0040.delete_data(id)
        err = f"[{name}]の訂正が完了しました。"
        gakuseiData = session.get(f"{user_id}_gakuseiData")
        return render_template('GK_db002.html', gakuseiData=gakuseiData, err1=err) 
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
        status_cd = int(request.form['status_cd'])
        kanri_cd = int(request.form['kanri_cd'])
        shikaku_cd = int(request.form['shikaku_cd'])
        err = GK1S0040.check04(id, name, status_cd, shikaku_cd)
        if err:
            return render_template('GK_db004.html', err =err)   
        err = GK1S0040.insert_gakusei(id, name, status_cd, kanri_cd, shikaku_cd)
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


#学科試験管理セグ・照会
@app.route('/GK_db031', methods=['GET', 'POST'])
def GK_db031():
    user_id = session.get('user_id')
    if not session.get('logged_in'):
        return redirect(url_for('GK_login'))
    if not session.get('authority') in [6,7,8,9]:
        return redirect(url_for('GK_menu01'))
    if f"{user_id}_gakkaShikenList" not in session:
        return redirect(url_for('GK_menu01'))
    if request.method == 'POST':
        gakkaShikenList = session.get(f'{user_id}_gakkaShikenList')
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['氏名', '法規', '工学', '気象', '航法', '航特', '有効期間', '更新日'])
        for row in gakkaShikenList:
            writer.writerow(row[:8])
        csv_data = '\ufeff' + output.getvalue()
        output.close()
        return Response(
            csv_data.encode('utf-8'),
            mimetype='text/csv; charset=utf-8',
            headers={'Content-Disposition': "attachment; filename*=UTF-8''%E5%AD%A6%E7%A7%91%E8%A9%A6%E9%A8%93%E7%B5%90%E6%9E%9C.csv"}
        )
    
    gakkaShikenList = session.get(f'{user_id}_gakkaShikenList')
    return render_template('GK_db031.html', gakkaShikenList=gakkaShikenList)


#学科試験管理セグ・訂正
@app.route('/GK_db032', methods=['GET', 'POST'])
def GK_db032():
    user_id = session.get('user_id')
    if not session.get('logged_in'):
        return redirect(url_for('GK_login'))
    if request.method == 'POST':  
        limitDate = request.form['limit']
        kekka = [int(request.form['hoki']), int(request.form['kogaku']), int(request.form['kisho']), int(request.form['koho']),int(request.form['kotoku']), limitDate.replace("-", "")]
        err = GK1S0040.check06(kekka)
        gakkaShiken_old = session.get(f'{user_id}_gakkaShiken_data')
        limitdate_old =session.get(f'{user_id}_limitdate')
        gakkaShiken_new = [gakkaShiken_old[0],kekka[0],kekka[1],kekka[2],kekka[3],kekka[4],gakkaShiken_old[6]]
        limitdate_new = limitDate
        if err:
            return render_template('GK_db032.html', gakkaShiken1=gakkaShiken_old,limitdate1=limitdate_old, gakkaShiken2=gakkaShiken_new,limitdate2=limitdate_new,err=err)   
        err1 = GK1S0040.update_gakkaShiken(user_id,kekka)
        session.pop('_flashes', None)
        flash("学科試験結果の訂正が完了しました。")
        init06(user_id)
        return redirect(url_for('GK_menu01')) 
    return render_template('GK_db032.html', gakusei=session.get(f'{user_id}_gakusei'), err ="")      


#各種CHK管理セグ・照会（管理者用）
@app.route('/GK_db041', methods=['GET', 'POST'])
def GK_db041():
    user_id = session.get('user_id')
    if not session.get('logged_in'):
        return redirect(url_for('GK_login'))
    if not session.get('authority') in [6,7,8,9]:
        return redirect(url_for('GK_menu01'))
    return render_template('GK_db041.html')


#各種CHK管理セグ・照会（練許生用）
@app.route('/GK_db042', methods=['GET', 'POST'])
def GK_db042():
    user_id = session.get('user_id')
    if not session.get('logged_in'):
        return redirect(url_for('GK_login'))
    if not session.get('authority') in [0]:
        return redirect(url_for('GK_menu01'))
    return render_template('GK_db042.html')

#各種CHK管理セグ訂正・照会
@app.route('/GK_db043', methods=['GET', 'POST'])
def GK_db043():
    user_id = session.get('user_id')
    if not session.get('logged_in'):
        return redirect(url_for('GK_login'))
    if not session.get('authority') in [6,7,9]:
        return redirect(url_for('GK_menu01'))
    if request.method == 'POST':
        chk_id = request.form['selected_chk']
        ret_array, err = GK1S0040.get_gakusei(chk_id,session.get('authority'))
        session[f'{user_id}_chk_id'] = chk_id
        session[f'{user_id}_chk_name'] = ret_array[1]
        chkData = GK1S0040.get_chkList(chk_id,2)
        if chkData:
            for ix1 in range(len(chkData)):
                if ix1 in [1,2,3,4,5,6]:
                    if chkData[ix1] == "":
                        chkdate = ""
                    else:
                        chkdate = f"{chkData[ix1][0:4]}-{chkData[ix1][4:6]}-{chkData[ix1][6:8]}"
                    chkData[ix1] = chkdate
            session[f"{user_id}_chkData1"] = chkData
            return render_template('GK_db044.html', chkData1=chkData, chkData2=chkData,stu_name=ret_array[1],err1="")
        else:
            flash("各種CHKのデータがありません。学科班に確認してください。")    
            return redirect(url_for('GK_menu01'))   
    return render_template('GK_db043.html')


#各種CHK管理セグ訂正・訂正
@app.route('/GK_db044', methods=['GET', 'POST'])
def GK_db044():
    user_id = session.get('user_id')
    if not session.get('logged_in'):
        return redirect(url_for('GK_login'))
    if not session.get('authority') in [6,7,9]:
        return redirect(url_for('GK_menu01'))
    if request.method == 'POST':
        hoki_date = request.form['hoki_date']
        kisho_date = request.form['kishou_date']
        kogaku_date = request.form['kogaku_date']
        joho_date = request.form['joho_date']
        gakuseiCHK_date = request.form['gakuseiCHK_date']
        kyoukanCHK_date = request.form['kyoukanCHK_date']
        hoki_name = request.form['hoki_name']
        kisho_name = request.form['kisho_name']
        kogaku_name = request.form['kogaku_name']
        joho_name = request.form['joho_name']
        gakuseiCHK_name = request.form['gakuseiCHK_name']
        kyoukanCHK_name = request.form['kyoukanCHK_name']
        date_array = [hoki_date, kisho_date, kogaku_date, joho_date, gakuseiCHK_date, kyoukanCHK_date]
        name_array = [hoki_name, kisho_name, kogaku_name, joho_name, gakuseiCHK_name, kyoukanCHK_name]
        bef_array = session.get(f"{user_id}_chkData1")
        err = GK1S0040.check07(date_array, name_array)
        if not err:
            err = GK1S0040.check08(date_array, session.get(f'{user_id}_chk_id'))
        kekka = [bef_array[0], hoki_date, kisho_date, kogaku_date, joho_date, gakuseiCHK_date, 
                 kyoukanCHK_date,hoki_name, kisho_name, kogaku_name, joho_name, gakuseiCHK_name, kyoukanCHK_name]
        if err:
            return render_template('GK_db044.html', chkData1=bef_array, chkData2=kekka,stu_name=session.get(f'{user_id}_chk_name'),err1=err)
        else:
            aft_array1 = [session.get(f'{user_id}_chk_id'), 1,hoki_date.replace("-", ""), kisho_date.replace("-", ""), 
                          kogaku_date.replace("-", ""), joho_date.replace("-", ""), gakuseiCHK_date.replace("-", ""), kyoukanCHK_date.replace("-", "")]
            aft_array2 = [session.get(f'{user_id}_chk_id'), 2,hoki_name, kisho_name, kogaku_name, joho_name, gakuseiCHK_name, kyoukanCHK_name]
            err = GK1S0040.update_chkList(aft_array1, aft_array2)
            err1 = f"{session.get(f'{user_id}_chk_name')}の訂正が完了しました。"
            return render_template('GK_db043.html', gakuseiCHK=session.get(f"{user_id}_gakuseiCHK"), err1=err1) 


#養成状況管理セグ照会１
@app.route('/GK_db051', methods=['GET', 'POST'])
def GK_db051():
    user_id = session.get('user_id')
    if not session.get('logged_in'):
        return redirect(url_for('GK_login'))
    if request.method == 'POST':
        wk51gakuseiID = request.form['selected_studentInfo']
        wk51gakuseiName = GK1S0040.get_gakuseiName(wk51gakuseiID)
        session[f'{user_id}_wk51gakuseiID'] = wk51gakuseiID
        session[f'{user_id}_wk51gakuseiName'] = wk51gakuseiName
        wk51yoseiJokyo, wk51sum = GK1S0040.get_yoseiJokyo(wk51gakuseiID)
        if not wk51yoseiJokyo:
            err = "照会するデータがありません。"
            return render_template('GK_db051.html', studentList=session.get(f"{user_id}_wk51studentList"), err1=err) 
        session[f'{user_id}_wk51yoseiJokyo'] = wk51yoseiJokyo
        session[f'{user_id}_wk51sum'] = wk51sum
        return redirect(url_for('GK_db052'))
    return render_template('GK_db051.html', studentList=session.get(f"{user_id}_wk51studentList"), err1="")

#養成状況管理セグ照会２
@app.route('/GK_db052', methods=['GET', 'POST'])
def GK_db052():
    user_id = session.get('user_id')
    if not session.get('logged_in'):
        return redirect(url_for('GK_login'))
    if not session.get('authority') in [0,1,6,7,8,9]:
        return redirect(url_for('GK_menu01'))
    
    return render_template('GK_db052.html',
                           wk51yoseiJokyo=session.get(f'{user_id}_wk51yoseiJokyo'),
                           gakuseiName=session.get(f'{user_id}_wk51gakuseiName'),
                           wk51sum=session.get(f'{user_id}_wk51sum'))

#養成状況管理セグ一括照会
@app.route('/GK_db053', methods=['GET', 'POST'])
def GK_db053():
    user_id = session.get('user_id')
    if not session.get('logged_in'):
        return redirect(url_for('GK_login'))
    if not session.get('authority') in [6,7,8,9]:
        return redirect(url_for('GK_menu01'))
    
    if request.method == 'POST':
        csv_data = GK1S0040.get_yoseiAllDataForCSV()
        if not csv_data:
            flash("データの取得に失敗しました。")
            return redirect(url_for('GK_menu01'))  
        output = io.StringIO()
        writer = csv.writer(output)
        for row in csv_data:
            writer.writerow(row)
        csv_content = '\ufeff' + output.getvalue()
        output.close()
        return Response(
            csv_content.encode('utf-8'),
            mimetype='text/csv; charset=utf-8',
            headers={'Content-Disposition': "attachment; filename*=UTF-8''%E9%A4%8A%E6%88%90%E7%8A%B6%E6%B3%81%E4%B8%80%E8%A6%A7.csv"}
        )
    return render_template('GK_db053.html')

#養成状況管理セグ更新１
@app.route('/GK_db054', methods=['GET', 'POST'])
def GK_db054():
    user_id = session.get('user_id')
    if not session.get('logged_in'):
        return redirect(url_for('GK_login'))
    if not session.get('authority') in [1,6,7,9]:
        return redirect(url_for('GK_menu01'))
    if request.method == 'POST':
        yoseiKamoku = request.form['yoseiKamoku']
        yoseiStudent = request.form.getlist('yoseiStudent')
        yoseiDate = request.form['yoseiDate']
        if yoseiDate:
            yoseiDate = yoseiDate.replace("-", "")
        wk54updateInfo = GK1S0040.get_youseiJyokyo(yoseiKamoku, yoseiStudent, yoseiDate)
        session[f'{user_id}_wk54updateInfo'] = wk54updateInfo
        session[f'{user_id}_wk54yoseicd'] = yoseiKamoku
        return render_template('GK_db055.html', wk54updateInfo=wk54updateInfo, err1="")
    return render_template('GK_db054.html', wk54yoseiKamoku=session.get(f'{user_id}_wk54yoseiKamoku'), wk54yoseiStudent=session.get(f'{user_id}_wk54yoseiStudent'), err1="")

#養成状況管理セグ更新２
@app.route('/GK_db055', methods=['GET', 'POST'])
def GK_db055():
    user_id = session.get('user_id')
    if not session.get('logged_in'):
        return redirect(url_for('GK_login'))
    if not session.get('authority') in [1,6,7,9]:
        return redirect(url_for('GK_menu01'))
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'back':
            return render_template('GK_db054.html', wk54yoseiKamoku=session.get(f'{user_id}_wk54yoseiKamoku'), wk54yoseiStudent=session.get(f'{user_id}_wk54yoseiStudent'), err1="")
        else:
            wk54updateInfo = session.get(f'{user_id}_wk54updateInfo')
            err = GK1S0040.update_yoseiJokyo(wk54updateInfo,session.get(f'{user_id}_wk54yoseicd'))
        if err:
            return render_template('GK_db055.html', wk54updateInfo=wk54updateInfo, err1=err)
        session.pop(f'{user_id}_wk54updateInfo', None)
        session.pop(f'{user_id}_wk54yoseicd', None)
        err1 = "養成状況の更新が完了しました。"
        return render_template('GK_db054.html', wk54yoseiKamoku=session.get(f'{user_id}_wk54yoseiKamoku'), wk54yoseiStudent=session.get(f'{user_id}_wk54yoseiStudent'), err1=err1)
    return render_template('GK_db055.html', wk54updateInfo=session.get(f'{user_id}_wk54updateInfo'), err1="")


# セッションの有効期限をリセット
@app.before_request
def refresh_session():
    session.modified = True  


# ログアウト
@app.route('/GK_logout')
def GK_logout():
    session.clear()
    return redirect(url_for('GK_login'))


def init01(user_id):
    session.pop(f"{user_id}_fukushu", None)


def init02(user_id):
    session.pop(f"{user_id}_mondai_list", None)
    session.pop(f"{user_id}_ix1", None)
    session.pop(f"{user_id}_fukushu", None)
    session.pop(f"{user_id}_mondaiNum", None)
    session.pop(f"{user_id}_mondaiNo", None)


def init03(user_id):
    session.pop(f"{user_id}_testList", None)
    session.pop(f"{user_id}_test", None)
    session.pop(f"{user_id}_end", None) 


def init04(user_id):
    session.pop(f"{user_id}_gakuseiName", None)
    session.pop(f"{user_id}_gakuseiID", None)
    session.pop(f"{user_id}_rireki", None)


def init05(user_id):
    session.pop(f"{user_id}_fukushuList", None)
    session.pop(f"{user_id}_fukushuNum", None)
    session.pop(f'{user_id}_fukushuNo', None)
    session.pop(f'{user_id}_fukushu_eof', None)


def init06(user_id):
    session.pop(f"{user_id}_gakkaShiken_data", None)
    session.pop(f"{user_id}_limitdate", None)


def init07(user_id):
    session.pop(f"{user_id}_wk51gakuseiID", None)
    session.pop(f"{user_id}_wk51gakuseiName", None)
    session.pop(f"{user_id}_wk51yoseiJokyo", None)
    session.pop(f"{user_id}_wk51sum", None)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)

