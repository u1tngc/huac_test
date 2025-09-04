#PGM-ID:GK1S0000
#PGM-NAME:GK自家用練習問題・テスト
#最終更新日:2025/06/25

from datetime import datetime, timedelta
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
        "E":"その他",
        "X":"赤帽"
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


def update_rireki02(user_id, shoriYMD, kaito_ymd):
    GK0S002D.update_rireki02(user_id, shoriYMD, kaito_ymd)
    update_kaitoJyokyoCD(user_id)


def update_kaitoJyokyoCD(user_id):
    ret_array = GK0S002D.get_rireki(user_id)
    mikaito = 0
    for ix1 in range(len(ret_array)):
        if ret_array[ix1][2] == 0:
            mikaito = mikaito + 1
    if mikaito < 2:
        ret_cd = GK0S001D.update_kaitoJyokyoCD(user_id)


def update_fukushu(user_id, fukushu):
    today = datetime.now(ZoneInfo("Asia/Tokyo")).strftime("%Y%m%d")
    for ix1 in range(len(fukushu)):
        ret_array = GK0S003D.check_fukushu(user_id, fukushu[ix1])
        if ret_array:
            GK0S003D.update_fukushu(user_id, fukushu[ix1], today)
        else:
            GK0S003D.insert_fukushu(user_id, fukushu[ix1], today)


def get_fukushuNum(user_id,num):
    fukushu_array = GK0S003D.select_fukushu(user_id)
    random.shuffle(fukushu_array)
    if len(fukushu_array) < int(num):
        ret_num = len(fukushu_array)
    else:
        ret_num = int(num)
    ret_array = []
    for ix1 in range(ret_num):
        array = GK0S01XD.get_test(fukushu_array[ix1][1], fukushu_array[ix1][2], fukushu_array[ix1][3])
        array[3] = array[3].replace("\\n", "\n").replace("\n", "<br>")
        array[4] = array[4].replace("\\n", "\n").replace("\n", "<br>")
        ret_array.append(array)
    return ret_array, ret_num


def update_fukushu1(user_id, fukushuNo, result):
    today = datetime.now(ZoneInfo("Asia/Tokyo")).strftime("%Y%m%d")
    if result == "1":
        fukushu = GK0S003D.check_shoriymd(user_id, fukushuNo)
        bef_date = datetime.strptime(today, "%Y%m%d")
        aft_date = datetime.strptime(fukushu[4], "%Y%m%d")
        days_difference = (bef_date - aft_date).days
        if days_difference >= 10:   
            dummy = GK0S003D.delete_fukushu(user_id, fukushuNo)
    else:
        dummy = GK0S003D.update_fukushu(user_id, fukushuNo, today)

"""
    def check_nigate(use_id):
        array = GK0S002D.check_nigate(use_id)
        if array:
            ret_array = []
            for ix1 in range(len(array)):
                eof_sw = 0
                ix2 = 3
                while eof_sw == 0:
                    if array[ix1][ix2 + 1] in [2,3]:
                        ret_array.append([array[ix1][ix2][0:1],array[ix1][ix2][1:2]])
                    ix2 = ix2 + 2
                    if ix2 >= 12:
                        eof_sw = 1
            return ret_array
        else:
            return []


    def create_nigate(mondaiNo):
        mondai = []
        for ix1 in range(len(mondaiNo)):
            ret_array = GK0S01XD.get_nigateMondai(mondaiNo[ix1][0], mondaiNo[ix1][1])
            print(ret_array)
            
        return mondai
"""

#ret = check_nigate("22N2047")
#create_nigate(ret)