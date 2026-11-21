#PGM-ID:WL0S0200
#PGM-NAME:WLメタタフ取得
#最終更新日:2026/11/21

import os
from pypdf import PdfWriter

import WX0S0201
import WX0S0202
import WX0S0205
import WX0S0221
import WX0S0222

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
            WX0S0221.metar_pdf(metarJpn, metarEng, warning_flg, fileName_m, ix1, path)
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
            WX0S0222.taf_pdf(tafJpn, tafEng, warning_flg, fileName_t, ix2, path)
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
