#PGM-ID:WL1S0002
#PGM-NAME:WL自家用取得
#最終更新日:


import datetime
import requests

import PK0S0100


def get_asas(currentDateTime: datetime, fileName_array, temp_file):
    url_array = []
    fileName = []
  #地上天気図（実況）  
    url_array.append('https://www.data.jma.go.jp/fcd/yoho/data/wxchart/quick/ASAS_COLOR.pdf')
    fileName.append(f"地上天気図(実況)_{temp_file}.pdf")
    fileName_array[1] = f"地上天気図(実況)_{temp_file}.pdf"

  #地上天気図（予報）  
    url_array.append('https://www.data.jma.go.jp/fcd/yoho/data/wxchart/quick/FSAS24_COLOR_ASIA.pdf')
    fileName.append(f"地上天気図(予報・当日21時)_{temp_file}.pdf")
    fileName_array[2] = f"地上天気図(予報・当日21時)_{temp_file}.pdf"

  #地上天気図（予報）  
    url_array.append('https://www.data.jma.go.jp/fcd/yoho/data/wxchart/quick/FSAS48_COLOR_ASIA.pdf')
    fileName.append( f"地上天気図(予報・翌日21時)_{temp_file}.pdf")
    fileName_array[3] = f"地上天気図(予報・翌日21時)_{temp_file}.pdf"

  #地上天気図（過去） 
    #昨日21時のＵＲＬを準備  
    url1 = 'https://www.data.jma.go.jp/fcd/yoho/data/wxchart/quick/'
    url3 = '/ASAS_COLOR_'
    currentDateTimeYesterday = currentDateTime + datetime.timedelta(days=-1)
    url2 =  str(currentDateTimeYesterday.strftime('%Y%m'))
    timeKbn = PK0S0100.timeCheck(currentDateTime,2)
    if timeKbn == 21: #最新版が昨日21時版の場合は一昨日の21時を取得
        hours = int(currentDateTime.hour)
        minutes = int(currentDateTime.minute)
        asas_time = (hours * 60) + minutes
        if asas_time <= 330:
            currentDateTimeYesterday = currentDateTimeYesterday + datetime.timedelta(days=-1)
            url2 =  str(currentDateTime.strftime('%Y%m'))        
    url4 = str(currentDateTimeYesterday.strftime('%Y%m%d'))
    url5 = '1200.pdf'
    url_array.append(url1 + url2 + url3 + url4 + url5)
    #ファイル取得
    fileName.append(f"地上天気図(過去)_{temp_file}.pdf")
    fileName_array[0] = f"地上天気図(過去)_{temp_file}.pdf"
    for ix1 in range(len(url_array)):
        access_url(url_array[ix1],fileName[ix1])
    return fileName_array


def get_kosou(timeKbn, fileName, temp_file):
    if timeKbn == 21:
        urlTime = '12.pdf'
    else:
        urlTime = '00.pdf'

    url_aupq78 = 'https://www.jma.go.jp/bosai/numericmap/data/nwpmap/aupq78_' + str(urlTime)
    filename = f"高層天気図(850・700)_{temp_file}.pdf"
    fileName[4] = filename
    access_url(url_aupq78, filename)

    url_aupq35 = 'https://www.jma.go.jp/bosai/numericmap/data/nwpmap/aupq35_' + str(urlTime)
    filename = f"高層天気図(500・300)_{temp_file}.pdf"
    fileName[5] = filename
    access_url(url_aupq35, filename)

    return fileName


def get_tanki(fileName, temp_file):
    url_tanki = 'https://www.data.jma.go.jp/fcd/yoho/data/jishin/kaisetsu_tanki_latest.pdf'
    filename = f"短期予報解説資料_{temp_file}.pdf"
    fileName[6] = filename
    access_url(url_tanki, filename)

    return fileName


def access_url(url, fileName):
    response = requests.get(url)
    file = open(fileName,"wb")
    for chunk in response.iter_content(200000):
        file.write(chunk)    
    file.close()