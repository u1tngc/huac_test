#PGM-ID:GK1S0043
#PGM-NAME:GK小テスト管理サブ
#最終更新日:2026/09/02

import GK0S091D

def get_testInfo():
    ret_array = GK0S091D.get_testInfo()
    return ret_array

def updateData(akabou,jikayo,info_bef):
    for ix1 in range(len(akabou)):
        if ix1 == 0:
            pass
        else:
            akabou[ix1] = int(akabou[ix1])
            jikayo[ix1] = int(jikayo[ix1])
    if info_bef[1] == akabou and info_bef[0] == jikayo:
        return "更新されていません。", [], []
    info_flg_a = [info_bef[1][0],0,0,0,0,0,0,0]
    info_flg_b = [info_bef[0][0],0,0,0,0,0,0,0]
    update_flg = [0,0]
    for ix1 in range(len(akabou)):
        if ix1 == 0:
            pass
        else:
            if akabou[ix1] != info_bef[1][ix1]:
                info_flg_a[ix1] = 1
                update_flg[1] = 1
            if jikayo[ix1] != info_bef[0][ix1]:
                info_flg_b[ix1] = 1
                update_flg[0] = 1
    info_flg = [info_flg_b,info_flg_a]
    if update_flg[1] == 1:
        #赤帽
        err = GK0S091D.update_test(akabou)
        if err != 0:
            err = "ＤＢ更新時にエラーが発生しました。担当者に連絡してください。"
            return err, [], []
    if update_flg[0] == 1:
        #自家用
        err = GK0S091D.update_test(jikayo)
        if err != 0:
            err = "ＤＢ更新時にエラーが発生しました。担当者に連絡してください。"
            return err, [], []
    info_aft = [jikayo,akabou]
    return "", info_aft, info_flg
