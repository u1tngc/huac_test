#PGM-ID:GK1S0040
#PGM-NAME:GK自家用DB-CNTL
#最終更新日:2026/01/10

from datetime import datetime
from zoneinfo import ZoneInfo
import re

import GK0S001D
import GK0S002D
import GK0S031D
import GK0S041D
import GK0S051D
import GK0S052D
import GK0S099D

def get_gakusei(id,authority):
    gakusei_list = GK0S001D.get_gakusei(id)
    if gakusei_list:
        if gakusei_list[2] in [7,8,9] and authority in [0,1,2,3,4,5,6,7,8]:
            err = "当ユーザーの訂正は管理者のみが可能です"
        else:
            err = ""
    else:
        err = "DB相手無し"
    status_dict = {
        0: "学生",
        1: "自家用",
        2: "卒部生",
        3: "退部済",
        4: "",
        5: "",
        6: "学科班",
        7: "学科班主任",
        8: "教官",
        9: "管理者"
        }
    kanri_dict = {
            0 : "出題無",
            1 : "自家用",
            2 : "赤帽"       
    }  
    shikaku_dict = {
            0 : "練許生",
            1 : "自家用",
            2 : "教証"             
    }
    gakusei_list[2] = status_dict[gakusei_list[2]]
    gakusei_list[3] = kanri_dict[gakusei_list[3]]
    gakusei_list[4] = shikaku_dict[gakusei_list[4]]
    return gakusei_list, err


def get_gakuseiAll():
    status_dict = {
        0: "学生",
        1: "自家用",
        2: "卒部生",
        3: "退部済",
        4: "", 
        5: "",
        6: "学科班",
        7: "学科班主任",
        8: "教官",
        9: "管理者"
        }
    kanri_dict = {
            0 : "出題無",
            1 : "自家用",
            2 : "赤帽"       
    }  
    shikaku_dict = {
            0 : "練許生",
            1 : "自家用",
            2 : "教証"             
    }  
    array = GK0S001D.get_gakuseiAll()
    for ix1 in range(len(array)):
        array[ix1][2] = status_dict[array[ix1][2]]
        array[ix1][3] = kanri_dict[array[ix1][3]]
        array[ix1][4] = shikaku_dict[array[ix1][4]]
        array[ix1][6] = timestamp_to_date(array[ix1][6])
    return array


def timestamp_to_date(timestamp):
    if timestamp is None:
        return "未ログイン"
    date_str = timestamp.strftime("%Y/%m/%d/%H:%M")
    return date_str

"""
def check01(id,name):
    if id == "" and name == "":
        err = "学生番号もしくは氏名を入力してください。"
    else:
        err = ""
    return err
"""

def check02(name,status,answer):
    if not name or not status or not answer:
        return "未入力項目があります。"
    if len(name) > 10:
        return "氏名は10字以内で入力してください。"
    try:
        dummy = int(status)
        if len(status) != 1:
            return "状況CDは1桁の数字で入力してください。"
    except ValueError:
        return "状況CDは半角数字で入力してください。"
    try:
        dummy = int(answer)
        if len(answer) != 1:
            return "状況CDは1桁の数字で入力してください。"
    except ValueError:
        return "状況CDは半角数字で入力してください。"
    return ""
    

def check03(pass1,pass2):
    if pass1 != pass2:
        return "１回目と２回目で入力値が異なります。"
    else:
        if len(pass1) < 6 or len(pass1) > 30:
            return "パスワードは６字以上３０字以内で設定してください。"
        if not pass1.isalnum():
            return "パスワードは半角英数字で設定してください。"
        if not any(ix1.isdigit() for ix1 in pass1):
            return "パスワードは文字と数字を組み合わせてください。"
        if not any(ix1.isalpha() for ix1 in pass1):
            return "パスワードは文字と数字を組み合わせてください。"
        return ""


def check04(id, name, status_cd, shikaku_cd):
    if len(id) != 7:
        return "学籍番号が不正な値です。"
    pattern = r'^\d{2}[A-Z]\d{4}$'
    if not re.match(pattern, id):
        return "学籍番号が不正な値です。"
    if len(name) > 10:
        return "氏名は10字以内で入力してください。"
    if ' ' in name or '　' in name:
        return "氏名は空白を入れずに入力してください。"
    return ""

def check05(old, new):
    if old[4] == "練許生" and new[4] == 1:
        ret_cd = 1
    else:
        ret_cd = 0
    return ret_cd

