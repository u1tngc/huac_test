#PGM-ID:WL0S0200
#PGM-NAME:WLメタタフ取得
#最終更新日:

import os
from pypdf import PdfWriter
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4, portrait
from reportlab.lib.pagesizes import A3, portrait
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

import WX0S0201
import WX0S0202
import WX0S0205

def translate_MetarTaf(fileName, path):
    fileName_m = 'Metar'
    fileName_t = 'Taf'
    metar_umu = 0
    taf_umu = 0
    metar_US = ["RJTY", "RODN", "RJOI", "ROTM"]
    metar, taf = get_MetarTaf(str(fileName), path)
    if len(metar) != 0:
        for ix1 in range(len(metar)):
            if metar[ix1][6:10] in metar_US:
                metarJpn, metarEng, warning_flg = WX0S0201.readMetar(metar[ix1])
            else:
                metarJpn, metarEng, warning_flg = WX0S0205.readMetar(metar[ix1])
            if len(metar[ix1]) > 110:
                for ix10 in range(110):
                    if metar[ix1][110 - ix10 - 1 : 110 - ix10] == " ":
                        metar1 = metar[ix1][0:110 - ix10 - 1]
                        metar2 = metar[ix1][110 - ix10:]
                        break
                metarJpn.insert(0, metar2)
                metarJpn.insert(0, metar1)
                metarJpn.insert(2, "")
                metarEng.insert(0, "")
                metarEng.insert(1, "")
                metarEng.insert(2, "")
                warning_flg.insert(0, 0)
                warning_flg.insert(0, 0)
                warning_flg.insert(1, 0)
            else:
                metarJpn.insert(0, metar[ix1])
                metarJpn.insert(1, "")
                metarEng.insert(0, "")
                metarEng.insert(1, "")
                warning_flg.insert(0, 0)
                warning_flg.insert(1, 0)
            metarTaf_pdf(metarJpn, metarEng, warning_flg, fileName_m, 1, ix1, path)  
            metarJpn = []
            metarEng = []
            warning_flg = []
        if ix1 >= 1:
            join_File(ix1, fileName_m, path)
        else:
            try:
                os.remove(path + fileName_m + '.pdf')
            except FileNotFoundError:
                pass
            os.rename(path + fileName_m + '_1.pdf',path +  fileName_m + '.pdf')
        metar_umu = 1
    if len(taf) != 0:
        for ix2 in range(len(taf)):
            tafJpn, tafEng, warning_flg = WX0S0202.readTaf(taf[ix2])
            for ix1 in range(len(taf[ix2])):
                tafJpn.insert(0, taf[ix2][len(taf[ix2]) - ix1 - 1])
                tafEng.insert(0, "")
                warning_flg.insert(0,0)
            tafJpn.insert(ix1 + 1, "")
            tafEng.insert(ix1 + 1, "")
            warning_flg.insert(ix1 + 1,0)
            metarTaf_pdf(tafJpn, tafEng, warning_flg, fileName_t, 2, ix2, path) 
        taf_umu = 1
        if ix2 >= 1:
            join_File(ix2, fileName_t, path)
        else:
            try:
                os.remove(path + fileName_t + '.pdf')
            except FileNotFoundError:
                pass
            os.rename(path + fileName_t + '_1.pdf', path + fileName_t + '.pdf')
    retCD = 0
    if metar_umu == 1 and taf_umu == 1:
        retCD = join_metar_taf(fileName_m, fileName_t, fileName, path)
    return retCD

def join_File(ix1, fileName, path):
    merger = PdfWriter()
    for ix3 in range(ix1 + 1):
        merger.append(path + fileName + '_' + str(ix3 + 1) +'.pdf')
    merger.write(path + fileName + '.pdf')
    merger.close()
    for ix4 in range(ix1 + 1):
        os.remove(path + fileName + '_' + str(ix4 + 1) +'.pdf')

def get_MetarTaf(fileName, path):
    tafFlg = 0
    ix1 = 0
    metar = []
    taf = []
    taf_all = []
    with open(path + 'MetarTaf_' + fileName + '.txt', 'r') as f:
        record = f.readlines()

    for ix1 in range(len(record)):
        if record[ix1][0:5] in ["METAR", "SPECI"]:
            metar.append(record[ix1].replace("\n",""))
        else:
            taf_all.append(record[ix1])
            tafFlg = 1
    if tafFlg == 1:
        taf_wk1 = []
        taf_wk2 = []
        for ix1 in range(len(taf_all)):
            taf_str = taf_all[ix1].replace("\n","")
            if ix1 == 0:
                taf_wk1.append(taf_str)
            else:
                if taf_str[0:3] == "TAF":
                    taf_wk2.append(taf_wk1)
                    taf_wk1 = []
                    taf_wk1.append(taf_str)
                else:
                    taf_wk1.append(taf_str)
        taf_wk2.append(taf_wk1)
        if len(taf_wk2) == 1:
            taf = taf_wk2
        else:
            drop_array = []
            for ix1 in range(len(taf_wk2)):
                if taf_wk2[ix1] == taf_wk2[ix1 + 1]:
                    drop_array.append(ix1 + 1)
                if ix1 + 1 == len(taf_wk2) - 1:
                    break
            if drop_array:
                for ix1 in range(len(taf_wk2)):
                    if ix1 not in drop_array:
                        taf.append(taf_wk2[ix1])
            else:
                taf = taf_wk2
    return metar, taf

