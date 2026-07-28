#PGM-ID:WX0S0205
#PGM-NAME:[P]WX欧式METAR
#最終更新日:2026/02/01

import re

import PK0S0100
import WX0S0204
import WX0S0206
import WX0S0207
import WX0S0208

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
    metarRet.append("地点略号：" + location) 
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
    try:
        visual = int(metarInfo[ix1])
        if visual == 9999:
            metarRet.append("視    程：10km以上")
            metarEng.append(metarInfo[ix1])
            warning_flg.append(4)
        elif visual == 0000:
            metarRet.append("視    程：100m未満")
            metarEng.append(metarInfo[ix1])
            warning_flg.append(4)
        else:
            metarRet.append("視    程：" + str(visual) + "m")
            metarEng.append(metarInfo[ix1])
            warning_flg.append(4)
        ix1 = ix1 + 1
    except ValueError:
        if metarInfo[ix1] == "////":
            metarRet.append("視    程：不明")
            metarEng.append(metarInfo[ix1])
            warning_flg.append(0)
            ix1 = ix1 + 1

  #滑走路視距離
    rvr_eof = 0
    rvr_num = 1
    while rvr_eof == 0:
        if metarInfo[ix1][0:1] == "R" and re.search("/",metarInfo[ix1]):
            rvr_array = translate_rvr(metarInfo[ix1])
            metarRet.append("＜滑走路視距離" + str(rvr_num) + "＞")
            metarEng.append("")
            warning_flg.append(0)
            for ix2 in range(len(rvr_array)):
                metarRet.append(rvr_array[ix2])
                metarEng.append(metarInfo[ix1])
                if ix2 == 1:
                    warning_flg.append(11)
                else:
                    warning_flg.append(0)
            rvr_num = rvr_num + 1
            ix1 = ix1 + 1
        else:
            rvr_eof = 1


  #気象現象   
    eof_flg = 0
    wx_num = 1
    if metarInfo[ix1] != 'CAVOK':
        if metarInfo[ix1] == '//':
            metarRet.append("現在天気：不明")
            metarEng.append(metarInfo[ix1])
            warning_flg.append(0)
            ix1 = ix1 + 1
        else:
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
        if metarInfo[ix1] == "//////":
            metarRet.append("雲情報  ：不明")
            metarEng.append(metarInfo[ix1])
            warning_flg.append(0)
            ix1 = ix1 + 1
        else:
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
                    num_slash = 0
                    for ix10 in range(len(metarInfo[ix1]) + 1):
                        if metarInfo[ix1][ix10: ix10 + 1] == "/":
                            num_slash = num_slash + 1
                    if num_slash == 1:
                        eof_flg = 1
                    else:
                        if metarInfo[ix1] == 'NSC' or metarInfo[ix1] == 'NCD' or metarInfo[ix1] == 'CLR' or metarInfo[ix1] == 'SKC':
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
                                if cloud_base != "///":
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
        metarRet.append('  雲    ：5000ft以下に雲無し・かつ重要な対流雲がない')
        metarRet.append('現在天気：なし')
        metarEng.append(metarInfo[ix1])
        metarEng.append(metarInfo[ix1])
        metarEng.append(metarInfo[ix1])
        warning_flg.append(0)
        warning_flg.append(0)
        warning_flg.append(0)
        ix1 = ix1 + 1
        
  #気温露点温度
    if metarInfo[ix1] == "/////":
        metarRet.append("気    温：不明")
        metarEng.append(metarInfo[ix1])
        warning_flg.append(0)
        metarRet.append("露点温度：不明")
        metarEng.append(metarInfo[ix1])
        warning_flg.append(0)
        ix1 = ix1 + 1 
    elif (metarInfo[ix1][2:3] == '/' or metarInfo[ix1][3:4] == '/') and metarInfo[ix1][0:1] != 'R':
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

  #気圧補正値
    hpa_umu = 0
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
            if metarInfo[ix1][1:5] == "////":
                hPaInfo ='QNH気圧 ：不明'
            else:
                hpa_umu = 1
                metarInfo_hpa = metarInfo[ix1][1:5]
                hPaInfo = 'QNH気圧 ：' + str(metarInfo_hpa) + 'hPa'
            metarRet.append(hPaInfo)
            metarEng.append(metarInfo[ix1])
            warning_flg.append(0)
            ix1 = ix1 + 1
        if hpa_umu == 0:
            metarInfo_hpa = 0
        if metarInfo[ix1] == "RERA":
            metarRet.append('過去天気：過去20分以内に驟雨性の雨')
            metarEng.append(metarInfo[ix1])
            warning_flg.append(11)
            ix1 = ix1 + 1
        if metarInfo[ix1] == "WS":
            metarRet.append('＜ウインドシア＞')
            metarEng.append(metarInfo[ix1])
            warning_flg.append(0)
            metarRet.append('  場所：' + metarInfo[ix1 + 1])
            metarEng.append(metarInfo[ix1 + 1])
            warning_flg.append(0)
            ix1 = ix1 + 2
    except IndexError:
        warning_info = [0] * len(metarEng)
        warning_info = WX0S0204.checkWarning(warning_flg, metarEng)
        return metarRet, metarEng, warning_info
    #TREND
    try:
        if metarInfo[ix1] == "NOSIG" or metarInfo[ix1] == "TEMPO" or metarInfo[ix1] == "BECMG" or metarInfo[0:2] == "FM":
            metarRet, metarEng, warning_flg, ix1 = WX0S0206.get_trend(metarInfo, metarRet, metarEng, warning_flg, ix1)
    except IndexError:
        warning_info = [0] * len(metarEng)
        warning_info = WX0S0204.checkWarning(warning_flg, metarEng)
        return metarRet, metarEng, warning_info
    
    #RMK
    try:
        if metarInfo[ix1] == "RMK":
            metarRet.append("")
            metarEng.append("")
            warning_flg.append(0)
            metarRet.append("～国内記事～")
            metarEng.append(metarInfo[ix1])
            warning_flg.append(0)
            ix1 = ix1 + 1
            metarRet, metarEng, warning_flg, ix1 = get_rmk(metarInfo, metarRet, metarEng, warning_flg, ix1)
    except IndexError:
        warning_info = [0] * len(metarEng)
        warning_info = WX0S0204.checkWarning(warning_flg, metarEng)
        return metarRet, metarEng, warning_info

    warning_info = [0] * len(metarEng)
    warning_info = WX0S0204.checkWarning(warning_flg, metarEng)
    return metarRet, metarEng, warning_info

    
