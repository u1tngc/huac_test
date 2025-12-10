#PGM-ID:GK1S0040
#PGM-NAME:GK自家用DB-CNTL
#最終更新日:2025/12/11

from datetime import datetime
from zoneinfo import ZoneInfo
import re

import GK0S001D
import GK0S002D
import GK0S031D
import GK0S041D

def get_gakusei(id,authority):
    gakusei_list = GK0S001D.get_gakusei(id)
    if gakusei_list:
        if gakusei_list[2] in [7,8,9] and authority in [0,1,2,3,4,5,6,7,8]:
            err = "当ユーザーの訂正は管理者のみが可能です"
        else:
            err = ""
    else:
        err = "DB相手無し"
    status_dict = {
        0: "学生",
        1: "自家用",
        2: "卒部生",
        3: "退部済",
        4: "",
        5: "",
        6: "学科班",
        7: "学科班主任",
        8: "教官",
        9: "管理者"
        }
    kanri_dict = {
            0 : "出題無",
            1 : "自家用",
            2 : "赤帽"       
    }  
    shikaku_dict = {
            0 : "練許生",
            1 : "自家用",
            2 : "教証"             
    }
    gakusei_list[2] = status_dict[gakusei_list[2]]
    gakusei_list[3] = kanri_dict[gakusei_list[3]]
    gakusei_list[4] = shikaku_dict[gakusei_list[4]]
    return gakusei_list, err


def get_gakuseiAll():
    status_dict = {
        0: "学生",
        1: "自家用",
        2: "卒部生",
        3: "退部済",
        4: "", 
        5: "",
        6: "学科班",
        7: "学科班主任",
        8: "教官",
        9: "管理者"
        }
    kanri_dict = {
            0 : "出題無",
            1 : "自家用",
            2 : "赤帽"       
    }  
    shikaku_dict = {
            0 : "練許生",
            1 : "自家用",
            2 : "教証"             
    }  
    array = GK0S001D.get_gakuseiAll()
    for ix1 in range(len(array)):
        array[ix1][2] = status_dict[array[ix1][2]]
        array[ix1][3] = kanri_dict[array[ix1][3]]
        array[ix1][4] = shikaku_dict[array[ix1][4]]
        array[ix1][6] = timestamp_to_date(array[ix1][6])
    return array


def timestamp_to_date(timestamp):
    if timestamp is None:
        return "未ログイン"
    date_str = timestamp.strftime("%Y/%m/%d/%H:%M")
    return date_str

"""
def check01(id,name):
    if id == "" and name == "":
        err = "学生番号もしくは氏名を入力してください。"
    else:
        err = ""
    return err
"""

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


def check04(id, name, status_cd, shikaku_cd):
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

def check05(old, new):
    if old[4] == "練許生" and new[4] == 1:
        ret_cd = 1
    else:
        ret_cd = 0
    return ret_cd

def check06(kekka):
    if kekka[5] == "" and (kekka[0] != 0 or kekka[1] != 0 or kekka[2] != 0 or kekka[3] != 0 ):
        return "有効期間を入力してください。"
    elif kekka[5] != "" and (kekka[0] == 0 and kekka[1] == 0 and kekka[2] == 0 and kekka[3] == 0 ):
        return "学科試験結果を入力してください。"
    else:
        return ""


def update_gakusei(update_gakusei):
    if update_gakusei[4] == 1:
        update_gakusei[3] = 0
    err = GK0S001D.update_gakusei(update_gakusei)       
    return ""


def insert_gakusei(id, name, status_cd, kanri_cd, shikaku_cd):
    err = GK0S001D.insert_gakusei(id, name, status_cd, kanri_cd, shikaku_cd)
    if err == 3:
        return "入力した学籍番号は登録済みです。"
    if shikaku_cd == 0:
        err = GK0S031D.insert_data(id)
        err = GK0S041D.insert_chkList(id,1)
        err = GK0S041D.insert_chkList(id,2)
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


def get_gakuseiInfo01():
    ret_array = GK0S001D.get_gakuseiInfo01()
    return ret_array

def get_gakuseiInfo00(authority):
    ret_array = GK0S001D.get_gakuseiInfo00(authority)
    return ret_array

def get_gakuseiName(id):
    ret_array = GK0S001D.get_gakuseiName(id)
    return ret_array

def delete_data(id):
    err = GK0S031D.delete_data(id)
    return err

def get_gakkaShiken(id):
    gakkaShiken = GK0S031D.get_gakkaShiken(id)
    return gakkaShiken


def update_gakkaShiken(id,kekka):
    dt = datetime.now(ZoneInfo("Asia/Tokyo"))
    ymd = dt.strftime("%Y%m%d")
    updateInfo=[id,kekka[0],kekka[1],kekka[2],kekka[3],kekka[4],kekka[5], ymd]
    err1 = GK0S031D.update_gakkaShiken(updateInfo)


def get_gakkaShikenAll():
    kekka_dict = {
            0 : "未受験",
            1 : "合格",
            2 : "不合格"             
    }  
    array = GK0S031D.get_gakkaShikenAll()
    for ix1 in range(len(array)):
        array[ix1][1] = kekka_dict[array[ix1][1]]
        array[ix1][2] = kekka_dict[array[ix1][2]]
        array[ix1][3] = kekka_dict[array[ix1][3]]
        array[ix1][4] = kekka_dict[array[ix1][4]]
        array[ix1][5] = kekka_dict[array[ix1][5]]
        if array[ix1][6]:
            array[ix1][6] = f'{array[ix1][6][0:4]}/{array[ix1][6][4:6]}/{array[ix1][6][6:]}'
        if array[ix1][7]:
            array[ix1][7] = f'{array[ix1][7][4:6]}/{array[ix1][7][6:]}'
    return array


def get_chkListAll():
    temp_array1 = GK0S041D.get_chkListAll()
    ret_array = []
    for ix1 in range(0, len(temp_array1) - 1, 2):
        if temp_array1[ix1][0] == temp_array1[ix1 + 1][0]:
            # 1行目: index 0, 2以外を取得（氏名、法規～教官chk）
            row = [v for i, v in enumerate(temp_array1[ix1]) if i not in (0, 2)]
            # 2行目: index 0, 1, 2以外を追加（法規～教官chk）
            row += [v for i, v in enumerate(temp_array1[ix1 + 1]) if i not in (0, 1, 2)]
            ret_array.append(row)    
    return ret_array 


def get_chkList(id):
    temp_array1 = GK0S041D.get_chkList(id)
    ret_array = []
    for ix1 in range(0, len(temp_array1) - 1, 2):
        if temp_array1[ix1][0] == temp_array1[ix1 + 1][0]:
            # 1行目: index 0, 2以外を取得（氏名、法規～教官chk）
            ret_array = [v for i, v in enumerate(temp_array1[ix1]) if i not in (0, 2)]
            # 2行目: index 0, 1, 2以外を追加（法規～教官chk）
            ret_array += [v for i, v in enumerate(temp_array1[ix1 + 1]) if i not in (0, 1, 2)]   
    return ret_array 