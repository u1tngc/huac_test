#PGM-ID:PK0S0100
#PGM-NAME:[P]単位換算
#最終更新日:

import calendar
import datetime
import math

"""
関数名：utc_to_jst
引　数：utcTime[dd(int), hh(int), mm(int)]
戻り値：jstTime[dd(int), hh(int), mm(int)]
概　要：UTCを受け取り、JSTに変換して戻す。
"""
def utc_to_jst(utcTime):
    today = datetime.date.today()
    lastDay = calendar.monthrange(today.year, today.month)[1]
    jstTime = []
    jstTime.append(utcTime[0])
    jsthour = utcTime[1] + 9
    if jsthour >= 24:
        jstTime[0] = jstTime[0] + 1
        if  jstTime[0] > lastDay:
            jstTime[0] = 1
        jsthour = jsthour - 24
    jstTime.append(jsthour)
    jstTime.append(utcTime[2])
    return jstTime

"""
関数名：wind_direction
引　数：wind_direct(int)
戻り値：wind_direct_x(str)
概　要：360度式で風向を受け取り、8方位に変換して戻す。
"""
def wind_direction(wind_direct):
    if wind_direct <= 22.5 or wind_direct > 337.5:
        wind_direct_x = '北'
    elif 22.5 < wind_direct <= 67.5:
        wind_direct_x = '北東'
    elif 67.5 < wind_direct <= 112.5:
        wind_direct_x = '東'
    elif 112.5 < wind_direct <= 157.5:
        wind_direct_x = '南東'
    elif 157.5 < wind_direct <= 202.5:
        wind_direct_x = '南'
    elif 202.5 < wind_direct <=247.5:
        wind_direct_x = '南西'
    elif 247.5 < wind_direct <= 292.5:
        wind_direct_x = '西'
    elif 292.5 < wind_direct <= 337.5:
        wind_direct_x = '北西'
    return wind_direct_x

"""
関数名：kt_to_ms
引　数：wind_speed.kt(int)
戻り値：wind_speed_ms(float)
概　要：ktをm/sに変換
"""
def kt_to_ms(wind_speed_kt):
    wind_speed = float(wind_speed_kt) * 0.51444
    wind_speed_ms = round(wind_speed, 1)
    return wind_speed_ms

"""
関数名：statueMile_to_m
引　数：statueMile(int)
戻り値：metre(int)
概　要：陸マイルをメートルに変換
"""
def statueMile_to_m(statueMile):
    metre = int(statueMile * 1609.347)
    return metre

"""
関数名：inHg_to_hPa
引　数：inHg(float) 99.99
戻り値：hPa(float) 9999.9
概　要：水銀柱ｉｎｃｈをｈＰａに変換
"""
def inHg_to_hPa(inHg):
    hPa = round((inHg * 33.8638864), 1)
    return hPa

"""
関数名：inch_to_mm
引　数：inHg(float) 999.9
戻り値：mm(float) 9999
概　要：ｉｎｃｈをｍｍに変換
"""
def inch_to_mm(inch):
    mm = round(inch * 25.4,1)
    return mm

"""
関数名：calculate_humidity
引　数：dew_point(float) 99.9, temperature(float) 99.9
戻り値：humidity(float) 99.9
概　要：露点と気温から湿度を算出
"""
def calculate_humidity(dew_point, temperature):
    # 飽和水蒸気圧を計算する関数
    def saturation_vapor_pressure(T):
        return 6.1078 * 10 ** ((7.5 * T) / (237.3 + T))

    # 露点温度から飽和水蒸気圧を計算
    dew_point_pressure = saturation_vapor_pressure(dew_point)
    # 気温から飽和水蒸気圧を計算
    temperature_pressure = saturation_vapor_pressure(temperature)
    
    # 相対湿度を計算
    humidity = (dew_point_pressure / temperature_pressure) * 100
    return humidity

"""
関数名：ft_to_m
引　数：ft(int) 99900
戻り値：m(int) 9999
概　要：ｆｔをｍに変換
"""
def ft_to_m(ft):
    m = int(ft * 0.3048)
    return m

"""
関数名：dmm_to_d
引　数：latitude(float) 99.9999, longitude(float) 999.9999
戻り値：latitude(float) 9999.9999, longitude(float) 99999.9999
概　要
"""
def dmm_to_d(latitude, longitude):
    decimal, integer = math.modf(latitude/100.0)
    ret_latitde = integer + decimal / 60.0 * 100.0

    decimal, integer = math.modf(longitude/100.0)
    ret_longitude = integer + decimal / 60.0 * 100.0

    return ret_latitde, ret_longitude

"""
関数名：nauticalMile_to_m
引　数：nauticalMile(int)
戻り値：metre(int)
概　要：陸マイルをメートルに変換
"""
def nauticalMile_to_m(statueMile):
    metre = statueMile * 1852
    return metre

def timeCheck(currentDateTime,kino_cd):
    #現在時刻の取得
    currentTime = currentDateTime.time()
    if kino_cd == 1:
        time0900 = datetime.time(13,00,00) #高層天気図0900の更新時間
        time2100 = datetime.time(1,00,00) #高層天気図2100の更新時間
        time0000 = datetime.time(0,00,00)
        time0300 = datetime.time(5,45,00) #地上天気図0300の更新時間
        if currentTime > time2100 and currentTime < time0900:
            timeKbn = 21 #2100
        elif currentTime > time0000 and currentTime < time2100:
            timeKbn = 90 #0900
        else:
            timeKbn = 9 #0900
        return timeKbn
    elif kino_cd == 2:
        time2100 = datetime.time(23,45,00) #地上天気図2100の更新時間
        time0300 = datetime.time(5,45,00) #地上天気図0300の更新時間
        if currentTime > time2100 or currentTime < time0300:
            timeKbn = 21 #2100
        else:
            timeKbn = 3 #0900
    elif kino_cd == 3:
        time0900 = datetime.time(13,45,00) #2100の更新時間
        time2100 = datetime.time(1,45,00) #0900の更新時間
        if currentTime > time2100 and currentTime < time0900:
            timeKbn = 21 #2100
        else:
            timeKbn = 9 #0900
        return timeKbn