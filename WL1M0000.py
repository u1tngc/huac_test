#PGM-ID:WL1M0000
#PGM-NAME:WL資料取得メイン
#最終更新日:

import datetime
import os
from PIL import Image
from pypdf import PdfWriter
from PyPDF2 import PdfReader, PdfWriter
import requests
import time
import zoneinfo

#import WL0S0100
import WL0S0200
import WL1S0001
import WL1S0002

class WX1M0000:
    jst = zoneinfo.ZoneInfo("Asia/Tokyo")
    nowdatetime = datetime.datetime.now(jst).strftime('%Y%m%d%H%M%S')
    
def kyotsu_shori(shoriKbn, mt_location):
    out_file = ["",""]
    currentDateTime = datetime.datetime.now(WX1M0000.jst)
    if shoriKbn != 0:
        currentDateTime = get_time()
        timeKbn = timeCheck(currentDateTime,1)
        #RJTYのmetar取得
        if shoriKbn == "1":
            fileName = [""] * 7
            #地上天気図・過去→現在→予報を取得
            fileName = WL1S0002.get_asas(currentDateTime, fileName, WX1M0000.nowdatetime)
            #高層天気図850/700/500/300を取得（最新版）
            fileName = WL1S0002.get_kosou(timeKbn, fileName, WX1M0000.nowdatetime)
            #短期予報解説資料
            fileName = WL1S0002.get_tanki(fileName, WX1M0000.nowdatetime)
        elif shoriKbn == "2":
            fileName = [""] * 15
            fileName = WL1S0001.get_kyosho(timeKbn, currentDateTime, fileName, WX1M0000.nowdatetime)
            out_file[1] = get_DOC(currentDateTime)
        metar_flg = 1
        fileName_MetarTaf = []
        try:
            if mt_location == "":
                fileName_MetarTaf.append(get_MetarTaf("RJTY"))
                retCD = WL0S0200.translate_MetarTaf(fileName_MetarTaf[0], "")
            else:
                fileName_MetarTaf.append(get_MetarTaf("RJTY"))
                retCD = WL0S0200.translate_MetarTaf(fileName_MetarTaf[0], "")
                time.sleep(2)
                fileName_MetarTaf.append(get_MetarTaf(mt_location))
                if fileName_MetarTaf[1] == "":
                    metar_flg = 2
                else:
                    retCD = WL0S0200.translate_MetarTaf(fileName_MetarTaf[1], "")
                try:
                    os.rename('Metar.pdf', f"MetarTaf_{fileName_MetarTaf[1]}.pdf")
                except FileNotFoundError:
                    pass
        except Exception as e:
            print(f"Error fetching METAR/TAF data: {e}")
            metar_flg = 0
        blip = get_blipmap()
        #html_name = WL0S0100.getWx(shoriKbn, "360-0222,JP", WX1M0000.nowdatetime,"2")
        out_file[0] = append_pdf(fileName_MetarTaf, fileName, blip, metar_flg)
        if shoriKbn == "2": 
            rotatePDF()
        removefiles(fileName_MetarTaf, fileName, blip, metar_flg)
        time.sleep(2)
        if metar_flg == 0:
            err_msg = "お知らせ", "metarもしくはtafの取得ができませんでした。"
        elif metar_flg == 2:
            err_msg = "指定した飛行場のMETAR/TAFを取得できませんでした。\n横田飛行場のMETAR/TAFのみ出力しています。"
        elif blip  == 1:
            err_msg = ""
        else:
            err_msg = ""
    return out_file, err_msg
    #return out_file, err_msg, html_name

def get_time():
    currentTimeUnix = time.time()
    currentDateTime = datetime.datetime.fromtimestamp(currentTimeUnix)
    return currentDateTime

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

def get_MetarTaf(location):
    url = f'https://aviationweather.gov/api/data/metar?ids={location}&format=raw&taf=true'
    response = requests.get(url)
    file_name = f"{location}_x"
    file_path = f"MetarTaf_{file_name}.txt"
    with open(file_path, "wb") as file:
        for chunk in response.iter_content(200000):
            file.write(chunk)
        file.close() 
    if file_empty(f"MetarTaf_{file_name}"):
        return file_name
    else:
        get_eof = 0
        mt_hour = 1
        while get_eof == 0:
            mt_hour = mt_hour + 0.5
            if str(mt_hour)[-2:-1] == "." and str(mt_hour)[-1:] == "0":
                mt_hour_str, mt_hour_2 = str(mt_hour).split(".")
            else:
                mt_hour_str = str(mt_hour)
            url = f'https://aviationweather.gov/api/data/metar?ids={location}&format=raw&taf=true&hours={mt_hour_str}'
            response = requests.get(url, timeout=7)
            with open(file_path, "wb") as file:
                for chunk in response.iter_content(200000):
                    file.write(chunk)
                file.close()
            if file_empty(f"MetarTaf_{file_name}"):
                return file_name
            if mt_hour == 12:
                get_eof = 1
        return ""

def file_empty(file_name):
    file_path = file_name + '.txt'
    if os.path.getsize(file_path) == 0:
        return False
    else:
        with open(file_path, 'r') as f:
            content = f.read()
            if not content.strip():
                return False
            else:
                return True
   
