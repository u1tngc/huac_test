#PGM-ID:WX0S0102
#PGM-NAME:[P]WX天気概況html
#最終更新日:

import datetime
import os
import webbrowser


def wxGaikyo_html(title, now_weather1, now_weather2, forecast,kinocd, nowdate,path):
    text = make_head()
    text += make_body(title, now_weather1, now_weather2, forecast,kinocd)
    text += make_bottom()
    fileName = convertToPdf(text, nowdate,path)
    return fileName

def make_head():
    html = []
    html.append('<!DOCTYPE html>')
    html.append('<html lang="ja">')
    html.append('<head>')
    html.append('<title>気象概況</title>')
    html.append('<meta charset="UTF-8">')
    html.append('<meta http-equiv="X-UA-Compatible" content="IE=edge" />')
    html.append('<meta name="viewport" content="width=device-width, initial-scale=1.0" />')
    html.append('<link rel="stylesheet" type="text/css" href="./fonts/WX0C0001.css" /> ')
    html.append('<style>')
    html.append('@font-face {')
    html.append('font-family: "japanese";')
    html.append('src: url(fonts/GenShinGothic-Monospace-Medium.ttf);')
    html.append('}')
    html.append('body{')
    html.append('font-family: "japanese"')
    html.append('}')
    html.append('</style>')
    html.append('</head>')
    text = ''
    for ix1 in range(len(html)):
        text += html[ix1]
    return text

