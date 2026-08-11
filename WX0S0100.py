#PGM-ID:WX0S0100
#PGM-NAME:[P]WX天気取得
#最終更新日:

from datetime import datetime, timedelta, timezone
import math
import requests

import PK0S0100
import WX0S0101
import WX0S0102


def getWx(kinocd,postCode, filename,path):
    title = []
    now_weather1 = []
    now_weather2 = []
    forecast = []
    if kinocd == 1 or 2: #1 自家用　2教証・取得郵便　3取得都市名
        title, now_weather1, now_weather2 = get_weather(title, now_weather1, now_weather2, postCode, kinocd)
        title, forecast = get_forecast(title,forecast,postCode, kinocd)
    else:
        title, now_weather1, now_weather2 = get_weather(title, now_weather1, now_weather2, postCode, kinocd)
        title, forecast = get_forecast(title,forecast,postCode, kinocd)
    url = get_asas()
    title.append(url)
    if kinocd == 3:
        kinocd = 2
    html_name = WX0S0102.wxGaikyo_html(title, now_weather1, now_weather2, forecast, kinocd, filename,path)
    return html_name

def get_weather(title, now_weather1, now_weather2, postCode, kinocd):
    if kinocd == 3:
        weather_data = get_wxJson(3, postCode)
    else:
        weather_data = get_wxJson(1, postCode)
    location = weather_data["name"]
    title.append(location)
    arr_time = unix_to_jst(weather_data["dt"],1)
    title.append("現在天気")
    arr_str1 = str(arr_time) + "時点"
    arr_str2 = ""
    now_weather1, now_weather2 = add_arr(now_weather1, now_weather2, arr_str1, arr_str2)

    arr_wx = WX0S0101.get_wx(str(weather_data["weather"][0]["id"]),1)
    arr_str1 = "現在天気"
    arr_str2 = arr_wx
    now_weather1, now_weather2 = add_arr(now_weather1, now_weather2, arr_str1, arr_str2)

    arr_icon = weather_data["weather"][0]["id"]
    arr_str1 = "アイコン"
    arr_str2 = WX0S0101.get_wx(arr_icon, 2)
    now_weather1, now_weather2 = add_arr(now_weather1, now_weather2, arr_str1, arr_str2)

    arr_wind_d = PK0S0100.wind_direction(weather_data["wind"]["deg"])
    arr_str1 = "風向"
    arr_str2 = arr_wind_d
    now_weather1, now_weather2 = add_arr(now_weather1, now_weather2, arr_str1, arr_str2)

    arr_wind_s1 = weather_data["wind"]["speed"]
    arr_wind_s2 = rounds(arr_wind_s1,1)
    arr_wind_s2 = getWindSpeedIndex(arr_wind_s2)
    arr_str1 = "風速"
    arr_str2 = arr_wind_s2 + "m/s"
    now_weather1, now_weather2 = add_arr(now_weather1, now_weather2, arr_str1, arr_str2)

    try:
        arr_wind_g1 = weather_data["wind"]["gust"]
        arr_wind_g2 = rounds(arr_wind_g1,1)
        arr_wind_g2 = getWindSpeedIndex(arr_wind_g2)
        arr_str1 = "ガスト"
        arr_str2 = arr_wind_g2 + "m/s"
        now_weather1, now_weather2 = add_arr(now_weather1, now_weather2, arr_str1, arr_str2)
    except KeyError:
        pass

    try:
        arr_rain = weather_data["rain"]["1h"]
        arr_str1 = "1h雨量"
        arr_str2 = str(arr_rain) + "mm"
        now_weather1, now_weather2 = add_arr(now_weather1, now_weather2, arr_str1, arr_str2)
    except KeyError:
        arr_str1 = "1h雨量"
        arr_str2 = "-"
        now_weather1, now_weather2 = add_arr(now_weather1, now_weather2, arr_str1, arr_str2)

    arr_vis = str(weather_data["visibility"])
    if arr_vis == "10000":
        arr_str1 = "視程"
        arr_str2 = "10km以上"
    else:
        arr_str1 = "視程"
        arr_str2 = arr_vis
    now_weather1, now_weather2 = add_arr(now_weather1, now_weather2, arr_str1, arr_str2)

    arr_temp = weather_data["main"]["temp"]
    arr_humidity = weather_data["main"]["humidity"]
    arr_dew1 = dew_point(arr_temp, arr_humidity)
    arr_dew2 = rounds(arr_dew1,1)
    arr_cd1 = (arr_temp - arr_dew2) * 125
    arr_cd2 = int(rounds(arr_cd1,0))
    arr_str1 = "雲底高度"
    arr_str2 = str(arr_cd2)
    now_weather1, now_weather2 = add_arr(now_weather1, now_weather2, arr_str1, arr_str2)

    arr_str1 = "気温"
    arr_str2 = str(int(rounds(arr_temp,0))) + "℃"
    now_weather1, now_weather2 = add_arr(now_weather1, now_weather2, arr_str1, arr_str2)

    arr_str1 = "湿度"
    arr_str2 = str(arr_humidity) + "％"
    now_weather1, now_weather2 = add_arr(now_weather1, now_weather2, arr_str1, arr_str2)

    try:
        arr_pressure = str(weather_data["main"]["grnd_level"])
        arr_str1 = "地上気圧"
        arr_str2 = arr_pressure + "hPa"
    except KeyError:
        arr_pressure = str(weather_data["main"]["pressure"])
        arr_str1 = "気圧"
        arr_str2 = arr_pressure + "hPa"
    now_weather1, now_weather2 = add_arr(now_weather1, now_weather2, arr_str1, arr_str2)

    arr_sunsetT = unix_to_jst(weather_data["sys"]["sunset"],2)
    arr_str1 = "日没時間"
    arr_str2 = arr_sunsetT
    now_weather1, now_weather2 = add_arr(now_weather1, now_weather2, arr_str1, arr_str2)

    now_weather1, now_weather2 = add_arr(now_weather1, now_weather2, '@', '@')

    return title, now_weather1, now_weather2

