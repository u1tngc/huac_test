#PGM-ID:GK1S0042
#PGM-NAME:GK学科機能メイン
#最終更新日:2026/09/04

from datetime import datetime
from zoneinfo import ZoneInfo
import os

import GK0S001D
import GK0S081D
import GK0S082D
import PK0S0002

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
        ret_cd, maxEdaNo = GK0S081D.get_maxEdaNo(gakuseiID, kanriKbn, kanriNo)
        if ret_cd != 0:
            return 1, "枝番の採番に失敗しました。"
        if maxEdaNo is None:
            return 1, "選択された管理番号の明細が存在しません。"
        edaNo = int(maxEdaNo) + 1
    else:
        # 管理番号追加／管理区分追加：管理番号を採番し、枝番は0とする
        if not kanriKbn:
            return 1, "管理区分を選択してください。"
        ret_cd, maxKanriNo = GK0S081D.get_maxKanriNo(gakuseiID, kanriKbn)
        if ret_cd != 0:
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
    else:
        gmail_info = [os.getenv("MAIL_FROM"), os.getenv("MAIL_PASS")]
        # send_mail内でTOヘッダを", ".join(to)しているためリストで渡す
        to = ["taniguchi.tanglin@icloud.com"]
        cc = ""
        title = "【通知】会話履歴の更新"
        mail = get_mailBody(gakuseiID, kanriKbn, kanriNo)
        ret = PK0S0002.send_mail(gmail_info,to,cc,title,mail)
        if not ret:
            # 登録自体は完了しているため、通知失敗はログ出力のみとする
            print("会話履歴更新の通知メール送信に失敗しました。")
    return 0, ""


def get_mailBody(gakuseiID, kanriKbn, kanriNo):
    """会話履歴更新の通知メール本文を編集する
       追加したデータと同一の管理区分・管理番号のデータを全枝番分出力する"""
    gakuseiName = GK0S001D.get_gakuseiName(gakuseiID)
    kanriName = get_name(GK0S081D.get_kanriName(), kanriKbn)
    rireki = GK0S081D.get_rirekiByNo(gakuseiID, kanriKbn, kanriNo)

    mail = []
    mail.append(f"学生名：{gakuseiName}（{gakuseiID}）")
    mail.append(f"管理区分：{kanriName}（{kanriKbn}）")
    mail.append("")
    mail.append("下記情報を追加したデータと同一の管理区分・管理番号のデータ全件です。")
    mail.append("")
    if rireki:
        for ix1 in range(len(rireki)):
            mail.append("------------------------------------------------------------")
            mail.append(f"管理番号：{rireki[ix1][2]}")
            mail.append(f"日　　付：{get_ymd(rireki[ix1][5])}")
            mail.append(f"起 票 者：{rireki[ix1][4]}")
            mail.append(f"内　　容：{rireki[ix1][6]}")
        mail.append("------------------------------------------------------------")
    else:
        mail.append("該当データが取得できませんでした。")
    return "\n".join(mail)


def get_ymd(ymd):
    """YYYYMMDDの8桁文字列をYYYY/MM/DDに編集する"""
    if ymd and len(ymd) == 8:
        return f"{ymd[0:4]}/{ymd[4:6]}/{ymd[6:8]}"
    return ymd


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


def get_kanriName():
    ret_array = GK0S082D.get_kanriName()
    return ret_array


def get_task1(id):
    task_list = GK0S082D.get_task01(id)
    if task_list:
        for ix1 in range(len(task_list)):
            name = GK0S001D.get_gakuseiName(task_list[ix1][4])
            task_list[ix1].append(name)
            ymd = get_ymd(task_list[ix1][6])
            task_list[ix1][6] = ymd
    return task_list
