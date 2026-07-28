#PGM-ID:WX0S0201
#PGM-NAME:[P]WX横田METAR

import PK0S0100
import WX0S0203
import WX0S0204
import WX0S0207


def readMetar(metar):
  #Metar読み込み
    metarInfo = metar.split()
    metarRet = []
    metarEng = []
    warning_flg = []

    for ix9 in range(len(metarInfo)):
        if metarInfo[ix9] == 'M':
            metarRet.append("当matarは変換できません。")
            metarRet.append("METAR観測機器にエラーがあります。")
            metarRet.append("Mは情報の欠如を示します。")
            metarEng.append("@@@@@@@@@@@@@@@@@@@@@@")
            metarEng.append("@@@@@System Error@@@@@")
            metarEng.append("@@@@@@@@@@@@@@@@@@@@@@")
            warning_info = [0] * len(metarRet)
            return metarRet, metarEng, warning_info
    ix1 = 0
  #通報種類判定
    if metarInfo[ix1] == "METAR":
        kind = "METAR(定時飛行場実況気象通報式)"
    elif metarInfo[ix1]  == "SPECI":
        kind = "SPECI(特別飛行場実況気象通報式)"
    metarRet.append(f"通報種類：{kind}") 
    metarEng.append(metarInfo[ix1])
    warning_flg.append(0)
    ix1 = ix1 + 1
  #地点略号
    location = WX0S0207.get_location(metarInfo[ix1])
    metarRet.append(f"地点略号：{location}") 
    metarEng.append(metarInfo[ix1])
    warning_flg.append(0)
    ix1 = ix1 + 1

  #観測時間
    utcTime = []
    jstTime = []
    utcTime.append(int(metarInfo[ix1][0:2]))
    utcTime.append(int(metarInfo[ix1][2:4]))
    utcTime.append(int(metarInfo[ix1][4:6]))
    jstTime = PK0S0100.utc_to_jst(utcTime)
    if jstTime[2] < 10:
        jstTimeM = '0' + str(jstTime[2])
    else:
        jstTimeM = str(jstTime[2])
    metarRet.append("観測日時：" + str(jstTime[0]) + "日" + str(jstTime[1]) + ":" + jstTimeM + '(JST)') 
    metarEng.append(metarInfo[ix1])
    warning_flg.append(0)
    ix1 = ix1 + 1
    if metarInfo[ix1] == 'COR':
        metarRet.append("通報区分：訂正報（本報に誤りがある場合に通報）" ) 
        metarEng.append(metarInfo[ix1])
        warning_flg.append(0)
        ix1 = ix1 + 1
    elif metarInfo[ix1] == 'AMD':
        metarRet.append("通報区分：修正報（本報に情報不足がある場合に通報）" ) 
        metarEng.append(metarInfo[ix1])
        warning_flg.append(0)
        ix1 = ix1 + 1
    elif metarInfo[ix1] == 'RTD':
        metarRet.append("通報区分：遅延報" ) 
        metarEng.append(metarInfo[ix1])
        warning_flg.append(0)
        ix1 = ix1 + 1
    elif metarInfo[ix1] == 'AUTO':
        metarRet.append("通報区分：自動観測通報") 
        metarEng.append(metarInfo[ix1])
        warning_flg.append(0)
        ix1 = ix1 + 1
    if metarInfo[ix1] == 'AUTO':
        metarRet.append("通報区分：自動観測通報") 
        metarEng.append(metarInfo[ix1])
        warning_flg.append(0)
        ix1 = ix1 + 1

  #風向風速
    if metarInfo[ix1].endswith("KT"):
        if metarInfo[ix1][0:5] == '00000':
            windInfo = "風    向：風なし"
            metarRet.append(windInfo)
            metarEng.append(metarInfo[ix1])
            warning_flg.append(0)
            windInfo = "風    速：風なし"
            metarRet.append(windInfo)
            metarEng.append(metarInfo[ix1])
            warning_flg.append(0)
            ix1 = ix1 + 1
        else:
            wind_directs = metarInfo[ix1][0:3]
            if wind_directs == 'VRB':
                wind_direct = '不定'
            else:
                wind_direct = int(metarInfo[ix1][0:3])
                wind_direct_x = PK0S0100.wind_direction(wind_direct)
                wind_direct = str(wind_direct) + '度(' + wind_direct_x + ')からの風'
            wind_direct_info = '風    向：' + wind_direct
            metarRet.append(wind_direct_info)
            metarEng.append(metarInfo[ix1])  
            warning_flg.append(0)
            if metarInfo[ix1][5:6] == 'G':
                wind_speed_kt = metarInfo[ix1][3:5]
                wind_speed_ms = PK0S0100.kt_to_ms(int(wind_speed_kt))
                wind_speed_gkt = metarInfo[ix1][6:8]
                wind_speed_gms = PK0S0100.kt_to_ms(int(wind_speed_gkt))
                wind_speed_info = '風    速：' + str(wind_speed_kt) + 'kt' + '(' + str(wind_speed_ms) + 'm/s)'
                metarRet.append(wind_speed_info)
                metarEng.append(metarInfo[ix1])
                warning_flg.append(1)
                wind_speed_info_gust = 'ガスト  ：' + str(wind_speed_gkt) + 'kt' + '(' + str(wind_speed_gms) + 'm/s)'
                metarRet.append(wind_speed_info_gust)
                metarEng.append(metarInfo[ix1])
                warning_flg.append(10) 
            else:
                wind_speed_kt = metarInfo[ix1][3:5]
                wind_speed_ms = PK0S0100.kt_to_ms(int(wind_speed_kt))
                wind_speed_info = '風    速：' + str(wind_speed_kt) + 'kt' + '(' + str(wind_speed_ms) + 'm/s)'
                metarRet.append(wind_speed_info)
                metarEng.append(metarInfo[ix1])
                warning_flg.append(1)
            ix1 = ix1 + 1
            if metarInfo[ix1][3:4] == 'V':
                wind_direct_1 = int(metarInfo[ix1][0:3])
                wind_direct_2 = int(metarInfo[ix1][4:7])
                wind_exInfo = '風向変化：' + str(wind_direct_1) + '度～' + str(wind_direct_2) + '度で推移'
                metarRet.append(wind_exInfo)
                metarEng.append(metarInfo[ix1])
                warning_flg.append(0)
                ix1 = ix1 + 1

  #視程
    if metarInfo[ix1][2:4] == 'SM' or metarInfo[ix1][1:3] == 'SM':
        if metarInfo[ix1][0:2] == '10':
            visualInfo = '視    程：10マイル以上（＝10km以上）'
            warning_flg.append(0)
        else:
            visual = int(metarInfo[ix1][0:1])
            visual_m = PK0S0100.statueMile_to_m(visual)
            visualInfo = '視    程：' + str(visual) + 'マイル（＝' + str(visual_m) + 'm）'
            warning_flg.append(2)
        metarRet.append(visualInfo)
        metarEng.append(metarInfo[ix1])
        ix1 = ix1 + 1
    elif metarInfo[ix1 + 1][1:2] == '/' and metarInfo[ix1 + 1][3:5] == 'SM':
        visual = int(metarInfo[ix1]) + (1 * (int(metarInfo[ix1 + 1][0:1]) / int(metarInfo[ix1 + 1][2:3])))
        visual_m = PK0S0100.statueMile_to_m(visual)
        visualInfo = '視    程：' + str(visual) + 'マイル（＝' + str(visual_m) + 'm）'
        metarRet.append(visualInfo)
        metarEng.append(metarInfo[ix1] + ' ' + metarInfo[ix1 + 1])
        warning_flg.append(2)
        ix1 = ix1 + 2
    elif metarInfo[ix1][1:2] == '/' and metarInfo[ix1][3:5] == 'SM':
        visual = 1 * (int(metarInfo[ix1][0:1]) / int(metarInfo[ix1][2:3]))
        visual_m = PK0S0100.statueMile_to_m(visual)
        visualInfo = '視    程：' + str(visual) + 'マイル（＝' + str(visual_m) + 'm）'
        metarRet.append(visualInfo)
        metarEng.append(metarInfo[ix1])
        warning_flg.append(2)
        ix1 = ix1 + 1
    
  #滑走路視距離1
    if metarInfo[ix1][0:3] == "RVR" and (metarInfo[ix1][3:4] == "/" or metarInfo[ix1][4:5] == "/"):
        metarRet.append("＜滑走路視距離＞")
        metarEng.append("") 
        warning_flg.append(0)
        if metarInfo[ix1] == "RVRNO":
            rvr_str = "    滑走視距離不明"
        else:
            if metarInfo[ix1][3:4] == "R" or metarInfo[ix1][3:4] == "C" or metarInfo[ix1][3:4] == "L":
                runway = metarInfo[ix1][0:4]
                rvr_len = 5
            else:
                runway = metarInfo[ix1][0:3]
                rvr_len = 4
            metarRet.append("  滑走路：" + runway)
            metarEng.append(metarInfo[ix1]) 
            warning_flg.append(0)
            try: #下限
                dummy = int(metarInfo[ix1][rvr_len:rvr_len + 1])
                rvr_hugo = "" 
            except ValueError:
                if metarInfo[ix1][rvr_len:rvr_len + 1] == "P":
                    rvr_hugo = "以上" 
                elif metarInfo[ix1][rvr_len:rvr_len + 1] == "M":
                    rvr_hugo = "以下"
                rvr_len += 1

            rvr_s_ft = int(metarInfo[ix1][rvr_len:rvr_len + 4])
            rvr_s_m = PK0S0100.ft_to_m(rvr_s_ft)
            rvr_len += 4
            rvr_s = str(rvr_s_ft) + "ft(" + str(rvr_s_m) + "m)" + rvr_hugo
            if metarInfo[ix1][rvr_len:rvr_len + 1] == "V":
                rvr_len += 1
                try: #上限
                    dummy = int(metarInfo[ix1][rvr_len:rvr_len + 1])
                    rvr_hugo = "" 
                except ValueError:
                    if metarInfo[ix1][rvr_len:rvr_len + 1] == "P":
                        rvr_hugo = "以上" 
                    elif metarInfo[ix1][rvr_len:rvr_len + 1] == "M":
                        rvr_hugo = "以下"
                    rvr_len += 1

                rvr_e_ft = int(metarInfo[ix1][rvr_len:rvr_len + 4])
                rvr_e_m = PK0S0100.ft_to_m(rvr_e_ft)
                rvr_len += 1
                rvr_e = str(rvr_e_ft) + "ft(" + str(rvr_e_m) + "m)" + rvr_hugo
                rvr_str = "  視距離：" + rvr_s + "～" + rvr_e
            else:
                rvr_str = "  視距離：" + rvr_s
        metarRet.append(rvr_str)
        metarEng.append(metarInfo[ix1]) 
        warning_flg.append(0)
        ix1 = ix1 + 1

  #気象現象   
    eof_flg = 0
    wx_num = 1
    if metarInfo[ix1] != 'CAVOK':
        while eof_flg == 0:
            if metarInfo[ix1] == 'NSC' or metarInfo[ix1] == 'NSD' or metarInfo[ix1] == 'CLR' or metarInfo[ix1] == 'SKC':
                eof_flg = 1
            else:
                metarInfo_wx, retCd= WX0S0207.check_wx(wx_num, metarInfo[ix1])
                if retCd == 0:
                    eof_flg = 1
                else: 
                    metarRet.append(metarInfo_wx)
                    metarEng.append(metarInfo[ix1])
                    warning_flg.append(10)
                    wx_num = wx_num + 1
                    ix1 = ix1 + 1
    
  #雲
    eof_flg = 0
    cloud_num = 1
    if metarInfo[ix1] != 'CAVOK':
        while eof_flg == 0:
            if metarInfo[ix1][0:2] == 'VV':
                if metarInfo[ix1][2:5] == "///":
                    cloudInfo = "垂直視程：不明"
                    warning_flg.append(0)
                else:
                    c_vis_ft = int(metarInfo[ix1][2:5]) * 100
                    c_vis_m = PK0S0100.ft_to_m(c_vis_ft)
                    cloudInfo = "垂直視程：" + str(c_vis_ft) + "ft(" + str(c_vis_m) + ")m"
                    warning_flg.append(3)
                metarRet.append(cloudInfo)
                metarEng.append(metarInfo[ix1])
                ix1 = ix1 + 1
            else:
                if metarInfo[ix1][2:3] == '/' and metarInfo[ix1][3:4] != '/':
                    eof_flg = 1
                elif metarInfo[ix1][3:4] == '/' and metarInfo[ix1][4:5] != '/':
                    eof_flg = 1
                elif metarInfo[ix1] == 'NSC' or metarInfo[ix1] == 'NCD' or metarInfo[ix1] == 'CLR' or metarInfo[ix1] == 'SKC':
                    skyClear = '雲情報  ：雲無し'
                    metarRet.append(skyClear)
                    metarEng.append(metarInfo[ix1])
                    warning_flg.append(0)
                    ix1 = ix1 + 1
                else:    
                    cloud_amount = metarInfo[ix1][0:3]
                    cloud_base =  metarInfo[ix1][3:6]
                    try:
                        dummy = int(cloud_base)
                    except ValueError:
                        eof_flg = 1
                    if eof_flg == 0:
                        if len(metarInfo[ix1]) > 6:
                            cloud_kind = metarInfo[ix1][6:]
                        else:
                            cloud_kind = ""
                        cloudInfo = WX0S0207.get_cloudInfo(cloud_amount, cloud_base, cloud_kind, cloud_num)
                        metarRet.append(cloudInfo)
                        metarEng.append(metarInfo[ix1])
                        warning_flg.append(3)
                        cloud_num = cloud_num + 1
                        ix1 = ix1 + 1

  #ｃａｖｏｋ
    if metarInfo[ix1] == 'CAVOK':
        metarRet.append('視    程：卓越視程10km以上')
        metarRet.append('雲情報  ：5000ft以下に雲無し・かつ重要な対流雲がない')
        metarRet.append('現在天気：なし')
        metarEng.append(metarInfo[ix1])
        metarEng.append(metarInfo[ix1])
        metarEng.append(metarInfo[ix1])
        warning_flg.append(0)
        warning_flg.append(0)
        warning_flg.append(0)
        
  #気温露点温度
    if (metarInfo[ix1][2:3] == '/' or metarInfo[ix1][3:4] == '/') and metarInfo[ix1][0:1] != 'R':
        metarInfo_t1, metarInfo_td1 = metarInfo[ix1].split("/")
        if metarInfo_t1[0:1] == "M":
            metarInfo_t = 0 - int(metarInfo_t1[1:3])
            if metarInfo_t1 == "M00":
                tInfo = f"気    温：{str(metarInfo_t)}℃ (氷点下)"
            else:
                tInfo = f"気    温：{str(metarInfo_t)}℃"
        else:
            metarInfo_t = int(metarInfo_t1)
            tInfo = f"気    温：{str(metarInfo_t)}℃"
        if metarInfo_td1[0:1] == "M":
            metarInfo_td = 0 - int(metarInfo_td1[1:3])
            if metarInfo_td1 == "M00":
                tdInfo = f"露点温度：{str(metarInfo_td)}℃ (氷点下)"
            else:
                tdInfo = f"露点温度：{str(metarInfo_td)}℃"
        else:
            metarInfo_td = int(metarInfo_td1)
            tdInfo = f"露点温度：{str(metarInfo_td)}℃"
        metarRet.append(tInfo)
        metarRet.append(tdInfo)
        metarEng.append(metarInfo[ix1])
        metarEng.append(metarInfo[ix1])
        warning_flg.append(0)
        warning_flg.append(0)
        ix1 = ix1 + 1
    hpa_umu = 0

  #気圧補正値
    if (metarInfo[ix1][0:1] == 'A' or metarInfo[ix1] == "ALSTG") and metarInfo[ix1] != "ALSTG/SLP":
        hpa_umu = 1
        if metarInfo[ix1] == "ALSTG":
            metarRet.append('QNH気圧 ：機器不調のため不明')
            metarEng.append(metarInfo[ix1])
            warning_flg.append(0)
            metarInfo_hpa = 0
        elif metarInfo[ix1][0:1] == 'A':
            metarInfo_inHg = round((int(metarInfo[ix1][1:5]) / 100), 2)
            metarInfo_hpa = PK0S0100.inHg_to_hPa(metarInfo_inHg)
            hPaInfo = 'QNH気圧 ：' + str(metarInfo_inHg) + 'inHg（' + str(metarInfo_hpa) + 'hPa）'
            metarRet.append(hPaInfo)
            metarEng.append(metarInfo[ix1])
            warning_flg.append(0)
        ix1 = ix1 + 1
    try:
        if metarInfo[ix1][0:1] == 'Q' and len(metarInfo[ix1]) == 5:
            hpa_umu = 1
            metarInfo_hpa = metarInfo[ix1][1:5]
            hPaInfo = 'QNH気圧 ：' + str(metarInfo_hpa) + 'hPa'
            metarRet.append(hPaInfo)
            metarEng.append(metarInfo[ix1])
            warning_flg.append(0)
            ix1 = ix1 + 1
        if hpa_umu == 0:
            metarInfo_hpa = 0
    except IndexError:
        warning_info = [0] * len(metarEng)
        warning_info = WX0S0204.checkWarning(warning_flg, metarEng)
        return metarRet, metarEng, warning_info

    try:
    #国内記事
        if metarInfo[ix1] == 'RMK':
            metarRet.append(' ')
            metarRet.append('～国内記事～')
            metarEng.append('')
            metarEng.append(metarInfo[ix1])
            warning_flg.append(0)
            warning_flg.append(0)
            ix1 = ix1 + 1
            rmk_wx_num = 0
            cig_num = 0
            while ix1 < len(metarInfo) and metarInfo[ix1] != '$':
                str_flg = 0
                #1 = str
                #2 = num str
                #3 = num
                for ix9 in range(len(metarInfo[ix1])):
                    try:
                        dummy = int(metarInfo[ix1][ix9: ix9 + 1])
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
                rmk_cloud_array = {
                    "OVC":"全天を覆う雲",
                    "BKN":"5/8～7/8の雲",
                    "SCT":"3/8～4/8の雲",
                    "FEW":"1/8～2/8の雲"
                    }  
                 
            #あられ判定
                if metarInfo[ix1] == "SNOW" and metarInfo[ix1 + 1] == "PELLETS":
                    metarRet.append("あられ種類：雪あられ")
                    metarEng.append(f"{metarInfo[ix1]} {metarInfo[ix1 + 1]}")
                    warning_flg.append(0)
                    ix1 = ix1 + 1
                if metarInfo[ix1] == "SMALL" and metarInfo[ix1 + 1] == "HAIL":
                    metarRet.append("あられ種類：氷あられ")
                    metarEng.append(f"{metarInfo[ix1]} {metarInfo[ix1 + 1]}")
                    warning_flg.append(0)
                    ix1 = ix1 + 1

            #観測機器
                if metarInfo[ix1][0:2] == 'AO':
                    if metarInfo[ix1][2:3] == '1': #AO1
                        kansoku = '観測機器：ＡＯ１（雨・雪の判別不可）'
                    elif metarInfo[ix1] == 'AO2A':
                        kansoku = '観測機器：ＡＯ２Ａ（雨の種類・雪の判別可能）'
                    elif metarInfo[ix1][2:3] == '2': #AO2
                        kansoku = '観測機器：ＡＯ２（雨・雪の判別可能）'
                    metarRet.append(kansoku)
                    metarEng.append(metarInfo[ix1])
                    warning_flg.append(0)
            #雲
                elif metarInfo[ix1][0:3] in rmk_cloud_array:
                    rmk_c_f = rmk_cloud_array[metarInfo[ix1][0:3]]
                    rmk_c_t = rmk_cloud_array[metarInfo[ix1 + 2][0:3]]
                    metarRet.append(f"雲    量：{rmk_c_f}から{rmk_c_t}へ変動")
                    metarEng.append(f"{metarInfo[ix1]} {metarInfo[ix1 + 1]} {metarInfo[ix1 + 2]}")
                    warning_flg.append(0) 
                    ix1 = ix1 + 2  
                
            #海面気圧
                elif metarInfo[ix1][0:3] == 'SLP':
                    if metarInfo[ix1] == 'SLPNO':
                        slpInfo = '海面気圧：不明'
                    elif metarInfo_hpa >= 1000:
                        slp = '10' + str(metarInfo[ix1][3:5]) + '.' + str(metarInfo[ix1][5:6])
                        slpInfo = '海面気圧：' + slp + 'hPa'
                    elif hpa_umu == 0:
                        if metarInfo[ix1][3:4] == '0':
                            slp = '10' + str(metarInfo[ix1][3:5]) + '.' + str(metarInfo[ix1][5:6])
                        else:
                            slp = '9' + str(metarInfo[ix1][3:5]) + '.' + str(metarInfo[ix1][5:6])
                        slpInfo = '海面気圧：' + slp + 'hPa'
                    else:
                        if metarInfo[ix1][3:4] == '0':
                            slp = '10' + str(metarInfo[ix1][3:5]) + '.' + str(metarInfo[ix1][5:6])
                        else:    
                            slp = '9' + str(metarInfo[ix1][3:5]) + '.' + str(metarInfo[ix1][5:6])
                        slpInfo = '海面気圧：' + slp + 'hPa'
                    metarRet.append(slpInfo)
                    metarEng.append(metarInfo[ix1])
                    warning_flg.append(0)

            #T気温露点
                elif metarInfo[ix1][0:1] == 'T' and len(metarInfo[ix1]) == 9:
                    if metarInfo[ix1][1:2] == '1':
                        temp_x = round((0 - (int(metarInfo[ix1][2:5]) / 10)), 1)
                    else:
                        temp_x = round((float(metarInfo[ix1][2:5]) / 10), 1)
                    if metarInfo[ix1][5:6] == '1':
                        tempTd_x = round((0 - (float(metarInfo[ix1][6:9]) / 10)), 1)
                    else:
                        tempTd_x = round((float(metarInfo[ix1][6:9]) / 10), 1)
                    temp_x_info = '気    温：' + str(temp_x) + '℃'
                    tempTd_x_info = '露    点：' + str(tempTd_x) + '℃'
                    metarRet.append(temp_x_info)
                    metarEng.append(metarInfo[ix1])
                    metarRet.append(tempTd_x_info)
                    metarEng.append(metarInfo[ix1])
                    warning_flg.append(0)
                    warning_flg.append(0)

            #P時間降水量
                elif metarInfo[ix1][0:1] == 'P' and len(metarInfo[ix1]) == 5 and metarInfo[ix1][3:4] != 'V' and metarInfo[ix1] != "PWINO":
                    if metarInfo[ix1][1:5] == '////':
                        rainH_info = "時間降水量：不明"
                        rain_flg = 0
                    else:
                        rainHInch = round(int(metarInfo[ix1][1:5]) / 100, 2)
                        rainHMm = PK0S0100.inch_to_mm(rainHInch)
                        rainH_info = "時間降水量：" + str(rainHInch) + 'inch（' + str(rainHMm) + 'mm）'
                        if metarInfo[ix1][1:5] == "0000":
                            rain_flg = 0
                        else:
                            rain_flg = 1
                    metarRet.append(rainH_info)   
                    metarEng.append(metarInfo[ix1])  
                    if rain_flg == 0:
                        warning_flg.append(0)  
                    else:
                        warning_flg.append(11)        

            #1最高気温
                elif metarInfo[ix1][0:1] == '1' and len(metarInfo[ix1]) == 5 and metarInfo[ix1][3:4] != 'V':
                    try:
                        dummy = int(metarInfo[ix1])                 
                        if metarInfo[ix1][1:2] == '0':
                            maxTemp = round(int(metarInfo[ix1][2:5]) / 10, 1)
                            maxTemp_info = "最高気温（過去6時間）：" + str(maxTemp) + '℃' 
                        else:
                            maxTemp = round(0 - int(metarInfo[ix1][2:5]) / 10, 1)  
                            maxTemp_info = "最高気温（過去6時間）：" + str(maxTemp) + '℃'                 
                        metarRet.append(maxTemp_info)
                        metarEng.append(metarInfo[ix1])
                        warning_flg.append(0)
                    except ValueError:
                        if metarInfo[ix1][1:5] == '////':
                            maxTemp_info = "最高気温（過去6時間）：不明"
                            metarRet.append(maxTemp_info)
                            metarEng.append(metarInfo[ix1])
                            warning_flg.append(0)
                        else:
                            pass

            #2最低気温
                elif metarInfo[ix1][0:1] == '2' and len(metarInfo[ix1]) == 5 and metarInfo[ix1][3:4] != 'V':
                    if metarInfo[ix1][1:5] == '////':
                        minTemp_info = "最低気温（過去6時間）：不明"
                    elif metarInfo[ix1][1:2] == '0':                
                        minTemp = round(int(metarInfo[ix1][2:5]) / 10, 1)
                        minTemp_info = "最低気温（過去6時間）：" + str(minTemp) + '℃' 
                    else:
                        minTemp = round(0 - int(metarInfo[ix1][2:5]) / 10, 1)
                        minTemp_info = "最低気温（過去6時間）：" + str(minTemp) + '℃' 
                    metarRet.append(minTemp_info)
                    metarEng.append(metarInfo[ix1])
                    warning_flg.append(0)

            #3降水量
                elif metarInfo[ix1][0:1] == '3' and len(metarInfo[ix1]) == 5 and metarInfo[ix1][3:4] != 'V':
                    if metarInfo[ix1][1:5] == '////':
                        rain_info = "降水量（過去3時間）：不明"
                    else:
                        rainInch = round(int(metarInfo[ix1][1:5]) / 100, 2)
                        rainMm = PK0S0100.inch_to_mm(rainInch)
                        rain_info = "降水量（過去3時間）：" + str(rainInch) + 'inch（' + str(rainMm) + 'mm）'
                    metarRet.append(rain_info)
                    metarEng.append(metarInfo[ix1])
                    warning_flg.append(0)

            #4最高気温・最低気温
                elif metarInfo[ix1][0:1] == '4' and (len(metarInfo[ix1]) == 9 or len(metarInfo[ix1]) == 5):
                    if metarInfo[ix1][1:2] == '/' or len(metarInfo[ix1]) == 5:
                        temp_max4_info = '最高気温：不明'
                        temp_min4_info = '最低気温：不明'
                        metarRet.append(temp_max4_info)
                        metarEng.append(metarInfo[ix1])
                        metarRet.append(temp_min4_info)
                        metarEng.append(metarInfo[ix1])
                        warning_flg.append(0)
                        warning_flg.append(0)
                    else:
                        if metarInfo[ix1][1:2] == '1':
                            temp_max4 = round((0 - (int(metarInfo[ix1][2:5]) / 10)), 1)
                        else:
                            temp_max4 = round((float(metarInfo[ix1][2:5]) / 10), 1)
                        if metarInfo[ix1][5:6] == '1':
                            temp_min4 = round((0 - (float(metarInfo[ix1][6:9]) / 10)), 1)
                        else:
                            temp_min4 = round((float(metarInfo[ix1][6:9]) / 10), 1)
                        temp_max4_info = '最高気温：' + str(temp_max4) + '℃'
                        temp_min4_info = '最低気温：' + str(temp_min4) + '℃'
                        metarRet.append(temp_max4_info)
                        metarEng.append(metarInfo[ix1])
                        metarRet.append(temp_min4_info)
                        metarEng.append(metarInfo[ix1])
                        warning_flg.append(0)
                        warning_flg.append(0)

            #4積雪量
                elif metarInfo[ix1][0:1] == '4' and len(metarInfo[ix1]) == 5 and metarInfo[ix1][3:4] != 'V':
                    snow_inch = int(metarInfo[ix1][2:5])
                    snow_mm = PK0S0100.inch_to_mm(snow_inch)
                    snow_str = '積雪量  ：' + str(snow_inch) + 'inch（' + str(snow_mm) + 'mm）'
                    metarRet.append(snow_str)
                    metarEng.append(metarInfo[ix1])
                    warning_flg.append(0)
                    
            #5気圧傾向     
                elif metarInfo[ix1][0:1] == '5' and len(metarInfo[ix1]) == 5 and metarInfo[ix1][3:4] != 'V':
                    if metarInfo[ix1][1:5] == '////':
                        hPa_tendency = '気圧傾向：不明'
                    else:
                        if metarInfo[ix1][1:2] == '0' and metarInfo[ix1][2:5] == '000':
                            hPa_tendency = 0 #変化なし
                        elif metarInfo[ix1][1:2] == '5' and metarInfo[ix1][2:5] == '000':
                            hPa_tendency = 0 #変化なし
                        elif metarInfo[ix1][1:2] == '4':
                            hPa_tendency = 0 #変化なし
                        elif int(metarInfo[ix1][1:2]) <= 3:
                            hPa_tendency = 1 #増加
                            hPa_change_amount = int(metarInfo[ix1][2:5]) / 10
                        elif int(metarInfo[ix1][1:2]) >= 5:
                            hPa_tendency = 2 #現象
                            hPa_change_amount = int(metarInfo[ix1][2:5]) / 10
                        if hPa_tendency == 0:
                            hPa_tendency = '気圧傾向：3時間前から変化なし'
                        elif hPa_tendency == 1:
                            hPa_tendency = '気圧傾向：3時間前から' + str(hPa_change_amount) + 'hPa上昇'
                        elif hPa_tendency == 2:
                            hPa_tendency = '気圧傾向：3時間前から' + str(hPa_change_amount) + 'hPa下降'
                    metarRet.append(hPa_tendency)  
                    metarEng.append(metarInfo[ix1])  
                    warning_flg.append(0)

            #6降水量
                elif metarInfo[ix1][0:1] == '6' and len(metarInfo[ix1]) == 5 and metarInfo[ix1][3:4] != 'V':
                    if metarInfo[ix1][1:5] == '////':
                        rain_info6 = "降水量（過去6時間）：" + '不明'
                    else:
                        rainInch6 = round(int(metarInfo[ix1][1:5]) / 100, 2)
                        rainMm6 = PK0S0100.inch_to_mm(rainInch6)
                        rain_info6 = "降水量（過去6時間）：" + str(rainInch6) + 'inch（' + str(rainMm6) + 'mm）'
                    metarRet.append(rain_info6)
                    metarEng.append(metarInfo[ix1])  
                    warning_flg.append(0)

            #7降水量
                elif metarInfo[ix1][0:1] == '7' and len(metarInfo[ix1]) == 5 and metarInfo[ix1][3:4] != 'V':
                    if metarInfo[ix1][1:5] == '////':
                        rain_info24 = "降水量（過去24時間）：" + '不明'
                    else:
                        rainInch24 = round(int(metarInfo[ix1][1:5]) / 100, 2)
                        rainMm24 = PK0S0100.inch_to_mm(rainInch24)
                        rain_info24 = "降水量（過去24時間）：" + str(rainInch24) + 'inch（' + str(rainMm24) + 'mm）'
                    metarRet.append(rain_info24)
                    metarEng.append(metarInfo[ix1])  
                    warning_flg.append(0)
            
            #最大風速    
                elif metarInfo[ix1] == 'PK':
                    metarRet.append("＜最大風速情報＞")  
                    metarEng.append(metarInfo[ix1] + ' ' + metarInfo[ix1 + 1] )
                    warning_flg.append(0)    
                    ix1 = ix1 + 2
                    #風向
                    pkwind_direct1 = int(metarInfo[ix1][0:3])
                    pkwind_direct2 = PK0S0100.wind_direction(pkwind_direct1)
                    pwwind_direct_info = "  風向：" + str(pkwind_direct1) + '度(' + pkwind_direct2 + ')からの風'
                    metarRet.append(pwwind_direct_info)  
                    metarEng.append(metarInfo[ix1])
                    warning_flg.append(10)  
                    #風速
                    pkwind_spKt = int(metarInfo[ix1][3:5])
                    pkwind_spMs = PK0S0100.kt_to_ms(pkwind_spKt)
                    pwwind_sp_info = '  風速：' + str(pkwind_spKt) + 'kt' + '(' + str(pkwind_spMs) + 'm/s)'
                    metarRet.append(pwwind_sp_info)
                    metarEng.append(metarInfo[ix1])
                    warning_flg.append(10)
                    #発生時間
                    if len(metarInfo[ix1]) == 10:
                        pkTimeZ = []
                        pkTimeJ = []
                        pkTimeZ.append(10) #なんでもいい
                        pkTimeZ.append(int(metarInfo[ix1][6:8]))
                        pkTimeZ.append(int(metarInfo[ix1][8:10]))
                        pkTimeJ = PK0S0100.utc_to_jst(pkTimeZ)
                        pkTime_info = "  観測日時：" + str(pkTimeJ[1]) + ":" + str(pkTimeJ[2]) + '(JST)'    
                    elif len(metarInfo[ix1]) == 8:
                        pkTime_info = "  観測日時：" + str(jstTime[1]) + ":" + metarInfo[ix1][6:8] + '(JST)'   
                    metarRet.append(pkTime_info)        
                    metarEng.append(metarInfo[ix1])
                    warning_flg.append(10)   

            #風の変化
                elif metarInfo[ix1] == 'WSHFT':
                    if len(metarInfo[ix1 + 1]) == 2:
                        wshift = '風の変化：' + str(jstTime[1]) + ":" + metarInfo[ix1 + 1] + "(JST)に変化"
                        metarRet.append(wshift)        
                        metarEng.append(metarInfo[ix1] + ' ' + metarInfo[ix1 + 1])  
                        warning_flg.append(11) 
                    elif len(metarInfo[ix1 + 1]) == 4:
                        wshift = '風の変化：' + str(jstTime[1] - 1) + ":" + metarInfo[ix1 + 1][2:4] + "(JST)に変化"
                        metarRet.append(wshift)        
                        metarEng.append(metarInfo[ix1] + ' ' + metarInfo[ix1 + 1])    
                        warning_flg.append(11)                   
                    ix1 = ix1 + 1

            #急な気圧変化
                elif metarInfo[ix1][0:4] == 'PRES':
                    if metarInfo[ix1] == 'PRESRR':
                        pressure = '急な気圧変化：急速に気圧上昇'
                    elif metarInfo[ix1] == 'PRESFR':
                        pressure = '急な気圧変化：急速に気圧下降'
                    metarRet.append(pressure)        
                    metarEng.append(metarInfo[ix1]) 
                    warning_flg.append(0)

            #シーリング
                elif metarInfo[ix1] == "CIG":
                    cig_num = cig_num + 1
                    metarRet.append("＜シーリング" + str(cig_num) + "＞")
                    metarEng.append(metarInfo[ix1]) 
                    warning_flg.append(0)
                    if metarInfo[ix1] == "CHINO":
                        metarRet.append("    シーリング不明")
                        metarEng.append(metarInfo[ix1])    
                        warning_flg.append(0)
                    else:
                        ix1 = ix1 + 1
                        if len(metarInfo[ix1]) == 3:
                            cig_ft = int(metarInfo[ix1]) * 100
                            cig_m = PK0S0100.ft_to_m(cig_ft)
                            cig = "    高度：" + str(cig_ft) + "ft(" + str(cig_m) + "m)"
                            metarRet.append(cig)
                            metarEng.append(metarInfo[ix1]) 
                            warning_flg.append(0)
                            ix1 = ix1 + 1
                            cig = "    場所：" + metarInfo[ix1]
                            metarRet.append(cig)
                            metarEng.append(metarInfo[ix1])    
                            warning_flg.append(0)
                        elif len(metarInfo[ix1]) == 7 and metarInfo[ix1][3:4] == "V":
                            cig_ft_1 = int(metarInfo[ix1][0:3]) * 100
                            cig_ft_2 = int(metarInfo[ix1][4:7]) * 100
                            cig_m_1 = PK0S0100.ft_to_m(cig_ft_1)
                            cig_m_2 = PK0S0100.ft_to_m(cig_ft_2)
                            cig = "    高度：" + str(cig_ft_1) + "ft(" + str(cig_m_1) + "m)～" + str(cig_ft_2) + "ft(" + str(cig_m_2) + "m)"
                            metarRet.append(cig)
                            metarEng.append(metarInfo[ix1]) 
                            warning_flg.append(0)
            
            #管制塔視程
                elif (metarInfo[ix1] == "TWR" or metarInfo[ix1] == "TOWER") and metarInfo[ix1 + 1] == "VIS":
                    metarRet.append("＜管制塔視程＞")
                    metarEng.append(metarInfo[ix1] + " " + metarInfo[ix1 + 1]) 
                    warning_flg.append(0)
                    ix1 = ix1 + 2
                    twr_vis_num = 0
                    if len(metarInfo[ix1]) == 1:
                        twr_vis_sm = int(metarInfo[ix1])
                        if metarInfo[ix1 + 1][1:2] == "/":
                            try:
                                dummy = int(metarInfo[ix1 + 1][0:1]) 
                                dummy = int(metarInfo[ix1 + 1][2:3]) 
                                twr_vis_num = 2
                                twr_vis_sm = twr_vis_sm + (int(metarInfo[ix1 + 1][0:1]) / int(metarInfo[ix1 + 1][2:3]))
                            except ValueError:
                                pass
                    else:
                        if metarInfo[ix1][1:3] == "SM":
                            twr_vis_sm = int(metarInfo[ix1][0:1])
                        else:
                            twr_vis_sm = int(metarInfo[ix1][0:1]) / int(metarInfo[ix1][2:3])
                    twr_vis_m = PK0S0100.statueMile_to_m(twr_vis_sm)
                    metarRet.append("  視程："+str(twr_vis_sm)+"マイル("+str(twr_vis_m)+"m)")
                    warning_flg.append(5)
                    if twr_vis_num == 2:
                        metarEng.append(metarInfo[ix1] + " " + metarInfo[ix1 + 1])
                        ix1 = ix1 + 1
                    else:
                        metarEng.append(metarInfo[ix1])
            #指定
                elif metarInfo[ix1] == "VIS":
                    metarRet.append("＜視程＞")
                    metarEng.append(metarInfo[ix1]) 
                    warning_flg.append(0)
                    ix1 = ix1 + 1  
                    rmk_vis_eng = ""    
                    try:
                        dummy = int(metarInfo[ix1])
                        rmk_vis_value_sm = int(metarInfo[ix1])
                        rmk_vis_eng = metarInfo[ix1]
                        ix1 = ix1 + 1
                    except ValueError:
                        rmk_vis_value_sm = 0
                    rmk_vis_temp = metarInfo[ix1].split("/")
                    if "V" in rmk_vis_temp[1]:
                        rmk_vis_temp1 = rmk_vis_temp[1].split("V")
                        rmk_vis_f_sm = rmk_vis_value_sm
                        rmk_vis_t_sm = rmk_vis_value_sm
                        rmk_vis_f_sm = rmk_vis_f_sm + int(rmk_vis_temp[0]) / int(rmk_vis_temp1[0])
                        rmk_vis_t_sm = rmk_vis_t_sm + int(rmk_vis_temp[0]) / int(rmk_vis_temp1[1])
                        rmk_vis_value_f_m = PK0S0100.statueMile_to_m(rmk_vis_f_sm)
                        rmk_vis_value_t_m = PK0S0100.statueMile_to_m(rmk_vis_t_sm)
                        rmk_vis_ret = f"  視程：{str(rmk_vis_f_sm)}～{str(rmk_vis_t_sm)}マイル({str(rmk_vis_value_f_m)}～{str(rmk_vis_value_t_m)}m)"
                        rmk_vis_eng = rmk_vis_eng + " "+ metarInfo[ix1]
                    else:
                        rmk_vis_value_sm = rmk_vis_value_sm + int(rmk_vis_temp[0]) / int(rmk_vis_temp[1])
                        rmk_vis_value_m = PK0S0100.statueMile_to_m(rmk_vis_value_sm)
                        rmk_vis_ret = f"  視程：{str(rmk_vis_value_sm)}マイル({str(rmk_vis_value_m)}m)"
                        rmk_vis_eng = rmk_vis_eng +  metarInfo[ix1]
                        if len(rmk_vis_eng) not in [1,2,3]:
                            rmk_vis_eng = f"{rmk_vis_eng[0:1]} {rmk_vis_eng[1:]}"
                    metarRet.append(rmk_vis_ret)
                    metarEng.append(rmk_vis_eng)
                    warning_flg.append(5)   
                    if metarInfo[ix1 + 1][0:3] == "RWY":
                        ix1 = ix1 + 1
                        metarRet.append(f"  場所：{metarInfo[ix1]}")
                        metarEng.append(metarInfo[ix1])
                        warning_flg.append(0)                           

                elif metarInfo[ix1] == "RVRNO":
                    metarRet.append("滑走路視距離：不明")
                    metarEng.append(metarInfo[ix1]) 
                    warning_flg.append(0)            

                elif metarInfo[ix1] == "WND" and metarInfo[ix1 + 1] == "DATA" and metarInfo[ix1 + 2] == "ESTMD":
                    metarRet.append("風情報：機器不調のため推定値")
                    metarEng.append(metarInfo[ix1] + " " + metarInfo[ix1+1] + " " + metarInfo[ix1+2]) 
                    warning_flg.append(0)
                    ix1 = ix1 + 2
                
                elif (metarInfo[ix1] == "ALSTG/SLP" or metarInfo[ix1] == "ALSTG" or metarInfo[ix1] == "SLP/ALSTG") and metarInfo[ix1 + 1] == "ESTMD":
                    metarRet.append("気圧情報：機器不調のため推定値")
                    metarEng.append(metarInfo[ix1] + " " + metarInfo[ix1+1]) 
                    warning_flg.append(0)
                    ix1 = ix1 + 1
                
                elif (metarInfo[ix1] == "ALSTG/SLP" or metarInfo[ix1] == "ALSTG") and metarInfo[ix1 + 1] == "DATA" and metarInfo[ix1 + 2] == "ESTMD":
                    metarRet.append("気圧情報：機器不調のため推定値")
                    metarEng.append(metarInfo[ix1] + " " + metarInfo[ix1+1] + " " + metarInfo[ix1+2]) 
                    warning_flg.append(0)
                    ix1 = ix1 + 2
                
                elif metarInfo[ix1] == "PWINO":
                    metarRet.append("降水情報：機器不調のため種類と量の判別不能")
                    metarEng.append(metarInfo[ix1]) 
                    warning_flg.append(0)

                elif metarInfo[ix1] == "VISNO":
                    metarRet.append("視程情報：下記観測点にて測定不能")
                    metarEng.append(metarInfo[ix1] + " " + metarInfo[ix1+1]) 
                    warning_flg.append(0)
                    if metarInfo[ix1 + 1][0:3] == "RWY":
                        metarRet.append("    滑走路：" + metarInfo[ix1 + 1])
                        metarEng.append(metarInfo[ix1] + " " + metarInfo[ix1+1]) 
                        warning_flg.append(0)
                        ix1 = ix1 + 1

                elif metarInfo[ix1] == "CHINO":
                    if metarInfo[ix1 + 1][0:3] == "RWY":
                        metarRet.append("シーリング情報：下記観測点にて測定不能")
                        metarEng.append(metarInfo[ix1] + " " + metarInfo[ix1+1]) 
                        warning_flg.append(0)
                        metarRet.append("    滑走路：" + metarInfo[ix1 + 1])
                        metarEng.append(metarInfo[ix1] + " " + metarInfo[ix1+1]) 
                        warning_flg.append(0)
                        ix1 = ix1 + 1
                    else:
                        metarRet.append("シーリング情報：測定不能")
                        metarEng.append(metarInfo[ix1]) 
                        warning_flg.append(0)
                
                elif metarInfo[ix1] == "FZRANO":
                    metarRet.append("降水情報：機器不調のため降水と氷雨の判別と量を判別不能")
                    metarEng.append(metarInfo[ix1]) 
                    warning_flg.append(0)

                elif metarInfo[ix1] == "TSNO":
                    metarRet.append("雷情報：雷の観測無し")
                    metarEng.append(metarInfo[ix1]) 
                    warning_flg.append(0)

            #LTG
                elif metarInfo[ix1] == "LTG":
                    ltg_flg = check_LTG_direct(metarInfo[ix1 + 2],1)
                    if ltg_flg == 1:
                        metarRet.append("雷情報：遠方に雷を観測")
                        metarEng.append(metarInfo[ix1] + " " + metarInfo[ix1 + 1])  
                        warning_flg.append(0)
                        ix1 = ix1 + 1
                    else:
                        metarRet.append("雷情報：下記方角の遠方に雷を観測")
                        metarEng.append(metarInfo[ix1] + " " + metarInfo[ix1 + 1])  
                        warning_flg.append(0)
                        ltg_str = check_LTG_direct(metarInfo[ix1 + 2],ltg_flg)
                        metarRet.append(ltg_str)
                        metarEng.append(metarInfo[ix1 + 2])  
                        warning_flg.append(0)
                        ix1 = ix1 + 2            

            #気象現象の補足
                elif WX0S0207.check_rmkWx(metarInfo[ix1]) == 1:
                    rmkwx, rmk_wx_num = WX0S0203.get_rmkwx(metarInfo[ix1],rmk_wx_num, jstTime[1])
                    for ix3 in range(len(rmkwx)):
                        metarRet.append(rmkwx[ix3])
                        metarEng.append(metarInfo[ix1])
                        if rmkwx[ix3][0:9] == '    気象現象：':
                            warning_flg.append(11)
                        else:
                            warning_flg.append(0)

                ix1 = ix1 + 1

    except IndexError:
        pass
    warning_info = [0] * len(metarEng)
    warning_info = WX0S0204.checkWarning(warning_flg, metarEng)

    return metarRet, metarEng, warning_info


