#PGM-ID:WX0S0203
#PGM-NAME:[P]WX横田METAR国内記事取得

class WX_MARK:
    wx_kigo = {
        'DZ': '霧雨',
        'RA': '雨',
        'SN': '雪',
        'SG': '霧雪',
        'PL': '凍雨',
        'GR': 'ひょう',
        'GS': 'あられ',
        'BR': 'もや（1000m≦X≦5000m）',
        'FG': '霧（1000m＜X）',
        'FU': '煙',
        'VA': '火山灰',
        'DU': 'じん',
        'SA': '砂',
        'HZ': '煙霧',
        'PO': '塵旋風',
        'SQ': 'スコール',
        'FC': 'ろうと雲',
        'SS': '砂塵嵐（sand）',
        'DS': '砂塵嵐（dust）',
        'TS': '雷'
    }
    wx_with = {
        'VC': '付近に',
        'MI': '地',
        'BC': '散在',
        'PR': '部分',
        'DR': '低い',
        'BL': '高い',
        'SH': '驟雨性の',
        'TS': '雷',
        'FZ': '着氷性'
    }

def get_rmkwx(info, num, jTimeH):
    info = info + '$'
    wx_info = []
    if num == 0:
        num = num + 1
    wx_keta = []
    wx_keta = wx_keta_check(info, wx_keta)
    wx_time = [] * len(wx_keta)
    wx_time = wx_time_check(info, wx_time, wx_keta)
    wx_info, num = get_wx(wx_keta,wx_time, info, num, jTimeH)

    return wx_info, num

def wx_keta_check(info,wx_keta):
    eof_flg = 0
    ix1 = 0
    while eof_flg == 0:
        dummy1 = WX_MARK.wx_kigo.get(info[ix1:ix1+2])
        dummy2 = WX_MARK.wx_with.get(info[ix1:ix1+2])
        if dummy1 is not None or dummy2 is not None:
            dummy3 = ""
            dummy4 = ""
            if len(info) >= ix1 + 2:
                dummy3 = WX_MARK.wx_kigo.get(info[ix1+2:ix1+4])
                dummy4 = WX_MARK.wx_with.get(info[ix1+2:ix1+4])
            else:
                pass
            if dummy3 is not None or dummy4 is not None:
                wx_keta.append([ix1,4])
                ix1 += 4
            else:
                wx_keta.append([ix1,2])
                ix1 += 2
        else:
            ix1 += 1
        if len(info) <= ix1:
            eof_flg = 1
    return wx_keta


def wx_time_check(info, wx_time, wx_keta):
    for ix1 in range(len(wx_keta)):
        timeS_len = 0
        timeE_len = 0
        timeS = ""
        timeE = ""
        start_keta = wx_keta[ix1][0] + wx_keta[ix1][1]
        if info[start_keta:start_keta + 1] == "B":
            try:
                time = int(info[start_keta + 1: start_keta + 5])
                timeS_len = 4
            except ValueError:
                timeS_len = 2
            timeS = info[start_keta + 1: start_keta + 1 + timeS_len]
        if info[start_keta:start_keta + 1] == "E":
            try:
                time = int(info[start_keta + 1: start_keta + 5])
                timeE_len = 4
            except ValueError:
                timeE_len = 2
            timeE = info[start_keta + 1: start_keta + 1 + timeE_len]
        start_keta += timeS_len + timeE_len + 1
        if info[start_keta:start_keta + 1] == "B":
            try:
                time = int(info[start_keta + 1: start_keta + 5])
                timeS_len = 4
            except ValueError:
                timeS_len = 2
            timeS = info[start_keta + 1: start_keta + 1 + timeS_len]
        if info[start_keta:start_keta + 1] == "E":
            try:
                time = int(info[start_keta + 1: start_keta + 5])
                timeE_len = 4
            except ValueError:
                timeE_len = 2
            timeE = info[start_keta + 1: start_keta + 1 + timeE_len]
        wx_time.append([timeS,timeE])
    return wx_time

def get_wx(wx_keta, wx_time, info, num, jTimeH):
    wx_info = []
    for ix1 in range(len(wx_keta)):
        wx = ""
        if info[wx_keta[ix1][0]:wx_keta[ix1][0] + 2] in WX_MARK.wx_with:
            wx = WX_MARK.wx_with[info[wx_keta[ix1][0]:wx_keta[ix1][0] + 2]]
        if info[wx_keta[ix1][0]:wx_keta[ix1][0] + 2] in WX_MARK.wx_kigo:
            wx = WX_MARK.wx_kigo[info[wx_keta[ix1][0]:wx_keta[ix1][0] + 2]]
        if wx_keta[ix1][1] == 4:
            if info[wx_keta[ix1][0] + 2:wx_keta[ix1][0] + 4] in WX_MARK.wx_with:
                wx = wx + WX_MARK.wx_with[info[wx_keta[ix1][0] + 2:wx_keta[ix1][0] + 4]]
            if info[wx_keta[ix1][0] + 2:wx_keta[ix1][0] + 4] in WX_MARK.wx_kigo:
                wx = wx + WX_MARK.wx_kigo[info[wx_keta[ix1][0] + 2:wx_keta[ix1][0] + 4]]
        wx_info.append( "＜気象現象補足" + str(num) + "＞")
        wx_str = "    気象現象：" + wx
        num += 1
        wx_info.append(wx_str)
        
        for ix2 in range(len(wx_time[ix1])):
            if wx_time[ix1][ix2] != "":
                if len(wx_time[ix1][ix2]) == 4:
                    if jTimeH - 1 < 0:
                        time_str = "23:" + wx_time[ix1][ix2][2:4] + "(JST)"
                    else:
                        time_str = str(jTimeH - 1) + ":" + wx_time[ix1][ix2][2:4] + "(JST)"
                elif len(wx_time[ix1][ix2]) == 2:
                    time_str = str(jTimeH) + ":" + wx_time[ix1][ix2] + "(JST)"
                if ix2 == 0:
                    time_se_str = "    開始時刻：" + time_str
                else:
                    time_se_str = "    終了時刻：" + time_str
                wx_info.append(time_se_str)
        
    return wx_info, num
    
        

        
            
        