def translate_rvr(inp_rvr):
    prefix_translation = {
            "P": "m以上",
            "M": "m未満",
            "": "m"
        }
    trend_translation = {
        "D": "減少中",
        "N": "変化なし",
        "U": "増加中",
        "": "動向情報なし"
        }
    rvr_array = []
    rvr_vis_rest = ""
    rvr_trend = ""
    rvr = str(inp_rvr)
    rvr_rw, rvr_vis = rvr.split("/")
    if rvr_rw[1:] == "MID":
        rvr_array.append("  滑走路：RW中間で")
    else:
        rvr_array.append("  滑走路：RW" + rvr_rw[1:])
    if rvr_vis[4:5] == "V" or rvr_vis[5:6] == "V":
        rvr_vis1, rvr_vis2 = rvr_vis.split("V")
        if rvr_vis1[0:1] == "P" or rvr_vis1[0:1] == "M":
            rvr_prefix1 = prefix_translation[rvr_vis1[0:1]]
            rvr_distance1 = int(rvr_vis1[1:])
        else:
            rvr_prefix1 = prefix_translation[""]
            rvr_distance1 = int(rvr_vis1)
        rvr_vis_jp1 = f"{str(rvr_distance1)}{rvr_prefix1}"
        if rvr_vis2[0:1] == "P" or rvr_vis2[0:1] == "M":
            rvr_prefix2 = prefix_translation[rvr_vis2[0:1]]
            rvr_vis_rest2 = rvr_vis2[1:]
        else:
            rvr_prefix2 = prefix_translation[""]
            rvr_vis_rest2 = rvr_vis2
        if rvr_vis_rest2[-1] == "D" or rvr_vis_rest2[-1] == "N" or rvr_vis_rest2[-1] == "U":
            rvr_trend = rvr_vis_rest2[-1]
            rvr_distance2 = int(rvr_vis_rest2[:-1])
        else:
            rvr_trend = ""
            rvr_distance2 = int(rvr_vis_rest2)
        rvr_vis_jp2 = f"{str(rvr_distance2)}{rvr_prefix2}"
        rvr_distance_jp = f"{rvr_vis_jp1}～{rvr_vis_jp2}"
    else:
        if rvr_vis[0:1] == "P" or rvr_vis[0:1] == "M":
            rvr_prefix = prefix_translation[rvr_vis[0:1]]
            rvr_vis_rest = rvr_vis[1:]
        else:
            rvr_prefix = prefix_translation[""]
            rvr_vis_rest = rvr_vis
        if rvr_vis_rest[-1] == "D" or rvr_vis_rest[-1] == "N" or rvr_vis_rest[-1] == "U":
            rvr_trend = rvr_vis_rest[-1]
            rvr_distance = str(int(rvr_vis_rest[:-1]))
        else:
            rvr_trend = ""
            rvr_distance = str(int(rvr_vis_rest))
        rvr_distance_jp = f"{rvr_distance}{rvr_prefix}"
    rvr_array.append(f"  視  程：{rvr_distance_jp}")
    rvr_array.append(f"  傾  向：{trend_translation.get(rvr_trend, '')}")

    return rvr_array 