def check06(kekka):
    if kekka[5] == "" and (kekka[0] != 0 or kekka[1] != 0 or kekka[2] != 0 or kekka[3] != 0 ):
        return "有効期間を入力してください。"
    elif kekka[5] != "" and (kekka[0] == 0 and kekka[1] == 0 and kekka[2] == 0 and kekka[3] == 0 ):
        return "学科試験結果を入力してください。"
    else:
        return ""

def check07(date, name):
    has_gakusei_chk = date[4] != ""
    
    for ix1 in range(5):  # 0～4をチェック
        if has_gakusei_chk and date[ix1] == "":
            return "中間CHKの状況を入力してください。"
        if (date[ix1] == "") != (name[ix1] == ""):
            return "日付未入力のCHKがあります。" if date[ix1] == "" else "担当者未入力のCHKがあります。"
        if len(name[ix1]) > 8:
            return "担当者名は8字以内で入力してください。"
    if date[5] != "" and not has_gakusei_chk:
        return "学生CHKが未入力です。"
    
    return ""

def check08(date,id):
    kamoku = ["法規", "気象", "工学", "情報"]
    flg = [0,0,0,0,0,0]
    for ix1 in range(len(kamoku)):
        if date[ix1] != "":
            rate = GK0S051D.get_yoreiRate(kamoku[ix1], id)
            if rate != 100:
                return f"{kamoku[ix1]}の養成進捗率が100%未満です。"
            flg[ix1] = 1
    if date[4] != "":
        for ix1 in range(len(flg)):
            if flg[ix1] == 0:
                return "学生チェックの結果は、全科目の養成進捗率が100%でないと入力できません。" 
    return ""

def update_gakusei(update_gakusei):
    if update_gakusei[4] == 1:
        update_gakusei[3] = 0
    err = GK0S001D.update_gakusei(update_gakusei)       
    return ""

def insert_gakusei(id, name, status_cd, kanri_cd, shikaku_cd):
    err = GK0S001D.insert_gakusei(id, name, status_cd, kanri_cd, shikaku_cd)
    if err == 3:
        return "入力した学籍番号は登録済みです。"
    if shikaku_cd == 0:
        err = GK0S031D.insert_data(id)
        err = GK0S041D.insert_chkList(id,1)
        err = GK0S041D.insert_chkList(id,2)
    return ""    

def update_password(user_id,password):
    err = GK0S001D.update_password(user_id,password)
    return ""        

def get_rireki(user_id):
    list = GK0S002D.get_rireki(user_id)
    number = [4,6,8,10,12]
    result = {
        0 : "未",
        1 : "〇",
        2 : "△",
        3 : "✕"
    }
    cd = {
        0:"未解答",
        9:"解答済"
    }
    if list:
        for ix1 in range(len(list)):
            list[ix1][2] = cd[list[ix1][2]]  
            for ix2 in range(len(number)):
                list[ix1][number[ix2]] = result[list[ix1][number[ix2]]]
        ret_list = sorted(list, key=lambda x: x[1], reverse=True)
        return ret_list

    return []

def get_rirekiAll():
    list = GK0S002D.get_rirekiAll()
    number = [4,6,8,10,12]
    result = {
        0 : "未",
        1 : "〇",
        2 : "△",
        3 : "✕"
    }
    cd = {
        0:"未解答",
        9:"解答済"
    }
    if list:
        for ix1 in range(len(list)):
            list[ix1][2] = cd[list[ix1][2]]  
            for ix2 in range(len(number)):
                list[ix1][number[ix2]] = result[list[ix1][number[ix2]]]
        ret_list = sorted(list, key=lambda x: x[1], reverse=True)
        return ret_list

    return []

def get_gakuseiInfo01():
    ret_array = GK0S001D.get_gakuseiInfo01()
    return ret_array

def get_gakuseiInfo00(authority):
    ret_array = GK0S001D.get_gakuseiInfo00(authority)
    return ret_array

def get_renkyosei():
    ret_array = GK0S001D.get_renkyosei()
    return ret_array

def get_gakuseiName(id):
    ret_array = GK0S001D.get_gakuseiName(id)
    return ret_array

def delete_data(id):
    err = GK0S031D.delete_data(id)
    err = GK0S041D.delete_data(id)
    return err

def get_gakkaShiken(id):
    gakkaShiken = GK0S031D.get_gakkaShiken(id)
    return gakkaShiken

def update_gakkaShiken(id,kekka):
    dt = datetime.now(ZoneInfo("Asia/Tokyo"))
    ymd = dt.strftime("%Y%m%d")
    updateInfo=[id,kekka[0],kekka[1],kekka[2],kekka[3],kekka[4],kekka[5], ymd]
    err1 = GK0S031D.update_gakkaShiken(updateInfo)

