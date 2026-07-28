#PGM-ID:WX0S0206
#PGM-NAME:[P]WX欧式TREND

import PK0S0100
import WX0S0207

def get_trend(metarInfo, metarRet, metarEng, warning_flg, ix1):
    trend_eof = 0
    
    metarRet.append("")
    metarEng.append("")
    warning_flg.append(0)
    metarRet.append("～傾向型着陸予報(TREND)～")
    metarEng.append("")
    warning_flg.append(0)

    if metarInfo[ix1] == "NOSIG":
        metarRet.append("2時間以内に重要な変化なし(No Significant Change)")
        metarEng.append(metarInfo[ix1])
        warning_flg.append(0)
        ix1 = ix1 + 1
        return metarRet, metarEng, warning_flg, ix1
    wx_num = 1
    cloud_num = 1
    while trend_eof == 0:
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
        try:
        #変化群
            if metarInfo[ix1] == "TEMPO" or metarInfo[ix1] == "BECMG":
                if metarInfo[ix1] == "TEMPO":
                    metarRet.append("一時的に下記の状態になる")
                    metarEng.append(metarInfo[ix1])
                    warning_flg.append(0)      
                elif metarInfo[ix1] == "BECMG":
                    metarRet.append("下記の状態になる")
                    metarEng.append(metarInfo[ix1])
                    warning_flg.append(0)
        #対象時間
            elif metarInfo[ix1][0:2] == "FM" or metarInfo[ix1][0:2] == "AT" or metarInfo[ix1][0:2] == "TL":
                if metarInfo[ix1 + 1][0:2] == "FM" or metarInfo[ix1 + 1][0:2] == "AT" or metarInfo[ix1 + 1][0:2] == "TL":
                    trend_time_str1, trend_trend1 = get_trend_trend(metarInfo[ix1])
                    trend_time_str2, trend_trend2 = get_trend_trend(metarInfo[ix1 + 1])
                    metarRet.append("  対象時間：" + trend_time_str1 + trend_trend1 + trend_time_str2 + trend_trend2)
                    metarEng.append(metarInfo[ix1] + " " + metarInfo[ix1 + 1])
                    warning_flg.append(0)
                    ix1 = ix1 + 1
                else:
                    trend_time_str, trend_trend = get_trend_trend(metarInfo[ix1])
                    metarRet.append("  対象時間：" + trend_time_str + trend_trend)
                    metarEng.append(metarInfo[ix1])
                    warning_flg.append(0)
        #風向風速
            elif metarInfo[ix1].endswith("KT"):
                if metarInfo[ix1][0:5] == '00000':
                    windInfo = "  風    向：風なし"
                    metarRet.append(windInfo)
                    metarEng.append(metarInfo[ix1])
                    warning_flg.append(0)
                    windInfo = "  風    速：風なし"
                    metarRet.append(windInfo)
                    metarEng.append(metarInfo[ix1])
                    warning_flg.append(0)
                else:
                    wind_directs = metarInfo[ix1][0:3]
                    if wind_directs == 'VRB':
                        wind_direct = '不定'
                    else:
                        wind_direct = int(metarInfo[ix1][0:3])
                        wind_direct_x = PK0S0100.wind_direction(wind_direct)
                        wind_direct = str(wind_direct) + '度(' + wind_direct_x + ')からの風'
                    wind_direct_info = '  風    向：' + wind_direct
                    metarRet.append(wind_direct_info)
                    metarEng.append(metarInfo[ix1])  
                    warning_flg.append(0)
                    if metarInfo[ix1][5:6] == 'G':
                        wind_speed_kt = metarInfo[ix1][3:5]
                        wind_speed_ms = PK0S0100.kt_to_ms(int(wind_speed_kt))
                        wind_speed_gkt = metarInfo[ix1][6:8]
                        wind_speed_gms = PK0S0100.kt_to_ms(int(wind_speed_gkt))
                        wind_speed_info = '  風    速：' + str(wind_speed_kt) + 'kt' + '(' + str(wind_speed_ms) + 'm/s)'
                        metarRet.append(wind_speed_info)
                        metarEng.append(metarInfo[ix1])
                        warning_flg.append(1)
                        wind_speed_info_gust = '  ガスト  ：' + str(wind_speed_gkt) + 'kt' + '(' + str(wind_speed_gms) + 'm/s)'
                        metarRet.append(wind_speed_info_gust)
                        metarEng.append(metarInfo[ix1])
                        warning_flg.append(10) 
                    else:
                        wind_speed_kt = metarInfo[ix1][3:5]
                        wind_speed_ms = PK0S0100.kt_to_ms(int(wind_speed_kt))
                        wind_speed_info = '  風    速：' + str(wind_speed_kt) + 'kt' + '(' + str(wind_speed_ms) + 'm/s)'
                        metarRet.append(wind_speed_info)
                        metarEng.append(metarInfo[ix1])
                        warning_flg.append(1)
                    if metarInfo[ix1 + 1][3:4] == 'V':
                        wind_direct_1 = int(metarInfo[ix1][0:3])
                        wind_direct_2 = int(metarInfo[ix1][4:7])
                        wind_exInfo = '  風向変化：' + str(wind_direct_1) + '度～' + str(wind_direct_2) + '度で推移'
                        metarRet.append(wind_exInfo)
                        metarEng.append(metarInfo[ix1])
                        warning_flg.append(0)
                        ix1 = ix1 + 1
        #ｃａｖｏｋ
            elif metarInfo[ix1] == 'CAVOK':
                metarRet.append('  視    程：卓越視程10km以上')
                metarRet.append('    雲    ：5000ft以下に雲無し・かつ重要な対流雲がない')
                metarRet.append('  現在天気：なし')
                metarEng.append(metarInfo[ix1])
                metarEng.append(metarInfo[ix1])
                metarEng.append(metarInfo[ix1])
                warning_flg.append(0)
                warning_flg.append(0)
                warning_flg.append(0)

        #視程
            elif metarInfo[ix1].isdigit() and len(metarInfo[ix1]) == 4:
                visual = int(metarInfo[ix1])
                if visual == 9999:
                    metarRet.append("  視    程：10km以上")
                    metarEng.append(metarInfo[ix1])
                    warning_flg.append(0)
                elif visual == 0000:
                    metarRet.append("  視    程：100m未満")
                    metarEng.append(metarInfo[ix1])
                    warning_flg.append(4)
                else:
                    metarRet.append("  視    程：" + str(visual) + "m")
                    metarEng.append(metarInfo[ix1])
                    warning_flg.append(4)
        
        #気象現象
            elif metarInfo[ix1] == "NSW":
                metarRet.append("  気象現象：運航に支障のある気象現象が終了")
                metarEng.append(metarInfo[ix1])
                warning_flg.append(0)  

            elif metarInfo[ix1] == 'NSC' or metarInfo[ix1] == 'NSD' or metarInfo[ix1] == 'CLR' or metarInfo[ix1] == 'SKC':
                    skyClear = '  雲情報  ：雲無し'
                    metarRet.append(skyClear)
                    metarEng.append(metarInfo[ix1])
                    warning_flg.append(0)             

            elif str_flg == 1:
                wx_kyodo = 0
                if metarInfo[ix1][0:1] == '+':
                    wx_kyodo = 1
                    wx = metarInfo[ix1][1:]
                elif metarInfo[ix1][0:1] == '-':
                    wx_kyodo = 2
                    wx = metarInfo[ix1][1:]
                else:
                    wx = metarInfo[ix1]
                wx_info, retCd = WX0S0207.get_wx1(wx, 2)
                if retCd != 0:
                    if wx_kyodo == 1:
                        metar_str = '  気象現象' + str(wx_num) + '： 強い' + wx_info[1]
                    elif wx_kyodo == 2:
                        metar_str = '  気象現象' + str(wx_num) + '： 弱い' + wx_info[1]
                    else:
                        metar_str = '  気象現象' + str(wx_num) + '： ' + wx_info[1]
                wx_num = wx_num + 1
                metarRet.append(metar_str)
                metarEng.append(metarInfo[ix1])
                warning_flg.append(10) 

        #雲
            elif metarInfo[ix1][0:2] == 'VV':
                if metarInfo[ix1][2:5] == "///":
                    cloudInfo = "  垂直視程：不明"
                    warning_flg.append(0)
                else:
                    c_vis_ft = int(metarInfo[ix1][2:5]) * 100
                    c_vis_m = PK0S0100.ft_to_m(c_vis_ft)
                    cloudInfo = "  垂直視程：" + str(c_vis_ft) + "ft(" + str(c_vis_m) + ")m"
                    warning_flg.append(3)
                metarRet.append(cloudInfo)
                metarEng.append(metarInfo[ix1])
                    
            elif (len(metarInfo[ix1]) == 6 or len(metarInfo[ix1]) == 8 or len(metarInfo[ix1]) == 9) and str_flg == 2:
                try:
                    dummy = int(metarInfo[ix1][0:3])
                except ValueError:     
                    try:
                        dummy = metarInfo[ix1][3:6]
                        cloud_base = int(metarInfo[ix1][3:6])
                        cloud_amount = metarInfo[ix1][0:3]
                        if len(metarInfo[ix1]) == 8 or len(metarInfo[ix1]) == 9:
                            cloud_kind = metarInfo[ix1][6:]
                        else:
                            cloud_kind = ''
                        cloud_str = WX0S0207.get_cloudInfo(cloud_amount, cloud_base, cloud_kind, cloud_num)
                        metarRet.append(cloud_str)
                        metarEng.append(metarInfo[ix1])
                        warning_flg.append(3)
                        cloud_num = cloud_num + 1
                    except ValueError:
                        pass
            ix1 = ix1 + 1
            if metarInfo[ix1] == "RMK":
                return metarRet, metarEng, warning_flg, ix1
        except IndexError:
            return metarRet, metarEng, warning_flg, ix1
        
        
def get_trend_trend(inp_trend):
    utcTime = []
    jstTime = []
    if inp_trend[0:2] == "AT":
        trend_trend = ""
    elif inp_trend[0:2] == "FM":
        trend_trend = "から"
    elif inp_trend[0:2] == "TL":
        trend_trend = "までに"
    trend_time = inp_trend[2:]
    utcTime.append(0)
    utcTime.append(int(inp_trend[2:4]))
    utcTime.append(int(inp_trend[4:6]))
    jstTime = PK0S0100.utc_to_jst(utcTime)
    if jstTime[2] < 10:
        jstTimeM = '0' + str(jstTime[2])
    else:
        jstTimeM = str(jstTime[2])
    trend_time_str = str(jstTime[1]) + ':' + jstTimeM + '(JST)'
    return trend_time_str, trend_trend

