#PGM-ID:WL1M0200
#PGM-NAME:WLメタタフ取得翻訳メイン
#最終更新日:2026/07/28

import datetime
import os
import shutil
import tempfile
import uuid
import zoneinfo

import requests
from pypdf import PdfWriter

import WL0S0200

API_URL = 'https://aviationweather.gov/api/data/metar'
API_TIMEOUT = 7

# 一時作業ディレクトリの親フォルダ
WORK_ROOT = os.path.join(tempfile.gettempdir(), "metartaf_work")

# エラーコード
ERR_OK = 0        # 正常終了
ERR_NO_DATA = 1   # 該当データなし
ERR_NETWORK = 2   # ネットワーク異常
ERR_PDF = 3       # PDF作成失敗
ERR_KBN = 4       # 処理区分不正

ERR_MESSAGE = {
    ERR_NO_DATA: "該当するMETAR/TAFが取得できませんでした。空港コードを確認してください。",
    ERR_NETWORK: "気象情報の取得に失敗しました。時間をおいて再実行してください。",
    ERR_PDF: "PDFの作成に失敗しました。",
    ERR_KBN: "処理区分が不正です。",
}

def get_err_msg(err_cd):
    """エラーコードから画面表示用メッセージを取得する。"""
    if err_cd == ERR_OK:
        return ""
    return ERR_MESSAGE.get(err_cd, "異常終了しました。")

def make_workdir():

    os.makedirs(WORK_ROOT, exist_ok=True)
    workdir = tempfile.mkdtemp(prefix="mt_", dir=WORK_ROOT)
    return workdir + os.sep


def cleanup_workdir(path):
    if not path:
        return
    target = path.rstrip(os.sep)
    # 想定外のディレクトリを消さないよう、作業用ルート配下のみ削除する
    if os.path.abspath(target).startswith(os.path.abspath(WORK_ROOT)):
        shutil.rmtree(target, ignore_errors=True)


def is_empty(file_path):
    """txtファイルが空（または空白のみ）ならTrueを返す。"""
    if os.path.getsize(file_path) == 0:
        return True
    with open(file_path, 'r') as f:
        return not f.read().strip()

def save_response(response, file_path):
    with open(file_path, "wb") as file:
        for chunk in response.iter_content(200000):
            file.write(chunk)

def get_MetarTaf(inp_location, path):
    jst = zoneinfo.ZoneInfo("Asia/Tokyo")
    stamp = datetime.datetime.now(jst).strftime('%Y%m%d%H%M%S')
    # 秒 + ランダム文字列で、同時実行時もファイル名が衝突しないようにする
    file_name = f"{inp_location}_{stamp}_{uuid.uuid4().hex[:6]}"
    file_path = f"{path}MetarTaf_{file_name}.txt"
    try:
        url = f'{API_URL}?ids={inp_location}&format=raw&taf=true'
        response = requests.get(url, timeout=API_TIMEOUT)
        save_response(response, file_path)
        if not is_empty(file_path):
            return file_name, ERR_OK
        # 直近のデータが無い場合、遡る時間を0.5時間ずつ広げて再取得する
        mt_hour = 1.0
        while mt_hour < 12:
            mt_hour += 0.5
            if float(mt_hour).is_integer():
                mt_hour_str = str(int(mt_hour))
            else:
                mt_hour_str = str(mt_hour)
            url = (f'{API_URL}?ids={inp_location}&format=raw'
                   f'&taf=true&hours={mt_hour_str}')
            response = requests.get(url, timeout=API_TIMEOUT)
            save_response(response, file_path)
            if not is_empty(file_path):
                return file_name, ERR_OK
        return "", ERR_NO_DATA
    except (requests.exceptions.Timeout,
            requests.exceptions.ConnectionError,
            requests.exceptions.RequestException):
        return "", ERR_NETWORK

def get_and_transtale(inp_location, path):
    location = inp_location[0:4]
    file_name, err_cd = get_MetarTaf(location, path)
    if err_cd != ERR_OK:
        return "", err_cd
    ret_cd = WL0S0200.translate_MetarTaf(file_name, path)
    if ret_cd != 0:
        return "", ERR_PDF
    try:
        os.remove(f"{path}MetarTaf_{file_name}.txt")
    except OSError:
        pass
    output = f"{path}METAR・TAF翻訳結果_{file_name}.pdf"
    for src in (f"{path}MetarTaf_{file_name}.pdf",
                f"{path}Metar.pdf",
                f"{path}Taf.pdf"):
        if os.path.exists(src):
            os.replace(src, output)
            return output, ERR_OK
    return "", ERR_PDF

def translate_input(metar, taf, path):
    output = f"{path}METAR・TAF翻訳結果.pdf"
    temp_txt = f"{path}MetarTaf_temp.txt"
    parts = []
    seq = 0
    for text in (metar, taf):
        if text is None or text.strip() == "":
            continue
        seq += 1
        with open(temp_txt, 'w', encoding='utf-8') as file:
            file.write(text)
        ret_cd = WL0S0200.translate_MetarTaf('temp', path)
        try:
            os.remove(temp_txt)
        except OSError:
            pass
        if ret_cd != 0:
            return "", ERR_PDF
        # 生成物を退避し、次の翻訳で上書きされないようにする
        for name in ("Metar.pdf", "Taf.pdf"):
            src = path + name
            if os.path.exists(src):
                dst = f"{path}part{seq}_{name}"
                os.replace(src, dst)
                parts.append(dst)
    if not parts:
        return "", ERR_NO_DATA
    if len(parts) == 1:
        os.replace(parts[0], output)
    else:
        merger = PdfWriter()
        for part in parts:
            merger.append(part)
        merger.write(output)
        merger.close()
        for part in parts:
            try:
                os.remove(part)
            except OSError:
                pass
    return output, ERR_OK

def main(selected_option, airport, metar, taf):
    path = make_workdir()
    try:
        if selected_option == "取得・翻訳":
            output, err_msg = get_and_transtale(airport, path)
        elif selected_option == "翻訳":
            output, err_msg = translate_input(metar, taf, path)
        else:
            output, err_msg = "", ERR_KBN
    except Exception:
        cleanup_workdir(path)
        raise
    if err_msg != ERR_OK:
        cleanup_workdir(path)
        return "", err_msg
    return output, err_msg