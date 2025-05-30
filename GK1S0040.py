#PGM-ID:GK1S0040
#PGM-NAME:GK自家用DB-CNTL

import GK1S01DB

def get_gakusei(id,name):
    gakusei_list = GK1S01DB.get_gakusei(id,name)
    if gakusei_list:
        err = ""
    else:
        err = "DB相手無し"
    return gakusei_list, err

def get_gakuseiAll():
    array = GK1S01DB.get_gakuseiAll()
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
    

def update_gakusei(update_gakusei):
    err = GK1S01DB.update_gakusei(update_gakusei)
    return ""