def get_forecast(title, forecast, postCode, kinocd):
    title.append("予報天気")
    forecast_arr1 = ['予報時刻','天気','アイコン','風向','風速','ガスト','3h雨量','視程','雲底高度','気温','湿度','気圧']
    forecast.append(forecast_arr1)
    if kinocd == 3:
        weather_data = get_wxJson(4,postCode)
    else:
        weather_data = get_wxJson(2,postCode)
    ix1 = 0
    eof = 0
    while eof == 0:
        forecast_arr = []
        try:
            #時間
            arr_str = unix_to_jst(weather_data["list"][ix1]["dt"],1)
            forecast_arr.append(str(arr_str))
            #天気
            arr_str = WX0S0101.get_wx(str(weather_data["list"][ix1]["weather"][0]["id"]),1)
            forecast_arr.append(str(arr_str))
            #アイコン
            arr_str = WX0S0101.get_wx(str(weather_data["list"][ix1]["weather"][0]["id"]),2)
            forecast_arr.append(str(arr_str))
            #風向
            arr_str = PK0S0100.wind_direction(weather_data["list"][ix1]["wind"]["deg"])
            forecast_arr.append(str(arr_str))
            #風速
            arr_wind_s1 = weather_data["list"][ix1]["wind"]["speed"]
            arr_wind_s2 = rounds(arr_wind_s1,1)
            arr_wind_s2 = getWindSpeedIndex(arr_wind_s2)
            arr_str = arr_wind_s2 + "m/s"
            forecast_arr.append(str(arr_str))
            #ガスト
            try:
                arr_wind_g1 = weather_data["list"][ix1]["wind"]["gust"]
                arr_wind_g2 = rounds(arr_wind_g1,1)
                arr_wind_g2 = getWindSpeedIndex(arr_wind_g2)
                arr_str = arr_wind_g2 + "m/s"
                forecast_arr.append(str(arr_str))
            except KeyError:
                forecast_arr.append("-")
            #3h雨量
            try:
                arr_rain3 = str(weather_data["list"][ix1]["rain"]["3h"]) + "mm"
                forecast_arr.append(arr_rain3)
            except KeyError:
                forecast_arr.append("-")
            #視程
            try:
                arr_vis = str(weather_data["list"][ix1]["visibility"])
                if arr_vis == "10000":
                    arr_str = "10km以上"
                else:
                    arr_str = arr_vis
                forecast_arr.append(str(arr_str))
            except KeyError:
                forecast_arr.append("-")
            #雲底
            arr_temp = weather_data["list"][ix1]["main"]["temp"]
            arr_humidity = weather_data["list"][ix1]["main"]["humidity"]
            arr_dew1 = dew_point(arr_temp, arr_humidity)
            arr_dew2 = rounds(arr_dew1,1)
            arr_cd1 = (arr_temp - arr_dew2) * 125
            arr_cd2 = int(rounds(arr_cd1,0))
            arr_str = str(arr_cd2)
            forecast_arr.append(str(arr_str))
            #気温
            arr_str = str(int(rounds(arr_temp,0))) + "℃"
            forecast_arr.append(str(arr_str))
            #湿度
            arr_str = str(arr_humidity) + "％"
            forecast_arr.append(str(arr_str))
            #気圧
            try:
                arr_pressure = str(weather_data["list"][ix1]["main"]["grnd_level"])
                arr_str = arr_pressure + "hPa"
            except KeyError:
                arr_pressure = str(weather_data["list"][ix1]["main"]["pressure"])
                arr_str = arr_pressure + "hPa"
            forecast_arr.append(str(arr_str))
            forecast.append(forecast_arr)
            ix1 += 1
        except IndexError:
            eof = 1
    return title, forecast