def get_rmk(metarInfo, metarRet, metarEng, warning_flg, ix1):
    try:
        rmk_eof = 0
        cloud_num = 1
        pirep_num = 1
        while rmk_eof == 0:
        #項目チェック
            cloud_flg = 0
            try:
                dummy = int(metarInfo[ix1][0:1])
                dummy = int(metarInfo[ix1][3:6])
                cloud_flg = 1
            except ValueError:
                cloud_flg = 0
            if cloud_flg == 0:
                try:
                    dummy = int(metarInfo[ix1][0:1])
                    dummy = int(metarInfo[ix1][4:7])
                    cloud_flg = 1
                except ValueError:
                    cloud_flg = 0
            pirep_flg = check_PIREP(metarInfo[ix1])

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

        #気圧上昇下降
            if metarInfo[ix1] == "P/RR":
                metarRet.append("気圧情報：気圧急上昇(30分以内に1hPa以上の変化)")
                metarEng.append(metarInfo[ix1])
                warning_flg.append(0)
            elif metarInfo[ix1] == "P/FR":
                metarRet.append("気圧情報：気圧急下降(30分以内に1hPa以上の変化)")
                metarEng.append(metarInfo[ix1])
                warning_flg.append(0)

        #PIREP
            elif pirep_flg == 1:
                if metarInfo[ix1] != "AND":
                    if pirep_num == 1:
                        metarRet.append("")
                        metarEng.append("")
                        warning_flg.append(0)
                        metarRet.append("～PIREP(操縦士報告)等～")
                        metarEng.append("")
                        warning_flg.append(0)
                        metarRet, metarEng, warning_flg, ix1 = WX0S0208.translate_PIREP(metarInfo, metarRet, metarEng, warning_flg, ix1, pirep_num)
                        pirep_num = pirep_num + 1
                    else:
                        metarRet, metarEng, warning_flg, ix1 = WX0S0208.translate_PIREP(metarInfo, metarRet, metarEng, warning_flg, ix1, pirep_num)
                        pirep_num = pirep_num + 1
            elif metarInfo[ix1] == "AND":
                ix1 = ix1 + 1                
                metarRet, metarEng, warning_flg, ix1 = WX0S0208.translate_PIREP(metarInfo, metarRet, metarEng, warning_flg, ix1, pirep_num)
                pirep_num = pirep_num + 1

        #滑走路視距離    
            elif metarInfo[ix1][0:1] == "R" and re.search("/",metarInfo[ix1]):
                rvr_array = translate_rvr(metarInfo[ix1])
                metarRet.append("＜滑走路視距離＞")
                metarEng.append(metarInfo[ix1])
                warning_flg.append(0)
                for ix2 in range(len(rvr_array)):
                    metarRet.append(rvr_array[ix2])
                    metarEng.append(metarInfo[ix1])
                    if ix2 == 1:
                        warning_flg.append(11)
                    else:
                        warning_flg.append(0)

        #雲情報
            elif cloud_flg == 1:
                metarRet.append("＜雲情報" + str(cloud_num) + "＞")
                metarEng.append("")
                warning_flg.append(0)
                rmk_cloud = get_cloud_rmk(metarInfo[ix1])
                metarRet.append("  雲量：" + rmk_cloud[0])
                metarEng.append(metarInfo[ix1])
                warning_flg.append(0)
                metarRet.append("  雲形：" + rmk_cloud[1])
                metarEng.append(metarInfo[ix1])
                warning_flg.append(6)
                metarRet.append("  雲底：" + rmk_cloud[2])
                metarEng.append(metarInfo[ix1])
                warning_flg.append(7)
                cloud_num = cloud_num + 1

        #気圧補正値
            elif metarInfo[ix1][0:1] == 'A':
                if metarInfo[ix1] == "A////":
                    hPaInfo = 'QNH気圧 ：不明'
                    metarRet.append(hPaInfo)
                    metarEng.append(metarInfo[ix1])
                    warning_flg.append(0)
                else:
                    if re.search(".",metarInfo[ix1]) and len(metarInfo[ix1]) != 5:
                        print(metarInfo[ix1])
                        dummy_inHg1, dummy_inHg2 = metarInfo[ix1][1:].split(".")
                        dummy_inHg = dummy_inHg1 + dummy_inHg2
                        rmk_inHg = round((int(dummy_inHg) / 100), 2)
                    else:
                        rmk_inHg = round((int(metarInfo[ix1][1:5]) / 100), 2)
                    rmk_hpa = PK0S0100.inHg_to_hPa(rmk_inHg)
                    hPaInfo = 'QNH気圧 ：' + str(rmk_inHg) + 'inHg（' + str(rmk_hpa) + 'hPa）'
                    metarRet.append(hPaInfo)
                    metarEng.append(metarInfo[ix1])
                    warning_flg.append(0)
            elif metarInfo[ix1][0:3] == "QFE":
                qfeInfo = 'QFE気圧 ：' + metarInfo[ix1][3:] + 'hPa'
                metarRet.append(qfeInfo)
                metarEng.append(metarInfo[ix1])
                warning_flg.append(0)
            
        #降水開始
            elif metarInfo[ix1][0:2] == "RI" and len(metarInfo[ix1]) == 5:
                rain_start = f"降水開始：{str(int(metarInfo[ix1][2:]))}分前から降水現象を観測"
                metarRet.append(rain_start)
                metarEng.append(metarInfo[ix1])
                warning_flg.append(0)

        #風向計測機器
            elif metarInfo[ix1] == "WIND" and metarInfo[ix1 + 1] == "BY":
                wind_rw = metarInfo[ix1 + 2][5:]
                wind_equipment = f"風向計測機器：RW{wind_rw}による風向観測"
                metarRet.append(wind_equipment)
                metarEng.append(f"{metarInfo[ix1]} {metarInfo[ix1 + 1]} {metarInfo[ix1 + 2]}")
                warning_flg.append(0)
                ix1 = ix1 + 2
        # #落雷情報
        #     elif metarInfo[ix1] == "TS" and metarInfo[ix1 + 1] == "HIT":
        #         ts_info = f"{metarInfo[ix1]} {metarInfo[ix1 + 1]} {metarInfo[ix1 + 2]} {metarInfo[ix1 + 3]} {metarInfo[ix1 + 4]}"
        #         ts_str = "＜雷情報＞"
        #         metarRet.append(ts_str)
        #         metarEng.append(ts_info)
        #         warning_flg.append(0)
        #         ts_str = "  場 所：地上観測所"
        #         metarRet.append(ts_str)
        #         metarEng.append(ts_info)
        #         warning_flg.append(0)
        #         ts_time_jst = PK0S0100.utc_to_jst([90,int(metarInfo[ix1 + 4][0:2]), int(metarInfo[ix1 + 4][2:4])])
        #         ts_str = f"  時間：{str(ts_time_jst[1])}:{str(ts_time_jst[2])}(JST)"
        #         metarRet.append(ts_str)
        #         metarEng.append(ts_info)
        #         warning_flg.append(0)
        #         ix1 = ix1 + 3
            ix1 = ix1 + 1
    except IndexError:
        return metarRet, metarEng, warning_flg, ix1
    