def get_gakkaShikenAll():
    kekka_dict = {
            0 : "未",
            1 : "●",
            2 : "×"             
    }  
    array = GK0S031D.get_gakkaShikenAll()
    for ix1 in range(len(array)):
        array[ix1][1] = kekka_dict[array[ix1][1]]
        array[ix1][2] = kekka_dict[array[ix1][2]]
        array[ix1][3] = kekka_dict[array[ix1][3]]
        array[ix1][4] = kekka_dict[array[ix1][4]]
        array[ix1][5] = kekka_dict[array[ix1][5]]
        if array[ix1][6]:
            array[ix1][6] = f'{array[ix1][6][0:4]}/{array[ix1][6][4:6]}/{array[ix1][6][6:]}'
        if array[ix1][7]:
            array[ix1][7] = f'{array[ix1][7][4:6]}/{array[ix1][7][6:]}'
    return array

def get_chkListAll():
    temp_array1 = GK0S041D.get_chkListAll()
    ret_array = []
    for ix1 in range(0, len(temp_array1) - 1, 2):
        if temp_array1[ix1][0] == temp_array1[ix1 + 1][0]:
            # 1行目: index 0, 2以外を取得（氏名、法規～教官chk）
            row = [v for i, v in enumerate(temp_array1[ix1]) if i not in (0, 2)]
            # 2行目: index 0, 1, 2以外を追加（法規～教官chk）
            row += [v for i, v in enumerate(temp_array1[ix1 + 1]) if i not in (0, 1, 2)]
            ret_array.append(row)    
    return ret_array 

def get_chkList(id,kbn):
        temp_array1 = GK0S041D.get_chkList(id)
        ret_array = []
        for ix1 in range(0, len(temp_array1) - 1, 2):
            if temp_array1[ix1][0] == temp_array1[ix1 + 1][0]:
                # 1行目: index 0, 2以外を取得（氏名、法規～教官chk）
                ret_array = [v for i, v in enumerate(temp_array1[ix1]) if i not in (0, 2)]
                # 2行目: index 0, 1, 2以外を追加（法規～教官chk）
                ret_array += [v for i, v in enumerate(temp_array1[ix1 + 1]) if i not in (0, 1, 2)]   
        return ret_array 

def update_chkList(date_array, name_array):
    err = GK0S041D.update_chkList(date_array)
    err = GK0S041D.update_chkList(name_array)
    return err

def get_yoseiJokyo(id):
    yoseiJokyo = GK0S051D.get_yoseiJokyo(id)
    ret_array2 = []
    if yoseiJokyo:
        yosei = GK0S052D.get_yoseiAll()
        ret_array1 = []
        temp_array = []
        for ix1 in range(len(yosei)):
            temp_name = yosei[ix1][2]
            temp_date = ""
            temp_bunya = ""
            for ix2 in range(len(yoseiJokyo)):
                if yosei[ix1][0] == yoseiJokyo[ix2][1]:
                    temp_date = yoseiJokyo[ix2][3]
                    temp_bunya = yosei[ix1][1]
                    if temp_date != "":
                        temp_date = temp_date[0:4] + "/" + temp_date[4:6] + "/" + temp_date[6:8]
                    break
            temp_array = [temp_bunya, temp_name, temp_date]
            ret_array1.append(temp_array)
        summary_array = GK0S051D.get_yoseiJokyoSum(id)
        ret_array2.append(["法　規", summary_array[0]])
        ret_array2.append(["工　学", summary_array[1]])
        ret_array2.append(["気　象", summary_array[2]])
        ret_array2.append(["情　報", summary_array[3]])
        ret_array2.append(["衛　生", summary_array[4]])
        ret_array2.append(["六項目", summary_array[5]])
        return ret_array1, ret_array2
    return [], []

def get_yoseiSumAll():
    rows = GK0S051D.get_yoseiSumAll()
    if not rows:
        return []
    
    result_map = {}
    for row in rows:
        name, bunya, ratio = row
        if name not in result_map:
            result_map[name] = {'法規': 0, '工学': 0, '気象': 0, '情報': 0, '衛生': 0, '六項目': 0}
        result_map[name][bunya] = int(ratio) if ratio is not None else 0
    
    ret_array = []
    for name, bunya_data in result_map.items():
        ret_array.append([
            name,
            f"{bunya_data['法規']}%",
            f"{bunya_data['工学']}%",
            f"{bunya_data['気象']}%",
            f"{bunya_data['情報']}%",
            f"{bunya_data['衛生']}%",
            f"{bunya_data['六項目']}%"
        ])
    
    return ret_array

