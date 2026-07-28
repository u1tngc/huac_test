#PGM-ID:WX0S0208
#PGM-NAME:[P]WX操縦士報告(PIREP)
#最終更新日:2026/01/02

import re

import PK0S0100
import WX0S0207

def translate_PIREP(metarInfo, metarRet, metarEng, warning_flg, ix1, pirep_num):
    """
     1:程度, 2:現象, 3:時刻, 4:場所, 5:高度, 6:状況, 7:機種
    """
    ix2 = ix1
    pirep_d_flg = 0
    pirep_v_flg = 0
    pirep_altitude_flg = 0

    wx = {
        "WS": "ウインドシア―",
        "TURB": "乱気流",
        "ICE": "着氷",
        "VIRGA": "尾流雲",
        "FG": "霧",
        "BR": "靄",
        "TCU": "塔状積雲",
        "CB": "積乱雲",
        "TS": "雷"
    }

    wx1 = {
        "WS": "ウインドシア―",
        "VIRGA": "尾流雲",
        "FG": "霧",
        "BR": "靄",
        "TCU": "塔状積雲",
        "CB": "積乱雲",
        "TS": "雷"
    }

    strength = {
        "FBL": "弱",
        "LGT": "弱",
        "MOD": "並",
        "SEV": "強",
        "EXTRM": "激しい"
    }
    try:
    #TURB ICE WS
        if metarInfo[ix2 + 1] == "TURB" or metarInfo[ix2 + 1] == "ICE" or metarInfo[ix2 + 3] == "TURB" or metarInfo[ix2 + 3] == "ICE" or (metarInfo[ix2] == "TS" and metarInfo[ix2 + 1] == "HIT") or metarInfo[ix2 + 1] == "WS" or metarInfo[ix2] == "WS":
            metarRet.append(f"＜報告等{pirep_num}＞")
            metarEng.append("")
            warning_flg.append(0)
            tiw_strength_flg = 0
            if metarInfo[ix2] == "TS" and metarInfo[ix2 + 1] == "HIT":
                pirep_tsHit = 1
                pirep_wx_jp = "雷の直撃"
                pirep_wx_eg = f"{metarInfo[ix2]} {metarInfo[ix2 + 1]} {metarInfo[ix2 + 2]}"
                ix2 = ix2 + 2
            else:
                pirep_tsHit = 0
                #強度
                if metarInfo[ix2] in strength:
                    tiw_strength_flg = 1
                    if metarInfo[ix2 + 1] == "TO":
                        pirep_strength_jp = strength[metarInfo[ix2]]
                        pirep_strength_jp = pirep_strength_jp + "から" + strength[metarInfo[ix2 + 2]] + "程度"
                        pirep_strength_eg = f"{metarInfo[ix2]} {metarInfo[ix2 + 1]} {metarInfo[ix2 + 2]} "
                        ix2 = ix2 + 3
                    else:
                        pirep_strength_jp = strength[metarInfo[ix2]] + "程度"
                        pirep_strength_eg = metarInfo[ix2]
                        ix2 = ix2 + 1
                #現象
                if metarInfo[ix2] in ("TURB", "ICE", "WS"):
                    if metarInfo[ix2 + 1] == "AND":
                        pirep_wx_jp = wx[metarInfo[ix2]] + "と" + wx[metarInfo[ix2 + 2]]
                        pirep_wx_eg = metarInfo[ix2] + " " + metarInfo[ix2 + 1] + " " + metarInfo[ix2 + 2]
                        ix2 = ix2 + 3
                    else:
                        pirep_wx_jp = wx[metarInfo[ix2]]
                        pirep_wx_eg = metarInfo[ix2]
                        ix2 = ix2 + 1
            metarRet.append(f"  現    象：{pirep_wx_jp}")
            metarEng.append(pirep_wx_eg)
            warning_flg.append(0)
            if pirep_tsHit == 0:
                if tiw_strength_flg == 1:
                    metarRet.append(f"  強    度：{pirep_strength_jp}")
                    metarEng.append(pirep_strength_eg)
                    warning_flg.append(0)
            ix2 = ix2 + 1

            #時刻
            if metarInfo[ix2] == "AT":
                utcTime = []
                jstTime = []
                utcTime.append(int(0))
                utcTime.append(int(metarInfo[ix2 + 1][0:2]))
                utcTime.append(int(metarInfo[ix2 + 1][2:4]))
                jstTime = PK0S0100.utc_to_jst(utcTime)
                if jstTime[2] < 10:
                    jstTimeM = '0' + str(jstTime[2])
                else:
                    jstTimeM = str(jstTime[2])
                metarRet.append(f"  報告時刻：{str(jstTime[1])}:{jstTimeM}(JST)") 
                metarEng.append(metarInfo[ix2] + " " + metarInfo[ix2 + 1])
                warning_flg.append(0)
                ix2 = ix2 + 2
            
            #場所
            pirep_abt = 0
            if metarInfo[ix2] == "ABT":
                pirep_abt = 1
                ix2 = ix2 + 1
            if metarInfo[ix2][-2:] == "NM": #距離
                pirep_d_eg = metarInfo[ix2]
                pirep_d = metarInfo[ix2][:-2]
                pirep_d_m = PK0S0100.nauticalMile_to_m(int(pirep_d))
                if pirep_abt == 1:
                    pirep_d_km = round(pirep_d_m/1000)
                    pirep_d_jp = "約" + str(pirep_d_km) + "km"
                else:
                    pirep_d_jp = str(pirep_d_m) + "m"
                ix2 = ix2 + 1
                pirep_d_flg = 1
            elif metarInfo[ix2][-2:] == "KM":
                pirep_d_jp = metarInfo[ix2]
                ix2 = ix2 + 1
                pirep_d_flg = 1
                
            if check_direction(metarInfo[ix2],1): #方角
                pirep_v_eg = metarInfo[ix2]
                pirep_v_jp = check_direction(metarInfo[ix2],2)
                ix2 = ix2 + 1
                pirep_v_flg = 1
            if pirep_v_flg == 1 and pirep_d_flg == 1:
                if pirep_abt == 1:
                    pirep_distance_en = "ABT " + pirep_d_eg + " " + pirep_v_eg
                else:
                    pirep_distance_en = pirep_d_eg + " " + pirep_v_eg
                pirep_distance_jp = "の" + pirep_d_jp + pirep_v_jp
            if pirep_v_flg == 1 and pirep_d_flg == 0:
                pirep_distance_en = pirep_v_eg
                pirep_distance_jp = "の" + pirep_v_jp 

            if metarInfo[ix2] == "AROUND" or metarInfo[ix2] == "OVER":
                if metarInfo[ix2] == "AROUND":
                    pirep_distance_en = metarInfo[ix2]
                    pirep_distance_jp = "の周辺"
                elif metarInfo[ix2] == "OVER":
                    pirep_distance_en = metarInfo[ix2]
                    pirep_distance_jp = "の上空"
                ix2 = ix2 + 1

            if metarInfo[ix2 + 1] == "TO":
                location_eg = metarInfo[ix2] + " " + metarInfo[ix2 + 2]
                location_jp_1 = get_location(metarInfo[ix2])
                location_jp_2 = get_location(metarInfo[ix2 + 2])
                location_jp = location_jp_1 + "から" + location_jp_2
                ix2 = ix2 + 2
            else:
                try:
                    location_jp = get_location(metarInfo[ix2]) + pirep_distance_jp
                    location_eg = pirep_distance_en + " " + metarInfo[ix2]
                except UnboundLocalError:
                    location_jp = get_location(metarInfo[ix2])
                    location_eg = metarInfo[ix2]
            metarRet.append(f"  観測場所：{location_jp}") 
            metarEng.append(location_eg)
            warning_flg.append(0)        
            ix2 = ix2 + 1

            #高度
            if metarInfo[ix2] == "BTN":
                #from
                pirep_altitude_f_eg = metarInfo[ix2] + " " + metarInfo[ix2 + 1] + " " + metarInfo[ix2 + 2]
                ix2 = ix2 + 1
                if metarInfo[ix2][-2:] == "FT":
                    pirep_altitude_f_m = PK0S0100.ft_to_m(int(metarInfo[ix2][:-2]))
                    pirep_altitude_f_jp = metarInfo[ix2] + "(" +str(pirep_altitude_f_m) + "m)"
                elif metarInfo[ix2][0:2] == "FL":
                    pirep_altitude_f_jp = "フライトレベル" + metarInfo[ix2][2:]
                ix2 = ix2 + 2
                #to
                pirep_altitude_t_eg = metarInfo[ix2]
                if metarInfo[ix2][-2:] == "FT":
                    pirep_altitude_t_m = PK0S0100.ft_to_m(int(metarInfo[ix2][:-2]))
                    pirep_altitude_t_jp = metarInfo[ix2] + "(" +str(pirep_altitude_t_m) + "m)"
                elif metarInfo[ix2][0:2] == "FL":
                    pirep_altitude_t_jp = "フライトレベル" + metarInfo[ix2][2:]
                ix2 = ix2 + 1
                pirep_altitude_eg = pirep_altitude_f_eg + " " + pirep_altitude_t_eg
                pirep_altitude_jp = pirep_altitude_f_jp + "から" + pirep_altitude_t_jp
                pirep_altitude_flg = 1
            elif metarInfo[ix2] == "ABV" or metarInfo[ix2] == "BLW":
                pirep_altitude_eg = metarInfo[ix2] + " " + metarInfo[ix2 + 1]
                ix2 = ix2 + 1
                if metarInfo[ix2][-2:] == "FT":
                    pirep_altitude_m = PK0S0100.ft_to_m(int(metarInfo[ix2][:-2]))
                    pirep_altitude_jp = metarInfo[ix2] + "(" +str(pirep_altitude_m) + "m)"
                elif metarInfo[ix2][0:2] == "FL":
                    pirep_altitude_jp = "フライトレベル" + metarInfo[ix2][2:]
                if metarInfo[ix2 - 1] == "ABV":
                    pirep_altitude_jp = pirep_altitude_jp + "以上"
                elif metarInfo[ix2 - 1] == "BLW":
                    pirep_altitude_jp = pirep_altitude_jp + "未満"
                ix2 = ix2 + 1
                pirep_altitude_flg = 1
            elif metarInfo[ix2][-2:] == "FT":
                pirep_altitude_eg = metarInfo[ix2]
                pirep_altitude_m = PK0S0100.ft_to_m(int(metarInfo[ix2][:-2]))
                pirep_altitude_jp = metarInfo[ix2] + "(" +str(pirep_altitude_m) + "m)"
                pirep_altitude_flg = 1
                ix2 = ix2 + 1
            elif metarInfo[ix2][0:2] == "FL":
                pirep_altitude_jp = "フライトレベル" + metarInfo[ix2][2:]
                pirep_altitude_eg = metarInfo[ix2]
                pirep_altitude_flg = 1
                ix2 = ix2 + 1
            if pirep_altitude_flg == 1:
                metarRet.append(f"  観測高度：{pirep_altitude_jp}") 
                metarEng.append(pirep_altitude_eg)
                warning_flg.append(0)

            #シチュエーション
            if metarInfo[ix2] == "INC" or metarInfo[ix2] == "IN":
                if metarInfo[ix2] == "INC":
                    pirep_situation_eg = metarInfo[ix2]
                    pirep_situation_jp = "雲の中"
                elif metarInfo[ix2 + 1] == "CMB": 
                    pirep_situation_eg = metarInfo[ix2] + " " + metarInfo[ix2 + 1]
                    pirep_situation_jp = "上昇中"
                    ix2 = ix2 + 1
                elif metarInfo[ix2 + 1] == "DES": 
                    pirep_situation_eg = metarInfo[ix2] + " " + metarInfo[ix2 + 1]
                    pirep_situation_jp = "下降中"
                    ix2 = ix2 + 1
                metarRet.append(f"  飛行状態：{pirep_situation_jp}") 
                metarEng.append(pirep_situation_eg)
                warning_flg.append(0)   
                ix2 = ix2 + 1  

            #報告機種
            if metarInfo[ix2] == "BY":
                pirep_aircraft_eg = metarInfo[ix2] + " " + metarInfo[ix2 + 1]
                pirep_aircraft_jp = WX0S0207.get_aircraft(metarInfo[ix2 + 1])
                ix2 = ix2 + 1
            else:
                pirep_aircraft_eg = metarInfo[ix2] 
                pirep_aircraft_jp = WX0S0207.get_aircraft(metarInfo[ix2])
            metarRet.append(f"  報告機種：{pirep_aircraft_jp}") 
            metarEng.append(pirep_aircraft_eg)
            warning_flg.append(0)   
            ix1 = ix2
            return metarRet, metarEng, warning_flg, ix1
    except IndexError:
        pass   
    if metarInfo[ix2] in wx1 or metarInfo[ix2 + 1] in wx1:
        try:
            pirep_strength_flg = 0
            metarRet.append(f"＜報告等{pirep_num}＞")
            metarEng.append("")
            warning_flg.append(0)
            #程度
            if metarInfo[ix2] in strength:
                pirep_strength_eg = metarInfo[ix2]
                pirep_strength_jp = strength[metarInfo[ix2]] + "程度"
                ix2 = ix2 + 1
                pirep_strength_flg = 1
            #現象
            pirep_wx_jp = wx1[metarInfo[ix2]]
            pirep_wx_eg = metarInfo[ix2]
            metarRet.append(f"  現    象：{pirep_wx_jp}") 
            metarEng.append(pirep_wx_eg)
            warning_flg.append(0)  
            ix2 = ix2 + 1
            if metarInfo[ix2] == "OBS":
                ix2 = ix2 + 1
            if pirep_strength_flg == 1:
                metarRet.append(f"  強    度：{pirep_strength_jp}") 
                metarEng.append(pirep_strength_eg)
                warning_flg.append(0)  
            #場所
            pirep_abt = 0
            if metarInfo[ix2] == "ABT":
                pirep_abt = 1
                ix2 = ix2 + 1
            if metarInfo[ix2] == "OHD":
                pirep_location_eg = metarInfo[ix2]
                pirep_location_jp = "空港上空"
                metarRet.append(f"  場    所：{pirep_location_jp}") 
                metarEng.append(pirep_location_eg)
                warning_flg.append(0) 
                ix2 = ix2 + 1 
            elif metarInfo[ix2] == "ALL" and metarInfo[ix2 + 1] == "QUAD":
                pirep_location_eg = f"{metarInfo[ix2]} {metarInfo[ix2 + 1]}"
                pirep_location_jp = "全方位(4象限すべて)"
                metarRet.append(f"  場    所：{pirep_location_jp}") 
                metarEng.append(pirep_location_eg) 
                warning_flg.append(0) 
                ix2 = ix2 + 2
            elif metarInfo[ix2][-2:] == "NM" or metarInfo[ix2][-2:] == "KM":
                pirep_distance_eg = metarInfo[ix2]
                if metarInfo[ix2][-2:] == "NM":
                    if pirep_abt == 1:
                        pirep_distance_m = PK0S0100.nauticalMile_to_m(int(metarInfo[ix2][:-2]))
                        pirep_distance_jp = f"約{str(round(pirep_distance_m/1000))}km"
                    else:
                        pirep_distance_m = PK0S0100.nauticalMile_to_m(int(metarInfo[ix2][:-2]))
                        pirep_distance_jp = f"{str(pirep_distance_m)}m"
                elif metarInfo[ix2][-2:] == "KM":
                    if pirep_abt == 1:
                        pirep_distance_km = int(metarInfo[ix2][:-2])
                        pirep_distance_jp = f"約{round(pirep_distance_km)}km"
                    else:
                        pirep_distance_km = int(metarInfo[ix2][:-2])
                        pirep_distance_jp = f"{round(pirep_distance_km)}km"
                if len(metarInfo[ix2 + 1]) >= 3 and metarInfo[ix2 + 1] != "UNKNOWN":
                    pirep_direct_f1, pirep_direct_f2 = metarInfo[ix2 + 1].split("-")
                    pirep_direct_f1_jp = check_direction(pirep_direct_f1, 2)
                    pirep_direct_f2_jp = check_direction(pirep_direct_f2, 2)
                    pirep_direct_f_jp = pirep_direct_f1_jp + "～" + pirep_direct_f2_jp
                    pirep_direct_f_eg = metarInfo[ix2 + 1]
                else:
                    pirep_direct_f_jp = check_direction(metarInfo[ix2 + 1], 2)
                    pirep_direct_f_eg = metarInfo[ix2 + 1]
                metarRet.append(f"  場    所：空港から{pirep_distance_jp}{pirep_direct_f_jp}") 
                if pirep_abt == 1:
                    metarEng.append("ABT " + pirep_distance_eg + " " + pirep_direct_f_eg)
                else:
                    metarEng.append(pirep_distance_eg + " " + pirep_direct_f_eg)
                warning_flg.append(0) 
                ix2 = ix2 + 2
                if len(metarInfo) < ix2:
                    raise IndexError
            if re.search(metarInfo[ix2],"-"):
                pirep_direct_f1, pirep_direct_f2 = metarInfo[ix2].split("-")
                pirep_direct_f1_jp = check_direction(pirep_direct_f1, 2)
                pirep_direct_f2_jp = check_direction(pirep_direct_f2, 2)
                pirep_direct_f_jp = pirep_direct_f1_jp + "～" + pirep_direct_f2_jp
                pirep_direct_f_eg = metarInfo[ix2]
                metarRet.append(f"  場    所：空港の{pirep_direct_f_jp}") 
                metarEng.append(pirep_direct_f_eg)
                warning_flg.append(0) 
                ix2 = ix2 + 1
                if len(metarInfo) < ix2:
                    raise IndexError
            elif check_direction(metarInfo[ix2],1):
                pirep_direct_f_jp = check_direction(metarInfo[ix2], 2)
                pirep_direct_f_eg = metarInfo[ix2]
                metarRet.append(f"  場    所：空港の{pirep_direct_f_jp}") 
                metarEng.append(pirep_direct_f_eg)
                warning_flg.append(0) 
                ix2 = ix2 + 1
                if len(metarInfo) < ix2:
                    raise IndexError
            #状況
            if metarInfo[ix2] == "STNR":
                metarRet.append(f"  状    況：停滞") 
                metarEng.append(metarInfo[ix2])
                warning_flg.append(0) 
                ix2 = ix2 + 1
            elif metarInfo[ix2] == "MOV":
                pirep_situation_eg = metarInfo[ix2]
                ix2 = ix2 + 1
                if check_direction(metarInfo[ix2],1):
                    pirep_direct_t_jp = check_direction(metarInfo[ix2],2)
                    pirep_situation_eg = pirep_situation_eg + " " + metarInfo[ix2]
                    metarRet.append(f"  状    況：{pirep_direct_t_jp}へ移動") 
                    metarEng.append(pirep_situation_eg)
                    warning_flg.append(0) 
                    ix2 = ix2 + 1
                elif metarInfo[ix2] == "UNKNOWN":
                    pirep_situation_eg = pirep_situation_eg + " " + metarInfo[ix2]
                    metarRet.append(f"  状    況：移動方向不明") 
                    metarEng.append(pirep_situation_eg)
                    warning_flg.append(0) 
                    ix2 = ix2 + 1
                elif re.search(metarInfo[ix2],"-"):
                    pirep_direct_t1, pirep_direct_t2 = metarInfo[ix2].split("-")
                    pirep_direct_t1_jp = check_direction(pirep_direct_t1, 2)
                    pirep_direct_t2_jp = check_direction(pirep_direct_t2, 2)
                    pirep_direct_t_jp = pirep_direct_t1_jp + "～" + pirep_direct_t2_jp
                    pirep_situation_eg = pirep_situation_eg + " " + metarInfo[ix2]
                    metarRet.append(f"  状    況：{pirep_direct_t_jp}へ移動") 
                    metarEng.append(pirep_situation_eg)
                    warning_flg.append(0) 
                    ix2 = ix2 + 1         
        except IndexError:
            ix1 = len(metarInfo) - 1
            return metarRet, metarEng, warning_flg, ix1 
      
        ix1 = ix2
        return metarRet, metarEng, warning_flg, ix1 - 1