def get_cloud_rmk(inp_cloud):
    rmk_cloud = []
    cloud_amount_list = {
        "1": "1/8",
        "2": "2/8",
        "3": "3/8",
        "4": "4/8",
        "5": "5/8",
        "6": "6/8",
        "7": "7/8",
        "8": "8/8",
    }
    cloud_kind_list = {
        "CI": "巻雲",
        "CC": "巻積雲",
        "CS": "巻層雲",
        "AC": "高積雲",
        "AS": "高層雲",
        "NS": "乱層雲",
        "SC": "層積雲",
        "ST": "層雲",
        "CU": "積雲",
        "CB": "積乱雲",
        "TCU": "塔状積雲"
        }
    if inp_cloud[0:1] in cloud_amount_list:
        rmk_cloud.append(cloud_amount_list[inp_cloud[0:1]])
    if inp_cloud[1:3] in cloud_kind_list:
        rmk_cloud.append(cloud_kind_list[inp_cloud[1:3]])
        rmk_c_base = int(inp_cloud[3:6]) * 100
    elif inp_cloud[1:4] in cloud_kind_list:
        rmk_cloud.append(cloud_kind_list[inp_cloud[1:4]])
        rmk_c_base = int(inp_cloud[4:7]) * 100
    rmk_c_base_ft = int(rmk_c_base)
    rmk_c_base_m = str(PK0S0100.ft_to_m(rmk_c_base_ft)) + "m"
    rmk_cloud.append(rmk_c_base_m + "(" + str(rmk_c_base_ft) + "ft)")
    return rmk_cloud

def check_PIREP(input):
    pirep_flg = 0
    pirep_word = ["MOD", "FBL","LGT", "SEV", "EXTRM", "VIRGA", "ICE", "TURB", "GR", "BR", "TS", "TCU", "CB", "AND", "ABT", "WS"]
    if input in pirep_word:
        pirep_flg = 1
    else:
        pirep_flg = 0
    return pirep_flg