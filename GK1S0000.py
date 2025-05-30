#PGM-ID:GK1S0000
#PGM-NAME:GK自家用練習問題

import random

import GK1S01DB

def login_check(user, password):
    # ユーザー名の存在チェック
    user_info = GK1S01DB.select_gakusei(user)
    if not user_info:
        return 1,0
    else:
        if user_info[4] == password:
            GK1S01DB.update_lastLogin(user)
            return 0,user_info[2]
        else:
            return 2,0

def get_mondai(bunya):
    """
    bunya_list = {
        "1" : "法規",
        "2" : "気象",
        "3" : "工学",
        "4" : "情報",
        "5" : "その他"
    }
    bunya_name = bunya_list[bunya]
    """
    bunya_name = "法規"
    ret_list = GK1S01DB.get_mondai(bunya_name)
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
            if len(mondai) == 5:
                eof_flg = 1
    for ix1 in range(len(mondai)):
        mondai[ix1][4] = mondai[ix1][4].replace("\\n", "\n").replace("\n", "<br>")
    return mondai
                
    