def get_asas():
    now_jst = datetime.now()
    now_utc = now_jst + timedelta(hours = -9)
    comp1 = datetime(now_utc.year, now_utc.month, now_utc.day, 23, 30)
    for ix1 in range(8):
        comp = datetime(now_utc.year, now_utc.month, now_utc.day, 2 + 3 * ix1, 30)
        if now_utc < comp:
            if ix1 == 0:
                comp = comp + timedelta(days=-1)
                url_year = comp.strftime("%Y")
                url_month = comp.strftime("%m")
                url_day = comp.strftime("%d")
                url_hour = '21'
            else:
                url_year = now_utc.strftime("%Y")
                url_month = now_utc.strftime("%m")
                url_day = now_utc.strftime("%d")
                url_hour = str(3 * (ix1 - 1))
                if len(url_hour) == 1:
                    url_hour = '0' + url_hour
            break
        if comp1 <= now_utc:
            url_year = comp.strftime("%Y")
            url_month = comp.strftime("%m")
            url_day = comp.strftime("%d")
            url_hour = '21'
            break
    if url_hour == '15':
        url_hour = '12'
    url1 = str(url_year) + str(url_month)
    url2 = str(url_year) + str(url_month) + str(url_day) + str(url_hour) + "00"
    url = "https://www.data.jma.go.jp/fcd/yoho/data/wxchart/quick/" + url1 + "/SPAS_COLOR_" + url2 + ".png"
    return url

def get_wxJson(flg, postCode):
    api_key = "813610f17fcad78884866e8e0a0b1bd1"
    zip_place = postCode
    city_name = postCode
    lang = "ja"
    if flg == 1:
        url = f"https://api.openweathermap.org/data/2.5/weather?zip={zip_place}&units=metric&appid={api_key}&lang={lang}"
    elif flg == 2:
        url = f"https://api.openweathermap.org/data/2.5/forecast?zip={zip_place}&units=metric&appid={api_key}&lang={lang}"
    elif flg == 3:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city_name}&units=metric&appid={api_key}&lang={lang}"
    elif flg == 4:
        url = f"https://api.openweathermap.org/data/2.5/forecast?q={city_name}&units=metric&appid={api_key}&lang={lang}"
    response = requests.get(url)
    data = response.json()
    return data

def unix_to_jst(unix, kinoCd):
    JST = timezone(timedelta(hours=+9), 'JST')
    # Unix時間をdatetimeオブジェクトに変換
    jst_time = datetime.fromtimestamp(unix, JST)
    # UTC時間から日本時間に変換
    if kinoCd == 1:
        jst_datetime = jst_time.strftime("%d日 %H:%M")
    elif kinoCd == 2:
        jst_datetime = jst_time.strftime("%H:%M")
    else:
        jst_datetime = jst_time.strftime("%m/%d %H:%M")
    return jst_datetime

def rounds(num, keta):
    if keta == 1:
        ret = round(num, 1)
    elif keta == 0:
        ret = round(num, 0)
    return ret

def dew_point(temperature, humidity):
    a = 17.625
    b = 243.04
    # 露点温度を計算
    dew_temp = b * (math.log(humidity / 100) + ((a * temperature) / (b + temperature))) / (a - (math.log(humidity / 100) + ((a * temperature) / (b + temperature))))
    return dew_temp

def add_arr(arr1, arr2, str1, str2):
    arr1.append(str1)
    arr2.append(str2)
    return arr1, arr2

def getWindSpeedIndex(arr_wind):
    if arr_wind <= 3.9:
        wind_str = 'A' + str(arr_wind)
    elif arr_wind >= 4 and arr_wind <= 6.9:
        wind_str = 'B' + str(arr_wind)
    elif arr_wind >= 7 and arr_wind <= 9.9:
        wind_str = 'C' + str(arr_wind)
    elif arr_wind >= 10:
        wind_str = 'D' + str(arr_wind)
    return wind_str