def get_yoseiAllDataForCSV():
    """全学生の養成状況データをCSV用に整形"""
    data = GK0S051D.get_yoseiAllData()
    if not data:
        return None
    
    items = data['items']  # [(養成cd, 分野, 養成名), ...]
    students = data['students']  # [(学籍番号, 氏名), ...]
    statuses = data['statuses']  # [(学籍番号, 養成cd, 養成日), ...]
    progress = data['progress']  # [(学籍番号, 分野, 割合), ...]
    
    # 養成状況を辞書化（キー: (学籍番号, 養成cd) -> 養成日）
    status_dict = {(s[0], s[1]): s[2] for s in statuses}
    
    # 進捗率を辞書化（キー: (学籍番号, 分野) -> 割合）
    progress_dict = {(p[0], p[1]): int(p[2]) if p[2] else 0 for p in progress}
    
    # CSVデータ構築
    csv_data = []
    
    # ヘッダー行（1行目）
    header = ['分野', '養成名'] + [s[1] for s in students]  # 氏名のみ
    csv_data.append(header)
    
    # データ行
    for item in items:
        yosei_cd = item[0]
        bunya = item[1]  # 分野
        yosei_name = item[2]
        
        row = [bunya, yosei_name]
        
        # 各学生の養成日を追加
        for student in students:
            gakuseki = student[0]
            yosei_date = status_dict.get((gakuseki, yosei_cd), '')
            # 養成日をフォーマット (YYYYMMDD -> YYYY/MM/DD)
            if yosei_date and len(yosei_date) == 8:
                formatted_date = f"{yosei_date[0:4]}/{yosei_date[4:6]}/{yosei_date[6:8]}"
                row.append(formatted_date)
            else:
                row.append('')
        
        csv_data.append(row)
    
    # 進捗率の行を追加
    分野リスト = ['法規', '工学', '気象', '情報', '衛生', '六項目']
    for 分野 in 分野リスト:
        row = [分野, f'{分野}進捗率']
        for student in students:
            gakuseki = student[0]
            ratio = progress_dict.get((gakuseki, 分野), 0)
            row.append(f'{ratio}%')
        csv_data.append(row)
    
    return csv_data

def get_yoseiKamokuAll():
    temp_array = GK0S052D.get_yoseiAll()
    ret_array = []
    for ix1 in range(len(temp_array)):
        ret_array.append([temp_array[ix1][0], f"{temp_array[ix1][1]}：{temp_array[ix1][2]}"])
    return ret_array

def get_youseiJyokyo(yoseiKamoku, yoseiStudent, yoseiDateNew):
    ret_array = []
    if yoseiDateNew:
            yoseiDateNew = f'{yoseiDateNew[0:4]}/{yoseiDateNew[4:6]}/{yoseiDateNew[6:]}'
    for ix1 in range(len(yoseiStudent)):
        yoseiDateOld = GK0S051D.get_yoseiDate(yoseiStudent[ix1], yoseiKamoku)
        name = GK0S001D.get_gakuseiName(yoseiStudent[ix1])
        dt = datetime.now(ZoneInfo("Asia/Tokyo"))
        if yoseiDateOld:
            yoseiDateOld = f'{yoseiDateOld[0:4]}/{yoseiDateOld[4:6]}/{yoseiDateOld[6:]}'
        ret_array.append([yoseiStudent[ix1], name, yoseiDateOld, yoseiDateNew])
    return ret_array


def update_yoseiJokyo(wk54updateInfo, yoseiKamoku):
    for ix1 in range(len(wk54updateInfo)):
        wk54updateInfo[ix1][3] = wk54updateInfo[ix1][3].replace("/","")
        err = GK0S051D.update_yoseiJokyo(yoseiKamoku, wk54updateInfo[ix1][0], wk54updateInfo[ix1][3])
    return err


def insertLog(user,shobuncd,biko):
    dt = datetime.now(ZoneInfo("Asia/Tokyo"))
    ymd = dt.strftime("%Y%m%d%H%M")
    bunya_array = {
        "A" : "法規",
        "B" : "工学",
        "C" : "気象",
        "D" : "情報",
        "E" : "その他",
        "Z" : "赤帽",
        "X" : "極秘"
    }
    kbn_array = {
        "1" : "小テスト",
        "2" : "練習問題"
    }
    if shobuncd == "A001":
        bunyacd = biko[0:1]
        biko = bunya_array.get(bunyacd, "")
    if shobuncd == "A021":
        biko = kbn_array.get(biko,"")
    err = GK0S099D.insertLog(user,shobuncd,ymd,biko)