def make_body(title, now_weather1, now_weather2, forecast,kinocd):
    html = []
    num = 0
    eof_flg = 0
    html.append('<body>')
    html.append('<h1>天気概況</h1>')
    html.append('<h2>' + title[1] + '</h2>')
    html.append('<table border="1" class=table>')
    num += 1
    while eof_flg == 0:
        if now_weather1[num] == '@':
            html.append('</table>') 
            num += 1
            break
        html.append('<tr>')
        html.append('<th>' + str(now_weather1[num]) + '</th>')
        if now_weather1[num] == '風速' or now_weather1[num] == 'ガスト':
            if now_weather2[num][0:1] == 'A':
                html.append('<td class=blue>' + str(now_weather2[num][1:]) + '</td>')
            elif now_weather2[num][0:1] == 'B':
                html.append('<td class=orange>' + str(now_weather2[num][1:]) + '</td>')
            elif now_weather2[num][0:1] == 'C':
                html.append('<td class=red>' + str(now_weather2[num][1:]) + '</td>')
            elif now_weather2[num][0:1] == 'D':
                html.append('<td class=purple>' + str(now_weather2[num][1:]) + '</td>')
        elif now_weather1[num] == 'アイコン':
            html.append('<td class=tdIcon><img src="' + now_weather2[num] + '" alt="NULL"></td>')
        elif now_weather1[num] == '気温':
            try:
                if int(now_weather2[num][0:2]) >= 31:
                    html.append('<td class=purple>' + str(now_weather2[num]) + '</td>')
                elif int(now_weather2[num][0:2]) < 31 and int(now_weather2[num][0:2]) >= 28:
                    html.append('<td class=red>' + str(now_weather2[num]) + '</td>')
                elif int(now_weather2[num][0:2]) < 28 and int(now_weather2[num][0:2]) >= 25:
                    html.append('<td class=orange>' + str(now_weather2[num]) + '</td>')
                else:
                    html.append('<td>' + str(now_weather2[num]) + '</td>')
            except ValueError:
                html.append('<td>' + str(now_weather2[num]) + '</td>')
        elif now_weather1[num] == '視程':
            try:
                if int(now_weather2[num]) < 1500:
                    html.append('<td class=purple>' + str(now_weather2[num]) + 'm</td>')
                elif int(now_weather2[num]) >= 1500 and int(now_weather2[num]) < 5000:
                    html.append('<td class=red>' + str(now_weather2[num]) + 'm</td>')
                elif int(now_weather2[num]) >= 5000 and int(now_weather2[num]) < 10000:
                    html.append('<td class=orange>' + str(now_weather2[num]) + 'm</td>')
            except ValueError:
                html.append('<td>' + str(now_weather2[num]) + '</td>')
        elif now_weather1[num] == '雲底高度':
            if int(now_weather2[num]) < 450:
                html.append('<td class=purple>' + str(now_weather2[num]) + 'm</td>')
            elif int(now_weather2[num]) >= 450 and int(now_weather2[num]) < 600:
                html.append('<td class=red>' + str(now_weather2[num]) + 'm</td>')
            elif int(now_weather2[num]) >= 600 and int(now_weather2[num]) < 850:
                html.append('<td class=orange>' + str(now_weather2[num]) + 'm</td>')
            else:
                html.append('<td>' + str(now_weather2[num]) + 'm</td>')
        else:
            html.append('<td>' + str(now_weather2[num]) + '</td>')
        html.append('</tr>')  
        num += 1
    html.append('<div class="image-container">')
    html.append('<img src="' + str(title[3]) + '" alt="NULL">')
    html.append('</div>')
    html.append('<p class="time">出典：openWeather,気象庁  ' + now_weather1[0] + '  ' + title[0]  + '</p>')
    html.append('<p> </p>')
    html.append('<p> </p>')
    if kinocd == 2:
        forecast, fore_date, arr_len = remake_forecast(forecast)
        for ix1 in range(len(forecast)):
            fore_day = add_foreDay(fore_date, ix1)
            html.append('<h2>' + title[2] + ' ' + str(fore_day) + '日</h2>')
            html.append('<table border="1">')
            for ix2 in range(12):
                html.append('<tr>')
                for ix3 in range(9):
                    if ix3 == 0:
                        html.append('<th>' + str(forecast[ix1][ix2][ix3]) + '</th>')
                    else:
                        if forecast[ix1][ix2][ix3] == '-':
                            html.append('<td>-</td>')
                        elif ix2 == 2: #アイコン
                            html.append('<td class=tdIcon><img src="' + forecast[ix1][ix2][ix3] + '" alt="NULL"></td>')
                        elif ix2 == 4 or ix2 == 5: #風速・ガスト
                            if forecast[ix1][ix2][ix3][0:1] == 'A':
                                html.append('<td class=blue>' + str(forecast[ix1][ix2][ix3][1:]) + '</td>')
                            elif forecast[ix1][ix2][ix3][0:1] == 'B':
                                html.append('<td class=orange>' + str(forecast[ix1][ix2][ix3][1:]) + '</td>')
                            elif forecast[ix1][ix2][ix3][0:1] == 'C':
                                html.append('<td class=red>' + str(forecast[ix1][ix2][ix3][1:]) + '</td>')
                            elif forecast[ix1][ix2][ix3][0:1] == 'D':
                                html.append('<td class=purple>' + str(forecast[ix1][ix2][ix3][1:]) + '</td>')
                        elif ix2 == 7: #視程
                            try:
                                if int(forecast[ix1][ix2][ix3]) < 1500 :
                                    html.append('<td class=purple>' + str(forecast[ix1][ix2][ix3]) + 'm</td>')
                                elif int(forecast[ix1][ix2][ix3]) >= 1500 and int(forecast[ix1][ix2][ix3]) < 5000:
                                    html.append('<td class=red>' + str(forecast[ix1][ix2][ix3]) + 'm</td>')
                                elif int(forecast[ix1][ix2][ix3]) >= 5000 and int(forecast[ix1][ix2][ix3]) < 10000:
                                    html.append('<td class=orange>' + str(forecast[ix1][ix2][ix3]) + 'm</td>')
                            except ValueError:
                                html.append('<td>' + str(forecast[ix1][ix2][ix3]) + '</td>')   
                        elif ix2 == 8: #雲底高度
                            if int(forecast[ix1][ix2][ix3]) < 450 :
                                html.append('<td class=purple>' + str(forecast[ix1][ix2][ix3]) + 'm</td>')
                            elif int(forecast[ix1][ix2][ix3]) >= 450 and int(forecast[ix1][ix2][ix3]) < 600:
                                html.append('<td class=red>' + str(forecast[ix1][ix2][ix3]) + 'm</td>')
                            elif int(forecast[ix1][ix2][ix3]) >= 600 and int(forecast[ix1][ix2][ix3]) < 850:
                                html.append('<td class=orange>' + str(forecast[ix1][ix2][ix3]) + 'm</td>')
                            else:
                                html.append('<td>' + str(forecast[ix1][ix2][ix3]) + 'm</td>')  
                        elif ix2 == 9: #気温
                            try:
                                if int(forecast[ix1][ix2][ix3][0:2]) >= 31:
                                    html.append('<td class=purple>' + str(forecast[ix1][ix2][ix3]) + '</td>')
                                elif int(forecast[ix1][ix2][ix3][0:2]) < 31 and int(forecast[ix1][ix2][ix3][0:2]) >= 28:
                                    html.append('<td class=red>' + str(forecast[ix1][ix2][ix3]) + '</td>')
                                elif int(forecast[ix1][ix2][ix3][0:2]) < 28 and int(forecast[ix1][ix2][ix3][0:2]) >= 25:
                                    html.append('<td class=orange>' + str(forecast[ix1][ix2][ix3]) + '</td>')
                                else:
                                    html.append('<td>' + str(forecast[ix1][ix2][ix3]) + '</td>')  
                            except ValueError:
                                html.append('<td>' + str(forecast[ix1][ix2][ix3]) + '</td>') 
                        else:
                            html.append('<td>' + str(forecast[ix1][ix2][ix3]) + '</td>')                                    
                html.append('</tr>')
            html.append('</table>')
            html.append('<p>&copy; 法政大学令和元年卒 谷口 雄一</p>')  
            html.append('<p>    ※※無断転用禁止※※</p>')
            html.append('<p>  </p>')
            html.append('<p>  </p>')

    elif kinocd == 1:
        con = 0
        html.append('<h2>' + title[2] + '</h2>')
        html.append('<table border="1">')
        for ix2 in range(12):
            html.append('<tr>')
            for ix1 in range(10):
                if (ix1)  % 10 == 0:
                    html.append('<th>' + str(forecast[0][ix2]) + '</th>')
                else:
                    if ix2 == 2: #アイコン
                        html.append('<td class=tdIcon><img src="' + forecast[ix1][ix2] + '" alt="NULL"></td>')
                    elif ix2 == 4 or ix2 == 5: #風速・ガスト
                        if forecast[ix1][ix2][0:1] == 'A':
                            html.append('<td class=blue>' + str(forecast[ix1][ix2][1:]) + '</td>')
                        elif forecast[ix1][ix2][0:1] == 'B':
                            html.append('<td class=orange>' + str(forecast[ix1][ix2][1:]) + '</td>')
                        elif forecast[ix1][ix2][0:1] == 'C':
                            html.append('<td class=red>' + str(forecast[ix1][ix2][1:]) + '</td>')
                        elif forecast[ix1][ix2][0:1] == 'D':
                            html.append('<td class=purple>' + str(forecast[ix1][ix2][1:]) + '</td>')
                    elif ix2 == 7: #視程
                        try:
                            if int(forecast[ix1][ix2]) < 1500 :
                                html.append('<td class=purple>' + str(forecast[ix1][ix2]) + 'm</td>')
                            elif int(forecast[ix1][ix2]) >= 1500 and int(forecast[ix1][ix2]) < 5000:
                                html.append('<td class=red>' + str(forecast[ix1][ix2]) + 'm</td>')
                            elif int(forecast[ix1][ix2]) >= 5000 and int(forecast[ix1][ix2]) < 10000:
                                html.append('<td class=orange>' + str(forecast[ix1][ix2]) + 'm</td>')
                        except ValueError:
                            html.append('<td>' + str(forecast[ix1][ix2]) + '</td>') 
                    elif ix2 == 8: #雲底高度
                        if int(forecast[ix1][ix2]) < 450 :
                            html.append('<td class=purple>' + str(forecast[ix1][ix2]) + 'm</td>')
                        elif int(forecast[ix1][ix2]) >= 450 and int(forecast[ix1][ix2]) < 600:
                            html.append('<td class=red>' + str(forecast[ix1][ix2]) + 'm</td>')
                        elif int(forecast[ix1][ix2]) >= 600 and int(forecast[ix1][ix2]) < 850:
                            html.append('<td class=orange>' + str(forecast[ix1][ix2]) + 'm</td>')
                        else:
                            html.append('<td>' + str(forecast[ix1][ix2]) + 'm</td>') 

                    elif ix2 == 9: #気温
                        try:
                            if int(forecast[ix1][ix2][0:2]) >= 31:
                                html.append('<td class=purple>' + str(forecast[ix1][ix2]) + '</td>')
                            elif int(forecast[ix1][ix2][0:2]) < 31 and int(forecast[con + ix1][ix2][0:2]) >= 28:
                                html.append('<td class=red>' + str(forecast[ix1][ix2]) + '</td>')
                            elif int(forecast[ix1][ix2][0:2]) < 28 and int(forecast[con + ix1][ix2][0:2]) >= 25:
                                html.append('<td class=orange>' + str(forecast[ix1][ix2]) + '</td>')
                            else:
                                html.append('<td>' + str(forecast[ix1][ix2]) + '</td>')
                        except ValueError:
                                html.append('<td>' + str(forecast[ix1][ix2]) + '</td>') 
                    else:
                        html.append('<td>' + str(forecast[ix1][ix2]) + '</td>')
            html.append('</tr>') 
        html.append('</table>')
        html.append('<p>&copy; 法政大学令和元年卒 谷口 雄一  ※※無断転用禁止※※</p>')  
    text = ''
    for ix1 in range(len(html)):
        text += html[ix1]
    return text

