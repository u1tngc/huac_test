#PGM-ID:WL1S0100
#PGM-NAME:WL概況取得
#最終更新日:2026/08/11

import requests
import WX0S0100
import WX0S0102

DEFAULT_INPUT = "360-0222,JP"
# エラーメッセージ
MSG_BOTH_INPUT = "郵便番号と都市名の片方を指定してください。"
MSG_POSTNO = "郵便番号は数字７桁で入力してください。"
MSG_NOT_FOUND = "指定された郵便番号・都市名の気象情報が見つかりません。入力値を確認してください。"
MSG_NETWORK = "気象情報を取得できませんでした。時間をおいて再実行してください。"

def check01(postNo, city):
    # 郵便番号と都市名の同時入力は不可
    if postNo != "" and city != "":
        return MSG_BOTH_INPUT
    # 郵便番号はハイフンなしの数字7桁
    #   ※make_input()で postNo[0:3] + "-" + postNo[3:7] に組み立てるため
    #     ハイフン付きの入力は許可しない
    if postNo:
        # isdigit()単独では全角数字(３６００２２２)も通ってしまうため
        # isascii()と併用して半角数字のみ許可する
        if not (postNo.isascii() and postNo.isdigit()):
            return MSG_POSTNO
        if len(postNo) != 7:
            return MSG_POSTNO
    return ""

def make_input(postNo, city):
    """処理区分(2:郵便番号 3:都市名)とopenWeather用入力値を返す"""
    if postNo == "" and city == "":
        return 2, DEFAULT_INPUT
    if postNo:
        return 2, f"{postNo[0:3]}-{postNo[3:7]},JP"
    return 3, city

def get_gaikyo(postNo, city):
    """気象概況の表示用データを取得する

    前提   : check01()を通過済みの値が渡されること
    戻り値 : (err, gaikyo)
             err != ""  のとき gaikyo は None（取得エラー）
             err == ""  のとき gaikyo は GK_WX_gaikyoOUT.html に渡す辞書

    ※WX0S0100.getWx() は末尾でファイル書き出しとブラウザ起動を行うため使用しない。
      getWx()が内部で呼んでいるデータ生成関数のみを直接呼ぶ。
      （WX0S0100.py / WX0S0102.py は無変更 → WX1M0000・WX1M0010に影響なし）
    """
    shorikbn, iwx_input = make_input(postNo, city)
    try:
        title, now_weather1, now_weather2 = WX0S0100.get_weather(
            [], [], [], iwx_input, shorikbn)
        title, forecast = WX0S0100.get_forecast(
            title, [], iwx_input, shorikbn)
        title.append(WX0S0100.get_asas())
    except KeyError:
        # openWeatherが地点を返さなかった場合（404など）
        return MSG_NOT_FOUND, None
    except (requests.exceptions.Timeout,
            requests.exceptions.ConnectionError):
        return MSG_NETWORK, None
    # 予報を [日][12項目][9時刻] に整形（都市名指定も郵便番号と同じ表示形式に寄せる）
    now_weather2 = [to_web_path(v) for v in now_weather2]
    forecast = [[to_web_path(v) for v in row] for row in forecast]
    forecast, fore_date, arr_len = WX0S0102.remake_forecast(forecast)
    gaikyo = {
        "title": title,
        "now_weather1": now_weather1,
        "now_weather2": now_weather2,
        "forecast": forecast,
        "kinocd": 2,
    }
    return "", gaikyo

def to_web_path(value):
    """WX0S0101が返すローカル用パスをWeb用パスに変換する"""
    if isinstance(value, str) and value.startswith('./fonts/'):
        return '/static' + value[1:]
    return value