def check_direction(input_d, kino_cd):
    direction_list = {
        "N": "北",
        "NE": "北東",
        "E": "東",
        "SE": "南東",
        "S": "南",
        "SW": "南西",
        "W": "西",
        "NW": "北西",
        "UNKNOWN" : "（方角不明）"
    }
    if input_d in direction_list:
        if kino_cd == 1:
            return True
        elif kino_cd == 2:
            ret_d = direction_list[input_d]
            return ret_d
    else:
        if kino_cd == 1:
            return False
        elif kino_cd == 2:
            return ""

def get_location(input_location):
    location_list = {
        "HME": "羽田(VOR/DME)",
        "NRE": "成田(VOR/DME)",
        "HANEDA": "東京国際空港",
        "NARITA": "成田国際空港",
        "NHC": "那覇(VOLTAC)",
        "XAC": "大島(VOR/TACAN)",
        "OSHIMA": "大島空港",
        "TATEYAMA": "館山航空基地(JMSDF)",
    }
    if input_location in location_list:
        ret_location = location_list[input_location]
    else:
        if input_location[0:3] == "RWY":
            ret_location = input_location
        elif len(input_location) == 3:
            ret_location = input_location + "(VOR/DME等)"
        elif len(input_location) == 5:
            ret_location = input_location + "(WAYポイント)"
        else:
            ret_location = WX0S0207.get_location(input_location)
    return ret_location