def make_bottom():
    html = []
    html.append('</body>')
    html.append('</html>')
    text = ''
    for ix1 in range(len(html)):
        text += html[ix1]
    return text

def convertToPdf(text, nowdate,path):
    if path == "":
        with open('天気概況_' + nowdate + '.html', 'w', encoding='utf-8') as file:
            file.write(text)
        current_dir = os.getcwd()
        url = 'file:///' + current_dir + '/天気概況_' + nowdate + '.html'
        webbrowser.open_new_tab(url)
    else:
        with open(path + '/' + '天気概況_' + nowdate + '.html', 'w', encoding='utf-8') as file:
            file.write(text)
        current_dir = os.getcwd()
        url = 'file:///' + path + '/天気概況_' + nowdate + '.html'
        webbrowser.open_new_tab(url)
    return '天気概況_' + nowdate + '.html'

def remake_forecast(forecast):
    #初日の予報がない時間帯を-で埋める
    try:
        fore_date = int(forecast[1][0][0:2])
    except ValueError:
        fore_date = int(forecast[1][0][0:1])
    comp_hour_str = forecast[1][0][-5] + forecast[1][0][-4]
    comp_hour = int(comp_hour_str)
    flg = 0
    add_num = 1
    if comp_hour_str != "00":
        while flg == 0:
            add_hour = comp_hour - add_num * 3
            dummy_array = ['','-','-','-','-','-','-','-','-','-','-','-'] 
            dummy_array[0] = str(fore_date) + '日 ' + str(add_hour) + ':00'
            forecast.insert(1, dummy_array)
            if add_hour == 0:
                break
            add_num += 1
    #最終日の予報がない時間帯を-で埋める
    try:
        last_date = int(forecast[len(forecast) - 1][0][0:2])
    except ValueError:
        last_date = int(forecast[len(forecast) - 1][0][0:1])
    last_hour_str = forecast[len(forecast)-1][0][-5] + forecast[len(forecast)-1][0][-4]
    last_hour = int(last_hour_str)
    if last_hour != 21:
        num = int((21 - last_hour) / 3)
        for ix1 in range(num):
            add_hour = last_hour + (3 * (ix1 + 1))
            dummy_array = ['','-','-','-','-','-','-','-','-','-','-','-'] 
            dummy_array[0] = str(last_date) + '日 ' + str(add_hour) + ':00'
            forecast.append(dummy_array)

    arr_len = len(forecast)
    arr_title = ['予報時刻','天気','アイコン','風向','風速','ガスト','3h雨量','視程','雲底高度','気温','湿度','気圧']
    #forecast.insert(0,arr_title)
    forecast.insert(9,arr_title)
    forecast.insert(18,arr_title)
    forecast.insert(27,arr_title)
    forecast.insert(36,arr_title)
    if len(forecast) >= 44:
        forecast.insert(45,arr_title)
    new_forecast1 = []
    new_forecast2 = []
    arr = []
    arr1 = []
    for ix1 in range(12):
        for ix2 in range(len(forecast)):
            arr.append(forecast[ix2][ix1])
        new_forecast1.append(arr)
        arr = []
    arr_len = int(len(new_forecast1[0]) / 9)

    for ix13 in range(arr_len):
        for ix12 in range(len(new_forecast1)):
            for ix11 in range(9):
                arr.append(new_forecast1[ix12][ix11 + ix13 * 9])
            arr1.append(arr)
            arr = []
        new_forecast2.append(arr1)   
        arr1 = []
        
    return new_forecast2, fore_date, arr_len

def add_foreDay(date1, ix1):
    day1 = datetime.datetime.now()
    day2 = day1.replace(day=int(date1))
    day3 = day2 + datetime.timedelta(days=ix1)
    date2 = str(day3.day)
    return date2