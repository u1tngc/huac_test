#PGM-ID:WL1M0200
#PGM-NAME:WLメタタフ取得翻訳メイン
#最終更新日:

import datetime
import os
import requests
import sys
from pypdf import PdfWriter
import glob
import zoneinfo

import WL0S0200


def get_and_transtale(inp_location):
    # metar取得
    location = inp_location[0:4]
    fileName_MetarTaf = get_MetarTaf(location)
    if fileName_MetarTaf == "":
        retCD = 1
    else:
        retCD = WL0S0200.translate_MetarTaf(fileName_MetarTaf, "")
        os.remove('MetarTaf_' + fileName_MetarTaf + '.txt')
        try:
            os.rename("Metar.pdf",'Metar_' + fileName_MetarTaf + '.pdf')
            output = 'Metar_' + fileName_MetarTaf + '.pdf'
        except FileNotFoundError:
            output = 'MetarTaf_' + fileName_MetarTaf + '.pdf'
    return retCD, output


def get_MetarTaf(inp_location):
    url = f'https://aviationweather.gov/api/data/metar?ids={inp_location}&format=raw&taf=true'
    try:
        response = requests.get(url, timeout=7)
        jst = zoneinfo.ZoneInfo("Asia/Tokyo")
        fileName_m1 = datetime.datetime.now(jst)
        fileName_m2 = fileName_m1.strftime('%Y%m%d%H%M')
        file_name = inp_location + "_" + str(fileName_m2)
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
                url = f'https://aviationweather.gov/api/data/metar?ids={inp_location}&format=raw&taf=true&hours={mt_hour_str}'
                response = requests.get(url, timeout=7)
                with open(file_path, "wb") as file:
                    for chunk in response.iter_content(200000):
                        file.write(chunk)
                    file.close() 
                if file_empty(f"MetarTaf_{file_name}"):
                    return file_name
                if mt_hour == 12:
                    get_eof = 1
            os.remove('MetarTaf_' + file_name + '.txt')
            return ""              
    except requests.exceptions.Timeout:
        #messagebox.showerror("エラー", "異常終了しました。\nネットワークが弱いです。")
        sys.exit()
    except requests.exceptions.ConnectionError:
        #messagebox.showerror("エラー", "異常終了しました。\nインターネットに接続されていません。")
        sys.exit()


# metar tafをtxtファイルから読み込む
def translate(filename):
    retCD = WL0S0200.translate_MetarTaf(filename, "")
    return retCD


def file_empty(file_path):
    if os.path.getsize(file_path + ".txt") == 0:
        return False
    else:
        with open(file_path + ".txt", 'r') as f:
            content = f.read()
            if not content.strip():
                return False
            else:
                return True


def main(selected_option,airport,metar,taf):
    err_msg = 0
    output ="METAR・TAF翻訳結果.pdf"
    if selected_option == "取得・翻訳":
        err_msg, output = get_and_transtale(airport)
        for file_path in glob.glob("MetarTaf*.pdf"):
            os.rename(file_path,output)
    elif selected_option == "翻訳":
        mt = 0
        if metar != None and metar != "":
            with open('MetarTaf_temp.txt', 'w', encoding='utf-8') as file:
                file.writelines(metar)
            err_msg= translate('temp')
            os.remove('MetarTaf_temp.txt')
            mt = mt + 1
        if taf != None and taf != "":
            with open('MetarTaf_temp.txt', 'w', encoding='utf-8') as file:
                file.writelines(taf)
            err_msg= translate('temp')
            os.remove('MetarTaf_temp.txt')
            mt = mt + 1.5
        if mt >= 2:
            merger = PdfWriter()
            merger.append("Metar.pdf")
            merger.append("Taf.pdf")
            os.remove("Metar.pdf")
            os.remove("Taf.pdf")
            merger.write(output)
            merger.close()
        elif mt == 1:
            os.rename("Metar.pdf", output)
        elif mt == 1.5:
            os.rename("Taf.pdf", output)
    return output, err_msg