def check_LTG_direct(info,kino_code):
    direct = ["N","E","S","W","NE","SE","SW","NW"]
    direct_jp = {
        "N" : "北",
        "E" : "東",
        "S" : "南",
        "W" : "西",
        "NE" : "北東",
        "SE" : "南東",
        "SW" : "南西",
        "NW" : "北西"}
    if kino_code == 1:
        flg = 1
        if info[1:2] == "-" or info[2:3] == "-":
            if info[1:2] == "-":
                direct_info = info[0:1]
            elif info[2:3] == "-":
                direct_info = info[0:2]
            for ix1 in range(len(direct)):
                if direct[ix1] == direct_info:
                    flg = 3
        if len(info) == 1 or len(info) == 2:
            try:
                int(info[0:1])
                int(info[1:2])
            except ValueError:
                for ix1 in range(len(direct)):
                    if direct[ix1] == info:
                        flg = 2
        return flg
    elif kino_code == 2:
        ltg_direct = direct_jp.get(info)
        ret_str = "    方角：" + ltg_direct
        return ret_str
    elif kino_code == 3:
        haihun_flg = 0
        direct_len = len(info)
        for ix1 in range(direct_len):
            if info[ix1:ix1 + 1] == "-":
                haihun = ix1
        ltg_direct1 = direct_jp.get(info[0:haihun])
        ltg_direct2 = direct_jp.get(info[haihun + 1: direct_len])
        ret_str = "    方角：" + ltg_direct1 + "～" + ltg_direct2
        return ret_str
