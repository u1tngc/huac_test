#PGM-ID:WX0S0202
#PGM-NAME:[P]WX共通TAF

import PK0S0100
import WX0S0204
import WX0S0207

def readTaf(taf):
    tafInfo = change_taf(taf)
    tafRet = []
    tafEng = []
    warning_flg = []
    ix1 = 0
    """
    for ix3 in range(len(taf)):
        if ix3 == 0:
            tafInfo = taf[ix3].split()
        else:
            tafInfox = []
            tafInfox = taf[ix3].split()
            for ix2 in range(len(tafInfox)):
                tafInfo.append(tafInfox[ix2])
    """
    tafInfo.append("$")
  #初期処理
    num_array = [1,1,1,1] #雲,乱気流,アイシング,wx
    tafStr = "～ＴＡＦ～ "
    tafRet ,tafEng, warning_flg = appendList(tafRet, tafEng, warning_flg, tafStr, tafInfo[ix1], 0)
    ix1 = ix1 + 1
  #通報区分
    if tafInfo[ix1] == 'COR':
        tafStr = "通報区分：訂正報（本報に誤りがある場合に通報）" 
        tafRet ,tafEng, warning_flg = appendList(tafRet, tafEng, warning_flg, tafStr, tafInfo[ix1], 0)
        ix1 = ix1 + 1
    elif tafInfo[ix1] == 'AMD':
        tafStr = "通報区分：修正報（本報に情報不足がある場合に通報）" 
        tafRet ,tafEng, warning_flg = appendList(tafRet, tafEng, warning_flg, tafStr, tafInfo[ix1], 0)
        ix1 = ix1 + 1
    elif tafInfo[ix1] == 'RTD':
        tafStr = "通報区分：遅延報" 
        tafRet ,tafEng, warning_flg = appendList(tafRet, tafEng, warning_flg, tafStr, tafInfo[ix1], 0)
        ix1 = ix1 + 1
    elif tafInfo[ix1] == 'AUTO':
        tafStr = "通報区分：自動観測通報"
        tafRet ,tafEng, warning_flg = appendList(tafRet, tafEng, warning_flg, tafStr, tafInfo[ix1], 0)
        ix1 = ix1 + 1
    if tafInfo[ix1] == 'AUTO':
        tafStr = "通報区分：自動観測通報" 
        tafRet ,tafEng, warning_flg = appendList(tafRet, tafEng, warning_flg, tafStr, tafInfo[ix1], 0)
        ix1 = ix1 + 1
  #地点略号
    if WX0S0207.get_location(tafInfo[ix1]) != "不明（プログラムに登録なし）":
        airport = WX0S0207.get_location(tafInfo[ix1])
        tafStr = '地点略号：' + airport
        tafRet ,tafEng, warning_flg = appendList(tafRet, tafEng, warning_flg, tafStr, tafInfo[ix1], 0)
        ix1 = ix1 + 1
  #観測時間
    if tafInfo[ix1][6:7] == "Z":
        utcTime = []
        jstTime = []
        utcTime.append(int(tafInfo[ix1][0:2]))
        utcTime.append(int(tafInfo[ix1][2:4]))
        utcTime.append(int(tafInfo[ix1][4:6]))
        jstTime = PK0S0100.utc_to_jst(utcTime)
        taf_day = tafInfo[ix1][0:2]
        if jstTime[2] < 10:
            jstTimeM = '0' + str(jstTime[2])
        else:
            jstTimeM = str(jstTime[2])
        tafStr = '通報日時：' + str(jstTime[0]) + '日' + str(jstTime[1]) + ':' + jstTimeM + '(JST)'
        tafRet ,tafEng, warning_flg = appendList(tafRet, tafEng, warning_flg, tafStr, tafInfo[ix1], 0)
        ix1 = ix1 + 1
    tafStr = timeStartEnd(tafInfo[ix1])
    tafRet ,tafEng, warning_flg = appendList(tafRet, tafEng, warning_flg, tafStr, tafInfo[ix1], 0)
    ix1 = ix1 + 1
    henkagun = 1
    turbice_flg = 0
    while tafInfo[ix1] != '$':
        str_flg = 0
        #1 = str
        #2 = num str
        #3 = num
        for ix9 in range(len(tafInfo[ix1])):
            try:
                dummy = int(tafInfo[ix1][ix9: ix9 + 1])
                if str_flg == 1:
                    str_flg = 2
                    break
                else:
                    str_flg = 3
            except ValueError:
                if str_flg == 3:
                    str_flg = 2
                    break
                else:
                    str_flg = 1

 #変化群
        if tafInfo[ix1] == 'BECMG':
            tafRet ,tafEng, warning_flg = appendList(tafRet, tafEng, warning_flg, "","", 0)
            tafStr = "～変化群" + str(henkagun) + "～" 
            tafRet ,tafEng, warning_flg = appendList(tafRet, tafEng, warning_flg, tafStr, tafInfo[ix1], 0)
            tafStr = "開始時間から変化が始まり、終了時刻には以下の状態になる。" 
            tafRet ,tafEng, warning_flg = appendList(tafRet, tafEng, warning_flg, tafStr, tafInfo[ix1], 0)
            if tafInfo[ix1 - 1][0:4] == "PROB":
                prob = int(tafInfo[ix1-1][4:7])
                tafStr = f"発生確率：{str(prob)}%" 
                tafRet ,tafEng, warning_flg = appendList(tafRet, tafEng, warning_flg, tafStr, tafInfo[ix1 - 1], 0)
            ix1 = ix1 + 1
            #対象時間
            tafStr = timeStartEnd(tafInfo[ix1])
            taf_day = tafInfo[ix1][0:2]
            tafRet ,tafEng, warning_flg = appendList(tafRet, tafEng, warning_flg, tafStr, tafInfo[ix1], 0)
            henkagun = henkagun + 1 
            num_array = [1,1,1,1] #雲,乱気流,アイシング,wx
        elif tafInfo[ix1] == 'TEMPO':
            tafRet ,tafEng, warning_flg = appendList(tafRet, tafEng, warning_flg, "","", 0)
            tafStr = "～変化群" + str(henkagun) + "～"
            tafRet ,tafEng, warning_flg = appendList(tafRet, tafEng, warning_flg, tafStr, tafInfo[ix1], 0)
            tafStr = "開始時刻から終了時刻までの間で一時的に以下の状態になる。"
            tafRet ,tafEng, warning_flg = appendList(tafRet, tafEng, warning_flg, tafStr, tafInfo[ix1], 0)
            if tafInfo[ix1 - 1][0:4] == "PROB":
                prob = int(tafInfo[ix1-1][4:7])
                tafStr = f"発生確率：{str(prob)}%" 
                tafRet ,tafEng, warning_flg = appendList(tafRet, tafEng, warning_flg, tafStr, tafInfo[ix1 - 1], 0)
            ix1 = ix1 + 1
            #対象時間
            tafStr = timeStartEnd(tafInfo[ix1])
            tafRet ,tafEng, warning_flg = appendList(tafRet, tafEng, warning_flg, tafStr, tafInfo[ix1], 0)
            henkagun = henkagun + 1 
            num_array = [1,1,1,1] #雲,乱気流,アイシング,wx
        elif tafInfo[ix1][0:2] == 'FM' and len(tafInfo[ix1]) == 8:
            tafRet ,tafEng, warning_flg = appendList(tafRet, tafEng, warning_flg, "","", 0)
            tafStr = "～変化群" + str(henkagun) + "～"
            tafRet ,tafEng, warning_flg = appendList(tafRet, tafEng, warning_flg, tafStr, tafInfo[ix1], 0)
            tafStr = "開始時間から以下の状態に変化"
            tafRet ,tafEng, warning_flg = appendList(tafRet, tafEng, warning_flg, tafStr, tafInfo[ix1], 0)
            tafutcTime = []
            tafjstTime = []
            tafutcTime.append(int(tafInfo[ix1][2:4]))
            tafutcTime.append(int(tafInfo[ix1][4:6]))
            tafutcTime.append(int(tafInfo[ix1][6:8]))
            tafjstTime = PK0S0100.utc_to_jst(tafutcTime)
            if tafjstTime[2] < 10:
                tafjstTimeM = '0' + str(tafjstTime[2])
            else:
                tafjstTimeM = str(tafjstTime[2])
            tafStr = "開始時間：" + str(tafjstTime[0]) + "日" + str(tafjstTime[1]) + ":" + tafjstTimeM + '(JST)' 
            tafRet ,tafEng, warning_flg = appendList(tafRet, tafEng, warning_flg, tafStr, tafInfo[ix1], 0)
            henkagun = henkagun + 1 
            num_array = [1,1,1,1] #雲,乱気流,アイシング,wx
 #CAVOK  
        elif tafInfo[ix1] == "CAVOK":
            tafRet ,tafEng, warning_flg = appendList(tafRet, tafEng, warning_flg, '視程：卓越視程10km以上', tafInfo[ix1], 0)
            tafRet ,tafEng, warning_flg = appendList(tafRet, tafEng, warning_flg, '雲：5000ft以下に雲無し・かつ重要な対流雲がない', tafInfo[ix1], 0)
            tafRet ,tafEng, warning_flg = appendList(tafRet, tafEng, warning_flg, '現在天気：なし', tafInfo[ix1], 0)

 #風向風速
        elif (tafInfo[ix1][5:7] == 'KT' or tafInfo[ix1][8:10] == 'KT') and tafInfo[ix1][0:3] != 'WND':
            if tafInfo[ix1][0:5] == '00000':
                tafStr = "風    向：風なし"
                tafRet ,tafEng, warning_flg = appendList(tafRet, tafEng, warning_flg, tafStr, tafInfo[ix1], 0)
                tafStr = "風    速：風なし"
                tafRet ,tafEng, warning_flg = appendList(tafRet, tafEng, warning_flg, tafStr, tafInfo[ix1], 0)
            else:
                wind_directs = tafInfo[ix1][0:3]
                if wind_directs == 'VRB':
                    tafStr = '風    向：不定'
                    tafRet ,tafEng, warning_flg= appendList(tafRet, tafEng, warning_flg, tafStr, tafInfo[ix1], 0)
                else:
                    wind_direct = int(tafInfo[ix1][0:3])
                    wind_direct_x = PK0S0100.wind_direction(wind_direct)
                    tafStr = '風    向：' + str(wind_direct) + '度(' + wind_direct_x + ')からの風'
                    tafRet ,tafEng, warning_flg = appendList(tafRet, tafEng, warning_flg, tafStr, tafInfo[ix1], 0)
                if tafInfo[ix1][5:6] == 'G':
                    wind_speed_kt = tafInfo[ix1][3:5]
                    wind_speed_ms = PK0S0100.kt_to_ms(int(wind_speed_kt))
                    wind_speed_gkt = tafInfo[ix1][6:8]
                    wind_speed_gms = PK0S0100.kt_to_ms(int(wind_speed_gkt))
                    tafStr = '風    速：' + str(wind_speed_kt) + 'kt' + '(' + str(wind_speed_ms) + 'm/s)'
                    tafRet ,tafEng, warning_flg = appendList(tafRet, tafEng, warning_flg, tafStr, tafInfo[ix1], 1)
                    tafStr = 'ガスト  ：' + str(wind_speed_gkt) + 'kt' + '(' + str(wind_speed_gms) + 'm/s)'
                    tafRet ,tafEng, warning_flg = appendList(tafRet, tafEng, warning_flg, tafStr, tafInfo[ix1], 10)
                else:
                    wind_speed_kt = tafInfo[ix1][3:5]
                    wind_speed_ms = PK0S0100.kt_to_ms(int(wind_speed_kt))
                    tafStr = '風    速：' + str(wind_speed_kt) + 'kt' + '(' + str(wind_speed_ms) + 'm/s)'
                    tafRet ,tafEng, warning_flg = appendList(tafRet, tafEng, warning_flg, tafStr, tafInfo[ix1], 1)
        elif tafInfo[ix1][3:4] == 'V':
            wind_direct_1 = int(tafInfo[ix1][0:3])
            wind_direct_2 = int(tafInfo[ix1][4:7])
            tafStr = '風向変化：' + str(wind_direct_1) + '度～' + str(wind_direct_2) + '度で推移'
            tafRet ,tafEng, warning_flg = appendList(tafRet, tafEng, warning_flg, tafStr, tafInfo[ix1], 0)

  #風変化
        elif tafInfo[ix1][0:3] == 'WND':
            if tafInfo[ix1][-2:] == "KT":
                tafInfo.insert(ix1 + 1,tafInfo[ix1][3:])
            tafStr = '＜風の変化＞'
            tafRet ,tafEng, warning_flg = appendList(tafRet, tafEng, warning_flg, tafStr, tafInfo[ix1], 0)
            ix1 = ix1 + 1
            wind_directs = tafInfo[ix1][0:3]
            if wind_directs == 'VRB':
                tafStr = '  風  向：不定'
                tafRet ,tafEng, warning_flg = appendList(tafRet, tafEng, warning_flg, tafStr, tafInfo[ix1], 0)
            else:
                wind_direct = int(wind_directs)
                wind_direct_x = PK0S0100.wind_direction(wind_direct)
                tafStr = '  風  向：' + str(wind_direct) + '度(' + wind_direct_x + ')からの風'
                tafRet ,tafEng, warning_flg = appendList(tafRet, tafEng, warning_flg, tafStr, tafInfo[ix1], 0)
            if tafInfo[ix1][5:6] == 'G':
                wind_speed_kt = tafInfo[ix1][3:5]
                wind_speed_ms = PK0S0100.kt_to_ms(int(wind_speed_kt))
                wind_speed_gkt = tafInfo[ix1][6:8]
                wind_speed_gms = PK0S0100.kt_to_ms(int(wind_speed_gkt))
                tafStr = '  風  速：' + str(wind_speed_kt) + 'kt' + '(' + str(wind_speed_ms) + 'm/s)'
                tafRet ,tafEng, warning_flg = appendList(tafRet, tafEng, warning_flg, tafStr, tafInfo[ix1], 1)
                tafStr = '  ガスト：' + str(wind_speed_gkt) + 'kt' + '(' + str(wind_speed_gms) + 'm/s)'
                tafRet ,tafEng, warning_flg = appendList(tafRet, tafEng, warning_flg, tafStr, tafInfo[ix1], 10)
            else:
                wind_speed_kt = tafInfo[ix1][3:5]
                wind_speed_ms = PK0S0100.kt_to_ms(int(wind_speed_kt))
                tafStr = '  風  速：' + str(wind_speed_kt) + 'kt' + '(' + str(wind_speed_ms) + 'm/s)'
                tafRet ,tafEng, warning_flg = appendList(tafRet, tafEng, warning_flg, tafStr, tafInfo[ix1], 1)
            ix1 = ix1 + 1
            tafInfo_a = ""
            wind_str = ""
            if tafInfo[ix1] == "AFT":
                wind_str = "以降"
                tafInfo_a = tafInfo[ix1]
                ix1 = ix1 + 1
            elif tafInfo[ix1] == "BEF":
                wind_str == "以前"
                tafInfo_a = tafInfo[ix1]
                ix1 = ix1 + 1
            tafInfo_a = tafInfo_a + ' ' + tafInfo[ix1]
            if "-" in tafInfo[ix1]:
                windTimeZ_s = []
                windTimeJ_s = []
                windTimeZ_e = []
                windTimeJ_e = []
                wind_time = tafInfo[ix1].split("-")
                if len(wind_time[0]) == 4:
                    windTimeZ_s.append(int(wind_time[0][0:2]))
                    windTimeZ_s.append(int(wind_time[0][2:4]))
                    windTimeZ_s.append(10) #なんでもいい
                else:
                    windTimeZ_s.append(int(taf_day))
                    windTimeZ_s.append(int(wind_time[0][0:2]))
                    windTimeZ_s.append(10) #なんでもいい
                windTimeJ_s = PK0S0100.utc_to_jst(windTimeZ_s)
                if len(wind_time[1]) == 4:
                    windTimeZ_e.append(int(wind_time[1][0:2]))
                    windTimeZ_e.append(int(wind_time[1][2:4]))
                    windTimeZ_e.append(10) #なんでもいい
                else:
                    windTimeZ_e.append(int(taf_day))
                    windTimeZ_e.append(int(wind_time[1][0:2]))
                    windTimeZ_e.append(10) #なんでもいい
                windTimeJ_e = PK0S0100.utc_to_jst(windTimeZ_e) 
                tafStr = f"  時  間：{str(windTimeJ_s[0])}日{str(windTimeJ_s[1])}時～{str(windTimeJ_e[0])}日{str(windTimeJ_e[1])}時{wind_str}"               
            else:
                windTimeZ = []
                windTimeJ = []
                if len(tafInfo[ix1]) == 4:
                    windTimeZ.append(int(tafInfo[ix1][0:2]))
                    windTimeZ.append(int(tafInfo[ix1][2:4]))
                    windTimeZ.append(10) #なんでもいい
                else:
                    windTimeZ.append(int(taf_day))
                    windTimeZ.append(int(tafInfo[ix1][0:2]))
                    windTimeZ.append(10) #なんでもいい
                windTimeJ = PK0S0100.utc_to_jst(windTimeZ) 
                tafStr = f"  時  間：{str(windTimeJ[0])}日{str(windTimeJ[1])}時{wind_str}"
            tafRet ,tafEng, warning_flg = appendList(tafRet, tafEng, warning_flg, tafStr, tafInfo_a, 0)
                
  #視程  
        elif len(tafInfo[ix1]) == 4 and str_flg == 3:
            try:
                visual = int(tafInfo[ix1])
                if visual == 9999:
                    tafStr = '視    程：10km以上'
                    tafRet ,tafEng, warning_flg = appendList(tafRet, tafEng, warning_flg, tafStr, tafInfo[ix1], 0)
                else:
                    tafStr = '視    程：' + str(visual) + "m" 
                    tafRet ,tafEng, warning_flg = appendList(tafRet, tafEng, warning_flg, tafStr, tafInfo[ix1], 4)
            except ValueError:
                pass
        elif tafInfo[ix1] == 'SKC' or tafInfo[ix1] == 'NSC':
            tafStr = '  雲    ：無し'
            tafRet ,tafEng, warning_flg = appendList(tafRet, tafEng, warning_flg, tafStr, tafInfo[ix1], 0)

  #気象現象
        elif tafInfo[ix1] == 'NSW':
            tafStr = '天気 ' + str(num_array[3]) + '  ：運航に支障のある気象現象が終了'
            tafRet ,tafEng, warning_flg = appendList(tafRet, tafEng, warning_flg, tafStr, tafInfo[ix1], 0)
            num_array[3] = num_array[3] + 1

        elif str_flg == 1 and tafInfo[ix1][0:3] != 'QNH' and tafInfo[ix1] != "FM" and tafInfo[ix1][0:2] != "VV":
            wx_kyodo = 0
            if tafInfo[ix1][0:1] == '+':
                wx_kyodo = 1
                wx = tafInfo[ix1][1:]
            elif tafInfo[ix1][0:1] == '-':
                wx_kyodo = 2
                wx = tafInfo[ix1][1:]
            else:
                wx = tafInfo[ix1]
            wx_info, retCd = WX0S0207.get_wx1(wx, 2)
            if retCd != 0:
                if wx_kyodo == 1:
                    tafStr = '' + str(num_array[3]) + '  ：強い' + wx_info[1]
                elif wx_kyodo == 2:
                    tafStr = '天気 ' + str(num_array[3]) + '  ：弱い' + wx_info[1]
                else:
                    tafStr = '天気 ' + str(num_array[3]) + '  ：' + wx_info[1]
                tafRet ,tafEng, warning_flg = appendList(tafRet, tafEng, warning_flg, tafStr, tafInfo[ix1], 10)
                num_array[3] = num_array[3] + 1

  #乱気流・着氷          
        elif len(tafInfo[ix1]) == 6 and str_flg == 3:
            turbice_flg = 0
            try:    
                dummy = int(tafInfo[ix1])
                if tafInfo[ix1][0:1] == '5':
                    tab = get_turbIce(tafInfo[ix1][1:2],1) 
                    turbice_flg = 1
                elif tafInfo[ix1][0:1] == '6':
                    ice = get_turbIce(tafInfo[ix1][1:2],2)
                    turbice_flg = 2
                if turbice_flg != 0:
                    turbice_f = int(tafInfo[ix1][2:5]) * 100
                    turbice_h = int(tafInfo[ix1][5:6]) * 1000
                    turbice_t = turbice_f + turbice_h
                    turbice_h_str = str(turbice_f) + 'ft～' + str(turbice_t) + 'ft'
                    if  turbice_flg == 1:
                        tafStr = '＜乱気流情報' + str(num_array[1]) + '＞'
                        tafRet ,tafEng, warning_flg = appendList(tafRet, tafEng, warning_flg, tafStr, tafInfo[ix1], 10)
                        tafStr = '  強度：' + tab
                        tafRet ,tafEng, warning_flg = appendList(tafRet, tafEng, warning_flg, tafStr, tafInfo[ix1], 0)
                        tafStr = '  高度：' + turbice_h_str
                        tafRet ,tafEng, warning_flg = appendList(tafRet, tafEng, warning_flg, tafStr, tafInfo[ix1], 0)
                        num_array[1] = num_array[1] + 1
                    elif turbice_flg == 2:
                        tafStr = '＜着氷情報' + str(num_array[2]) + '＞'
                        tafRet ,tafEng, warning_flg = appendList(tafRet, tafEng, warning_flg, tafStr, tafInfo[ix1], 10)
                        tafStr = '  強度：' + ice
                        tafRet ,tafEng, warning_flg = appendList(tafRet, tafEng, warning_flg, tafStr, tafInfo[ix1], 0)
                        tafStr = '  高度：' + turbice_h_str
                        tafRet ,tafEng, warning_flg = appendList(tafRet, tafEng, warning_flg, tafStr, tafInfo[ix1], 0)
                        num_array[2] = num_array[2] + 1
                turbice_flg = 0
            except ValueError:
                pass   

  #雲
        elif (len(tafInfo[ix1]) == 6 or len(tafInfo[ix1]) == 8 or len(tafInfo[ix1]) == 9) and tafInfo[ix1][0:3] != "QNH":
            try:
                dummy = int(tafInfo[ix1][0:3])
            except ValueError:     
                try:
                    dummy = tafInfo[ix1][3:6]
                    cloud_base = int(tafInfo[ix1][3:6])
                    cloud_amount = tafInfo[ix1][0:3]
                    if len(tafInfo[ix1]) == 8 or len(tafInfo[ix1]) == 9:
                        cloud_kind = tafInfo[ix1][6:]
                    else:
                        cloud_kind = ''
                    cloud_str = WX0S0207.get_cloudInfo(cloud_amount, cloud_base, cloud_kind, num_array[0])
                    tafRet ,tafEng, warning_flg = appendList(tafRet, tafEng, warning_flg, cloud_str, tafInfo[ix1], 3)
                    num_array[0] = num_array[0] + 1
                except ValueError:
                    pass
        elif tafInfo[ix1] == "VV///":
            tafStr = '垂直視程：不明'
            tafRet ,tafEng, warning_flg = appendList(tafRet, tafEng, warning_flg, tafStr, tafInfo[ix1], 0)

  #最高気温      
        elif tafInfo[ix1][0:2] == 'TX' and tafInfo[ix1][-1] == 'Z':
            maxUtc = []
            if tafInfo[ix1][2:3] == 'M':
                maxT = 1 - int(tafInfo[ix1][3:5])
                maxUtc.append(int(tafInfo[ix1][6:8]))
                maxUtc.append(int(tafInfo[ix1][8:10]))
                maxUtc.append(0)
            else:
                maxT = int(tafInfo[ix1][2:4])
                maxUtc.append(int(tafInfo[ix1][5:7]))
                maxUtc.append(int(tafInfo[ix1][7:9]))
                maxUtc.append(0)
            maxJst = PK0S0100.utc_to_jst(maxUtc)
            tafStr = '最高気温：' + str(maxJst[0]) + '日' + str(maxJst[1]) + '時(JST)に' + str(maxT) + '℃'
            tafRet ,tafEng, warning_flg = appendList(tafRet, tafEng, warning_flg, tafStr, tafInfo[ix1], 0)

  #最低気温
        elif tafInfo[ix1][0:2] == 'TN' and tafInfo[ix1][-1] == 'Z':
            minUtc = []
            if tafInfo[ix1][2:3] == 'M':
                minT = 0 - int(tafInfo[ix1][3:5])
                minUtc.append(int(tafInfo[ix1][6:8]))
                minUtc.append(int(tafInfo[ix1][8:10]))
                minUtc.append(0)
            else:
                minT = int(tafInfo[ix1][2:4])
                minUtc.append(int(tafInfo[ix1][5:7]))
                minUtc.append(int(tafInfo[ix1][7:9]))
                minUtc.append(0)
            minJst = PK0S0100.utc_to_jst(minUtc)
            tafStr = '最低気温：' + str(minJst[0]) + '日' + str(minJst[1]) + '時(JST)に' + str(minT) + '℃'
            tafRet ,tafEng, warning_flg = appendList(tafRet, tafEng, warning_flg, tafStr, tafInfo[ix1], 0)

  #QNH気圧
        elif tafInfo[ix1][0:3] == 'QNH':
            if tafInfo[ix1] != "QNHINS":
                qnh_in = int(tafInfo[ix1][3:7]) / 100
                qnh_hpa = PK0S0100.inHg_to_hPa(qnh_in)
                tafStr = 'ＱＮＨ気圧：' + str(qnh_in) + 'inHg（' + str(qnh_hpa) + 'hPa）'
            else:
                tafStr = 'ＱＮＨ気圧：不明'
            tafRet ,tafEng, warning_flg = appendList(tafRet, tafEng, warning_flg, tafStr, tafInfo[ix1], 0)
  #fm
        elif tafInfo[ix1] == "FM":
            tafStr = " "
            tafRet ,tafEng, warning_flg = appendList(tafRet, tafEng, warning_flg, tafStr, " ", 0)
            tafStr = "～変化～"
            tafRet ,tafEng, warning_flg = appendList(tafRet, tafEng, warning_flg, tafStr, " ", 0)
            time_z = [0,0,0]
            time_j = []
            time_z[0] = int(tafInfo[ix1 + 1][0:2])
            time_z[1] = int(tafInfo[ix1 + 1][3:5])
            time_z[2] = int(tafInfo[ix1 + 1][5:7])
            time_j = PK0S0100.utc_to_jst(time_z)
            if time_j[2] < 10:
                time_j_m = "0" + str(time_j[2])
            else:
                time_j_m = str(time_j[2])
            tafStr = f"{str(time_j[0])}日{str(time_j[1])}:{time_j_m}(JST)から下記の現象が開始"
            tafRet ,tafEng, warning_flg = appendList(tafRet, tafEng, warning_flg, tafStr, tafInfo[ix1] + " " + tafInfo[ix1 + 1], 0)
            ix1 = ix1 + 1

        ix1 = ix1 + 1
    
    warning_info = [0] * len(tafEng)
    warning_info = WX0S0204.checkWarning(warning_flg, tafEng)

    return tafRet, tafEng, warning_info

