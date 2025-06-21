#PGM-ID:GK1S0040
#PGM-NAME:GK自家用DB-CNTL
#最終更新日:

import re

import GK0S001D
import GK0S002D

def get_gakusei(id,name, authority):
    gakusei_list = GK0S001D.get_gakusei(id,name)
    if gakusei_list:
        if gakusei_list[2] in [7,8,9] and authority in [0,1,2,3,4,5,6,7,8]:
            err = "当ユーザーの訂正は管理者のみが可能です"
        else:
            err = ""
    else:
        err = "DB相手無し"
    return gakusei_list, err


def get_gakuseiAll():
    status_dict = {
    0: "自家用養成中",
    1: "自家用養成完了",
    2: "自家用取得済み",
    3: "",
    4: "",  # 🔥 値が未設定の場合は空文字
    5: "退部済み",
    6: "学科班",
    7: "学科班主任",
    8: "教官",
    9: "管理者"
    }
    kanri_dict = {
        0 : "テスト有",
        1 : "テスト無"       
    }    
    array = GK0S001D.get_gakuseiAll()
    for ix1 in range(len(array)):
        array[ix1][2] = status_dict[array[ix1][2]]
        array[ix1][3] = kanri_dict[array[ix1][3]]
        array[ix1][6] = timestamp_to_date(array[ix1][6])
    return array


def timestamp_to_date(timestamp):
    if timestamp is None:
        return "未ログイン"
    date_str = timestamp.strftime("%Y/%m/%d/%H:%M")
    return date_str


def check01(id,name):
    if id == "" and name == "":
        err = "学生番号もしくは氏名を入力してください。"
    else:
        err = ""
    return err


def check02(name,status,answer):
    if not name or not status or not answer:
        return "未入力項目があります。"
    if len(name) > 10:
        return "氏名は10字以内で入力してください。"
    try:
        dummy = int(status)
        if len(status) != 1:
            return "状況CDは1桁の数字で入力してください。"
    except ValueError:
        return "状況CDは半角数字で入力してください。"
    try:
        dummy = int(answer)
        if len(answer) != 1:
            return "状況CDは1桁の数字で入力してください。"
    except ValueError:
        return "状況CDは半角数字で入力してください。"
    return ""
    

def check03(pass1,pass2):
    if pass1 != pass2:
        return "１回目と２回目で入力値が異なります。"
    else:
        if len(pass1) < 6 or len(pass1) > 30:
            return "パスワードは６字以上３０字以内で設定してください。"
        if not pass1.isalnum():
            return "パスワードは半角英数字で設定してください。"
        if not any(ix1.isdigit() for ix1 in pass1):
            return "パスワードは文字と数字を組み合わせてください。"
        if not any(ix1.isalpha() for ix1 in pass1):
            return "パスワードは文字と数字を組み合わせてください。"
        return ""


def check04(id, name, status_cd):
    if len(id) != 7:
        return "学籍番号が不正な値です。"
    pattern = r'^\d{2}[A-Z]\d{4}$'
    if not re.match(pattern, id):
        return "学籍番号が不正な値です。"
    if len(name) > 10:
        return "氏名は10字以内で入力してください。"
    if ' ' in name or '　' in name:
        return "氏名は空白を入れずに入力してください。"
    return ""


def update_gakusei(update_gakusei):
    if update_gakusei[2] == 2:
        update_gakusei[3] = 1
    err = GK0S001D.update_gakusei(update_gakusei)
    return ""


def insert_gakusei(id, name, status_cd, kanri_cd):
    err = GK0S001D.insert_gakusei(id, name, status_cd, kanri_cd)
    if err == 3:
        return "入力した学籍番号は登録済みです。"
    return ""    


def update_password(user_id,password):
    err = GK0S001D.update_password(user_id,password)
    return ""        


def get_rireki(user_id):
    list = GK0S002D.get_rireki(user_id)
    number = [4,6,8,10,12]
    result = {
        0 : "未",
        1 : "〇",
        2 : "△",
        3 : "✕"
    }
    cd = {
        0:"未解答",
        9:"解答済"
    }
    if list:
        for ix1 in range(len(list)):
            list[ix1][2] = cd[list[ix1][2]]  
            for ix2 in range(len(number)):
                list[ix1][number[ix2]] = result[list[ix1][number[ix2]]]
        ret_list = sorted(list, key=lambda x: x[1], reverse=True)
        return ret_list

    return []


def get_rirekiAll():
    list = GK0S002D.get_rirekiAll()
    number = [4,6,8,10,12]
    result = {
        0 : "未",
        1 : "〇",
        2 : "△",
        3 : "✕"
    }
    cd = {
        0:"未解答",
        9:"解答済"
    }
    if list:
        for ix1 in range(len(list)):
            list[ix1][2] = cd[list[ix1][2]]  
            for ix2 in range(len(number)):
                list[ix1][number[ix2]] = result[list[ix1][number[ix2]]]
        ret_list = sorted(list, key=lambda x: x[1], reverse=True)
        return ret_list

    return []


def get_gakuseiInfo():
    ret_array = GK0S001D.get_gakuseiInfo()
    return ret_array


def get_gakuseiName(id):
    ret_array = GK0S001D.get_gakuseiName(id)
    return ret_array