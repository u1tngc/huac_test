#PGM-ID:GK1S0042
#PGM-NAME:GK学生管理サブ
#最終更新日:2026/08/29

from datetime import datetime
from zoneinfo import ZoneInfo

import GK0S001D
import GK0S081D

def get_gakuseiInfo02():
    ret_array = GK0S001D.get_gakuseiInfo02()
    return ret_array

def get_KaiwaRireki(id):
    rireki = GK0S081D.get_rirekiAll(id)
    if rireki:
        kanriList = GK0S081D.get_kanriName()
        ret_array = []
        temp_array = []
        for ix1 in range(len(rireki)):
            kanriName = get_name(kanriList,rireki[ix1][1])
            if ix1 == 0:
                rireki[ix1].append(kanriName)
                temp_array.append(rireki[ix1])
            else:
                if rireki[ix1][1] == rireki[ix1 - 1][1]:
                    rireki[ix1].append(kanriName)
                    temp_array.append(rireki[ix1])
                else:
                    ret_array.append(temp_array)
                    temp_array = []
                    rireki[ix1].append(kanriName)
                    temp_array.append(rireki[ix1])
        ret_array.append(temp_array)
    else:
        ret_array = []
    return ret_array

def get_name(kanriList,kanricd):
    for ix1 in range(len(kanriList)):
        if kanriList[ix1][0] == kanricd:
            return kanriList[ix1][1]
    return kanricd


def get_KoshinList(gakuseiID):
    """会話履歴更新画面の選択肢を組み立てる
       戻り値：(kanriNoList, kanriKbnList, newKanriKbnList)
         kanriNoList    枝番追加用     [[管理区分, 管理区分名, 管理番号], ...]
         kanriKbnList   管理番号追加用 [[管理区分, 管理区分名], ...]（学生が既に持つ管理区分）
         newKanriKbnList 管理区分追加用 [[管理区分, 管理区分名], ...]（学生がまだ持たない管理区分）"""
    rireki = GK0S081D.get_rirekiAll(gakuseiID)
    kanriList = GK0S081D.get_kanriName()
    existKbn = []
    kanriNoList = []
    for ix1 in range(len(rireki)):
        kanriKbn = rireki[ix1][1]
        kanriNo = rireki[ix1][2]
        if kanriKbn not in existKbn:
            existKbn.append(kanriKbn)
        # 枝番違いは同一明細とみなし、管理区分＋管理番号で重複を除く
        if [kanriKbn, kanriNo] not in [[row[0], row[2]] for row in kanriNoList]:
            kanriNoList.append([kanriKbn, get_name(kanriList, kanriKbn), kanriNo])
    kanriKbnList = [[kbn, get_name(kanriList, kbn)] for kbn in existKbn]
    newKanriKbnList = [[row[0], row[1]] for row in kanriList if row[0] not in existKbn]
    return kanriNoList, kanriKbnList, newKanriKbnList


def insert_Kaiwa(gakuseiID, userID, koshinKbn, kanriKbn, kanriNo, naiyo):
    """会話履歴を1件登録する
       koshinKbn 1=枝番追加 2=管理番号追加 3=管理区分追加
       枝番追加以外は枝番0、管理番号は管理区分内の最大＋1を採番する
       戻り値：(rc, エラーメッセージ)  rc 0=正常 1=エラー"""
    if not naiyo:
        return 1, "内容を入力してください。"
    if len(naiyo) > 1000:
        return 1, "内容は1000文字以内で入力してください。"

    if koshinKbn == "1":
        # 枝番追加：管理区分・管理番号は既存のものを使い、枝番のみ採番する
        if not kanriKbn or not kanriNo:
            return 1, "追記する管理番号を選択してください。"
        rc, maxEdaNo = GK0S081D.get_maxEdaNo(gakuseiID, kanriKbn, kanriNo)
        if rc != 0:
            return 1, "枝番の採番に失敗しました。"
        if maxEdaNo is None:
            return 1, "選択された管理番号の明細が存在しません。"
        edaNo = int(maxEdaNo) + 1
    else:
        # 管理番号追加／管理区分追加：管理番号を採番し、枝番は0とする
        if not kanriKbn:
            return 1, "管理区分を選択してください。"
        rc, maxKanriNo = GK0S081D.get_maxKanriNo(gakuseiID, kanriKbn)
        if rc != 0:
            return 1, "管理番号の採番に失敗しました。"
        kanriNo = get_nextNo(maxKanriNo)
        if kanriNo is None:
            return 1, "管理番号の採番に失敗しました。"
        edaNo = 0

    # 起票者：ログインユーザーの学籍番号から氏名を編集
    kihyosha = GK0S001D.get_gakuseiName(userID)
    if not kihyosha:
        return 1, "起票者の氏名が取得できませんでした。"
    # 開始年月日：機械処理日をYYYYMMDDの文字列8桁で編集
    ymd = datetime.now(ZoneInfo("Asia/Tokyo")).strftime("%Y%m%d")

    err = GK0S081D.insert_rireki(gakuseiID, kanriKbn, kanriNo, edaNo, kihyosha, ymd, naiyo)
    if err != 0:
        return 1, "会話履歴の登録に失敗しました。"
    return 0, ""


def get_nextNo(maxKanriNo):
    """管理番号の次番を4桁ゼロ埋めで返す。採番できない場合は None"""
    if maxKanriNo is None:
        return "0001"
    try:
        nextNo = int(maxKanriNo) + 1
    except (TypeError, ValueError):
        return None
    if nextNo > 9999:
        return None
    return str(nextNo).zfill(4)