def change_taf(taf):
    tafInfo = []
    for ix4 in range(len(taf)):
        taf_dummy = taf[ix4].split()
        for ix5 in range(len(taf_dummy)):
            tafInfo.append(taf_dummy[ix5]) 
    return tafInfo
    for ix2 in range(len(taf[ix1])):
        taf_dummy = taf[ix1][ix2].split()


def appendList(tafRet, tafEng, warning_flg, str, tafinfo_ix1, warning):
    tafRet.append(str)
    if str[0:4] == '～変化群':
        tafEng.append('')
        warning_flg.append(warning)
    else:
        tafEng.append(tafinfo_ix1)
        warning_flg.append(warning)
    return tafRet, tafEng, warning_flg

def timeStartEnd(tafInfo_ix1):
    stime_z = []
    stime_j = []
    stime_z.append(int(tafInfo_ix1[0:2]))
    stime_z.append(int(tafInfo_ix1[2:4]))
    stime_z.append(0)
    stime_j = PK0S0100.utc_to_jst(stime_z)
    etime_z = []
    etime_j = []
    etime_z.append(int(tafInfo_ix1[5:7]))
    etime_z.append(int(tafInfo_ix1[7:9]))
    etime_z.append(0)
    etime_j = PK0S0100.utc_to_jst(etime_z)
    stime = str(stime_j[0]) + "日" + str(stime_j[1]) + "時(JST)"
    etime = str(etime_j[0]) + "日" + str(etime_j[1]) + "時(JST)"
    tafStr = "対象時刻：" + stime + '～' + etime
    return tafStr

def get_turbIce(kyodo,kinoCd):
    turbCode = {
        '0': 'なし',
        '1': '軽い乱気流',
        '2': '時折、晴天での乱気流',
        '3': '頻繁に晴天での乱気流',
        '4': '時折、雲中で乱気流',
        '5': '頻繁に雲中で乱気流',
        '6': '時折、晴天での強い乱気流',
        '7': '頻繁に晴天での強い乱気流',
        '8': '時折、雲中で強い乱気流',
        '9': '頻繁に雲中で強い乱気流'
    }

    iceCode = {
        '0': '極めて軽度の着氷',
        '1': '軽いミックス・アイシング',
        '2': '雲中で軽いライム・アイシング',
        '3': '降水下で軽いクリア・アイシング',
        '4': 'ミックス・アイシング',
        '5': '雲中でライム・アイシング',
        '6': '降水下でクリア・アイシング',
        '7': '強いミックス・アイシング',
        '8': '雲中で強いライム・アイシング',
        '9': '降水下で強いクリア・アイシング'
    }
    if kinoCd == 1:
        if kyodo in turbCode:
            turbice_str = turbCode[kyodo]
    elif kinoCd == 2:
        if kyodo in iceCode:
            turbice_str = iceCode[kyodo]
    return turbice_str
