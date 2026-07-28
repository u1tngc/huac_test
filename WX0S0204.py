# PGM-ID:WX0S0204
# PGM-NAME:[P]WXワーニングチェック
# 更新年月日:2026/04/23

import PK0S0100


def checkWarning(warning_flg, info):
    """
    0:黒表示    1:赤表示    2:橙表示
    """
    warning_info = [0] * len(warning_flg)
    for ix1 in range(len(info)):
        # 強制赤表示
        if warning_flg[ix1] == 10:
            warning_info[ix1] = 1
        # 強制橙表示
        elif warning_flg[ix1] == 11:
            warning_info[ix1] = 2
        # 風速
        elif warning_flg[ix1] == 1:
            ft = int(info[ix1][3:5])
            m = PK0S0100.kt_to_ms(ft)
            if m >= 10:
                warning_info[ix1] = 1
            elif m >= 4:
                warning_info[ix1] = 2
        # 視程SM
        elif warning_flg[ix1] == 2 or warning_flg[ix1] == 5:
            if warning_flg[ix1] == 5:
                vis = info[ix1] + "SM"
            else:
                vis = info[ix1]
            if vis[1:3] == "SM":  # 9SM
                vis_sm = int(vis[0:1])
            elif vis[2:4] == "SM":  # 99SM
                vis_sm = int(vis[0:2])
            elif vis[2:3] == "/" and vis[4:6] == "SM":
                vis_sm = int(vis[0:1]) + int(vis[1:2]) / int(vis[3:4])
            elif vis[5:7] == "SM":  # 9 9/9SM
                vis_sm = int(vis[0:1]) + (int(vis[2:3]) / int(vis[4:5]))
            elif vis[3:5] == "SM":  # 9/9SM
                vis_sm = int(vis[0:1]) / int(vis[2:3])
            vis_m = PK0S0100.statueMile_to_m(vis_sm)
            if vis_m <= 5000:
                warning_info[ix1] = 1
            elif vis_sm != 10 and vis_m <= 10000:
                warning_info[ix1] = 2
        # 雲底
        elif warning_flg[ix1] == 3:
            if info[ix1][3:6] != "///":
                cBase_ft = int(info[ix1][3:6]) * 100
                cBase_m = PK0S0100.ft_to_m(cBase_ft)
                if cBase_m < 600:
                    warning_info[ix1] = 1
                if cBase_m >= 600 and cBase_m < 850:
                    warning_info[ix1] = 2
                if len(info[ix1]) != 6 and warning_info[ix1] == 0:
                    if info[ix1][-2:] == "CB" or info[ix1][-2:] == "TCU":
                        warning_info[ix1] = 2
            elif len(info[ix1]) != 6 and warning_info[ix1] == 0:
                if info[ix1][-2:] == "CB" or info[ix1][-2:] == "TCU":
                    warning_info[ix1] = 2
        # 視程m
        elif warning_flg[ix1] == 4:
            vis = int(info[ix1])
            if vis <= 5000:
                warning_info[ix1] = 1
            elif vis < 9999:
                warning_info[ix1] = 2
        # rmk 雲形
        elif warning_flg[ix1] == 6:
            if info[ix1][1:3] == "CB" or info[ix1][1:4] == "TCU":
                warning_info[ix1] = 1
            elif info[ix1][1:3] == "NS":
                warning_info[ix1] = 2
        # rmk 雲底
        elif warning_flg[ix1] == 7:
            cBase_ft = int(info[ix1][-3:]) * 100
            cBase_m = PK0S0100.ft_to_m(cBase_ft)
            yokushi_flg = 0
            if cBase_m < 600:
                warning_info[ix1] = 1
                yokushi_flg = 1
            if cBase_m >= 600 and cBase_m < 850:
                warning_info[ix1] = 2
                yokushi_flg = 1
            if len(info[ix1]) == 8 and info[ix1][-2:] != "CU" and info[ix1][1:3]:
                warning_info[ix1] = 2
            elif len(info[ix1]) == 9 and yokushi_flg == 0:
                warning_info[ix1] = 2
        else:
            warning_info[ix1] = 0

    return warning_info