def get_blipmap():
    blip = 0
    url = 'http://blipmap.glider.jp/BLIPMAP/KANTO_JAPAN/FCST/sounding3.curr.1400lst.w2.png'
    try:
        response = requests.get(url, timeout = 10)
        # ステータスコードがエラーでないことを確認
        response.raise_for_status()
        file = open("blipmap.png","wb")
        for chunk in response.iter_content(200000):
            file.write(chunk)    
        file.close()
        #pngファイルのpdf化
        image1 = Image.open('blipmap.png')
        im_pdf = image1.convert("RGB")
        im_pdf.save("blipmap.pdf")
        #pngファイルの削除
        os.remove('blipmap.png')
        blip = 1
        return blip
    except requests.exceptions.Timeout:
        blip = 0
        return blip

def append_pdf(fileName_MetarTaf, fileName, blip, metar_flg):
    merger = PdfWriter()
    for ix2 in range(len(fileName)):
        merger.append(fileName[ix2])
    if blip == 1:
        merger.append('blipmap.pdf')
    if metar_flg != 0:
        for ix10 in range(len(fileName_MetarTaf)):
            merger.append('MetarTaf_' + fileName_MetarTaf[ix10] + '.pdf')
    merger.write('wxファイル統合版_' + WX1M0000.nowdatetime + '.pdf')
    merger.close()
    return 'wxファイル統合版_' + WX1M0000.nowdatetime + '.pdf'

def removefiles(fileName_MetarTaf, fileName, blip, metar_flg):
    for ix3 in range(len(fileName)):       
        os.remove(fileName[ix3])
    if blip == 1:
        os.remove('blipmap.pdf')
    if metar_flg == 1:
        for ix10 in range(len(fileName_MetarTaf)):
            os.remove('MetarTaf_' + fileName_MetarTaf[ix10] + '.pdf')
            os.remove('MetarTaf_' + fileName_MetarTaf[ix10] + '.txt')

def get_DOC(currentDateTime: datetime):
    timeKbn = timeCheck(currentDateTime,3)
    url_tanki = 'https://www.data.jma.go.jp/fcd/yoho/data/jishin/kaisetsu_tanki_latest.pdf'
    response = requests.get(url_tanki, timeout = 10)
    file = open("短期予報解説資料.pdf","wb")
    for chunk in response.iter_content(200000):
        file.write(chunk)    
    file.close()
    url_shukan = 'https://www.data.jma.go.jp/fcd/yoho/data/jishin/kaisetsu_shukan_latest.pdf'
    response = requests.get(url_shukan, timeout = 10)
    file = open("週間天気予報解説資料.pdf","wb")
    for chunk in response.iter_content(200000):
        file.write(chunk)    
    file.close()

    #500hPa予報
    if timeKbn == 9:
        time_url = '00'
    else:
        time_url = '12'
    url_num = ["2","4","7"]
    for ix1 in range(3):
        url_fxfe = f'https://www.jma.go.jp/bosai/numericmap/data/nwpmap/fxfe50{url_num[ix1]}_{time_url}.pdf'
        response = requests.get(url_fxfe, timeout = 10)
        file = open(f"fefx_{str(ix1)}.pdf","wb")
        for chunk in response.iter_content(200000):
            file.write(chunk)    
        file.close()
    
    #200hPa
    url_tanki = f'https://www.jma.go.jp/bosai/numericmap/data/nwpmap/aupa20_{time_url}.pdf'
    response = requests.get(url_tanki, timeout = 10)
    file = open("aupa20.pdf","wb")
    for chunk in response.iter_content(200000):
        file.write(chunk)    
    file.close()    

    merger = PdfWriter()
    merger.append("短期予報解説資料.pdf")
    merger.append("週間天気予報解説資料.pdf")
    for ix1 in range(3):
        merger.append(f"fefx_{str(ix1)}.pdf")
    merger.append("aupa20.pdf")

    if timeKbn == 9:
        time_fxjp854 = "00"
    else:
        time_fxjp854 = "12"
    url_fxjp854 = f"https://www.jma.go.jp/bosai/numericmap/data/nwpmap/fxjp854_{time_fxjp854}.pdf"
    response = requests.get(url_fxjp854, timeout = 10)
    file = open("fxjp854.pdf","wb")  
    for chunk in response.iter_content(200000):
        file.write(chunk)    
    file.close() 
    merger.append("fxjp854.pdf")

    merger.write('wx予報支援資料_' + WX1M0000.nowdatetime + '.pdf')
    merger.close()
    os.remove("短期予報解説資料.pdf")
    os.remove("週間天気予報解説資料.pdf")
    os.remove("fxjp854.pdf")
    for ix1 in range(3):
        os.remove(f"fefx_{str(ix1)}.pdf")
    os.remove("aupa20.pdf")
    return 'wx予報支援資料_' + WX1M0000.nowdatetime + '.pdf'

def rotatePDF():
    reader = PdfReader('wxファイル統合版_' + WX1M0000.nowdatetime + '.pdf')
    writer = PdfWriter()
    rotation = 270
    page_number = [12,13]
    # 各ページを処理
    for i, page in enumerate(reader.pages):
        if i in page_number:
            # ページを回転
            page.rotate(rotation)
        writer.add_page(page)

    # 新しいPDFファイルに保存
    with open('wxファイル統合版_' + WX1M0000.nowdatetime + '.pdf', 'wb') as outfile:
        writer.write(outfile)
