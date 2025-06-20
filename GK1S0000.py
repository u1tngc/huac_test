#PGM-ID:GK1S0000
#PGM-NAME:GK自家用練習問題・テスト
#最終更新日:

import datetime
from zoneinfo import ZoneInfo
import random

import GK0S001D
import GK0S002D
import GK0S003D
import GK0S01XD

def login_check(user, password):
    user_info = GK0S001D.select_gakusei(user)
    if not user_info:
        return 1,0
    else:
        if user_info[5] == password:
            GK0S001D.update_lastLogin(user)
            return 0,user_info[2]
        else:
            return 2,0
        

def check01(user_id):
    list = GK0S002D.check_rireki(user_id)
    if not list:
        return "現在発生している小テストはありません。", list
    return "", list


def get_mondai(bunya,mondai_num):
    bunya_list = {
        "A":"法規",
        "B":"工学",
        "C":"気象",
        "D":"情報",
        "E":"その他"
    }
    bunya_name = bunya_list[bunya]
    ret_list = GK0S01XD.get_mondai(bunya_name)
    mondai = []
    random_num = [0]

    eof_flg = 0
    random_num[0] = random.randint(0, len(ret_list) - 1)
    mondai.append(ret_list[random_num[0]])
    while eof_flg == 0:
        num = random.randint(0, len(ret_list) - 1)
        if num in random_num:
            pass
        else:
            random_num.append(num)
            mondai.append(ret_list[num])
            if len(mondai) == mondai_num:
                eof_flg = 1
    for ix1 in range(len(mondai)):
        mondai[ix1][3] = mondai[ix1][3].replace("\\n", "\n").replace("\n", "<br>")
        mondai[ix1][4] = mondai[ix1][4].replace("\\n", "\n").replace("\n", "<br>")
    return mondai


def get_testMondai(mondai):
    bunya = mondai[0:1]
    kubun = mondai[1:2]
    mondai_no = mondai[2:]
    ret_list = GK0S01XD.get_test(bunya,kubun,mondai_no)
    ret_list[3] = ret_list[3].replace("\\n", "\n").replace("\n", "<br>")
    ret_list[4] = ret_list[4].replace("\\n", "\n").replace("\n", "<br>")
    return ret_list
    
            
def update_rireki01(user_id, shoriYMD, mondai_no,column, result):
    err = GK0S002D.update_rireki01(user_id, shoriYMD, mondai_no,column, result)


def update_rireki02(user_id, shoriYMD):
    GK0S002D.update_rireki02(user_id, shoriYMD)
    update_kaitoJyokyoCD(user_id)


def update_kaitoJyokyoCD(user_id):
    ret_array = GK0S001D.get_rireki(user_id)
    mikaito = 0
    for ix1 in range(len(ret_array)):
        if ret_array[ix1][2] == 0:
            mikaito = mikaito + 1
    if mikaito < 2:
        ret_cd = GK0S001D.update_kaitoJyokyoCD(user_id)


def update_fukushu(user_id, fukushu):
    today = datetime.datetime.today().astimezone(ZoneInfo("Asia/Tokyo")).strftime("%Y%m%d")
    for ix1 in range(len(fukushu)):
        ret_array = GK0S003D.check_fukushu(user_id, fukushu[ix1])
        if ret_array:
            GK0S003D.update_fukushu(user_id, fukushu[ix1], today)
        else:
            GK0S003D.insert_fukushu(user_id, fukushu[ix1], today)