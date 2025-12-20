#PGM-ID:GK1S0101
#PGM-NAME:GK自家用小テストCHK
#最終更新日:2025/12/01

import datetime
import random

import GK0S101D
import GK0S102D
import GK0S11XD
import GK1S0102


def checkDB():
    gakusei_list = GK0S101D.get_gakusei_list()
    sekkyo_list = []
    for ix1 in range(len(gakusei_list)):
        rireki_list = GK0S102D.get_rireki_list(gakusei_list[ix1][0])
        kaitou_umu = 0
        if rireki_list:
            for ix2 in range(len(rireki_list)):
                if rireki_list[ix2][2] == 0:
                    kaitou_umu = kaitou_umu + 1
            if (kaitou_umu >= 2 and gakusei_list[ix1][3] == 1) or (kaitou_umu >= 1 and gakusei_list[ix1][3] == 2):
                sekkyo_list.append([gakusei_list[ix1][0],gakusei_list[ix1][1]])
    GK1S0102.send_mail(sekkyo_list)


def create_rireki():
    gakusei_list = GK0S101D.get_gakusei_list()
    shoriYYYYMMDD = datetime.datetime.today().strftime("%Y%m%d")
    for ix1 in range(len(gakusei_list)):
        print(gakusei_list[ix1])
        mondai_list = []
        if gakusei_list[ix1][3] == 1:
            for bunya in ["法規", "工学", "気象", "情報", "その他"]:
                mondai = GK0S11XD.get_mondai(bunya)
                random_row = random.choice(mondai)
                mondai_list.append(f"{random_row[0]}{random_row[1]}{random_row[2]}")
        elif gakusei_list[ix1][3] == 2:
            mondai = GK0S11XD.get_mondai("赤帽")
            mondai_array = random.sample(mondai,5)
            for ix2 in range(5):
                mondai_list.append(f"{mondai_array[ix2][0]}{mondai_array[ix2][1]}{mondai_array[ix2][2]}")
        GK0S102D.insert_rireki(gakusei_list[ix1][0], shoriYYYYMMDD, mondai_list)
