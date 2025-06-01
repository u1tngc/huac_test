#PGM-ID:GK1S0040
#PGM-NAME:GK自家用DB-CNTL

import re

import GK1S01DB

def get_gakusei(id,name, authority):
    gakusei_list = GK1S01DB.get_gakusei(id,name)
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
    1: "学生チェック済み",
    2: "教官チェック済み",
    3: "自家用取得済み",
    4: "",  # 🔥 値が未設定の場合は空文字
    5: "退部済み",
    6: "学科班",
    7: "学科班主任",
    8: "教官",
    9: "管理者"
    }
    array = GK1S01DB.get_gakuseiAll()
    for ix1 in range(len(array)):
        array[ix1][2] = status_dict[array[ix1][2]]
    return array


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
    err = GK1S01DB.update_gakusei(update_gakusei)
    return ""

def insert_gakusei(id, name, status_cd):
    err = GK1S01DB.insert_gakusei(id, name, status_cd)
    if err == 3:
        return "入力した学籍番号は登録済みです。"
    return ""    


def update_password(user_id,password):
    err = GK1S01DB.update_password(user_id,password)
    return ""        