def metarTaf_pdf(metartafJpn, metartafEng, warning_flg, fileName, metartaf, ix1, path):
    GEN_SHIN_GOTHIC_MEDIUM_TTF = os.path.abspath("static/fonts/GenShinGothic-Monospace-Medium.ttf")
    if metartaf == 1: #metar
        FILENAME = path + fileName + '_' + str(ix1 + 1) +'.pdf'
        c = canvas.Canvas(FILENAME, pagesize=portrait(A4))
        pdfmetrics.registerFont(TTFont('GenShinGothic', GEN_SHIN_GOTHIC_MEDIUM_TTF))
        font_size = 10
        c.setFont('GenShinGothic', font_size)
        y = 800
        for ix2 in range(len(metartafJpn)):
            if warning_flg[ix2] == 1:
                c.setFillColor(HexColor('#FF0000'))
            elif warning_flg[ix2] == 2:
                c.setFillColor(HexColor('#FF9900'))
            else:
                c.setFillColor(HexColor('#0d0000'))
            c.drawString(400, y, metartafEng[ix2])
            c.setFillColor(HexColor('#0d0000'))
            c.drawString(30, y, metartafJpn[ix2])
            y -= 13
        c.save()
    elif metartaf == 2: #taf
        FILENAME = path + fileName + '_' + str(ix1 + 1) +'.pdf'
        if len(metartafJpn) >= 60:
            flg_1 = 0
            flg_2 = 0
            c = canvas.Canvas(FILENAME, pagesize=portrait(A3))
            pdfmetrics.registerFont(TTFont('GenShinGothic', GEN_SHIN_GOTHIC_MEDIUM_TTF))
            y = 1150
            for ix2 in range(len(metartafJpn)):
                if metartafJpn[ix2][0:2] == "～Ｔ":
                    flg_2 = 1             
                if len(metartafJpn[ix2]) == 0:
                    font_size = 3
                    if flg_2 == 1:
                        newY = y - 11
                        flg_2 = 0
                    if y <= 200:
                        flg_1 = 1
                    c.setFont('GenShinGothic', font_size)
                    c.drawString(30, y, metartafJpn[ix2])
                    c.drawString(400, y, metartafEng[ix2])
                else:
                    font_size = 11
                    if warning_flg[ix2] == 1:
                        c.setFillColor(HexColor('#FF0000'))
                    elif warning_flg[ix2] == 2:
                        c.setFillColor(HexColor('#FF9900'))
                    else:
                        c.setFillColor(HexColor('#0d0000'))
                    if flg_1 == 1:
                        y = newY
                        flg_1 = 3   
                        c.setFont('GenShinGothic', font_size)    
                        c.drawString(780, y, metartafEng[ix2])
                        c.setFillColor(HexColor('#0d0000'))
                        c.drawString(450, y, metartafJpn[ix2])       
                    elif flg_1 == 3:
                        c.setFont('GenShinGothic', font_size)  
                        c.drawString(780, y, metartafEng[ix2])   
                        c.setFillColor(HexColor('#0d0000'))
                        c.drawString(450, y, metartafJpn[ix2])
                    else:
                        c.setFont('GenShinGothic', font_size)    
                        c.drawString(350, y, metartafEng[ix2])
                        c.setFillColor(HexColor('#0d0000'))
                        c.drawString(20, y, metartafJpn[ix2])
                        
                y -= 11
        else:
            c = canvas.Canvas(FILENAME, pagesize=portrait(A4))
            pdfmetrics.registerFont(TTFont('GenShinGothic', GEN_SHIN_GOTHIC_MEDIUM_TTF))
            font_size = 10
            c.setFont('GenShinGothic', font_size)
            y = 800
            for ix2 in range(len(metartafJpn)):
                if warning_flg[ix2] == 1:
                    c.setFillColor(HexColor('#FF0000'))
                elif warning_flg[ix2] == 2:
                    c.setFillColor(HexColor('#FF9900'))
                else:
                    c.setFillColor(HexColor('#0d0000'))
                c.drawString(400, y, metartafEng[ix2])
                c.setFillColor(HexColor('#0d0000'))
                c.drawString(30, y, metartafJpn[ix2])
                y -= 13

        c.save()

    return FILENAME

def join_metar_taf(fileName_m, fileName_t, fileName,path):
    try:
        merger = PdfWriter()
        merger.append(path + fileName_m + '.pdf')
        merger.append(path + fileName_t + '.pdf')
        merger.write(path + 'MetarTaf_' + fileName + '.pdf')
        merger.close()
        os.remove(path + fileName_m + '.pdf')
        os.remove(path + fileName_t + '.pdf')
        return 0
    except PermissionError:
        #messagebox.showerror("エラー", "異常終了しました。\npdfファイルを閉じてください。")
        return 1
