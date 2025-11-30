#PGM-ID:GK1S0101
#PGM-NAME:GK自家用小テストCHK
#最終更新日:2025/12/01

import datetime
import os
import random
import shutil
import tempfile

import GK0S101D
import GK0S102D
import GK0S11XD
import GK1S0102
import GK1S0103


# ZIPパスワード
ZIP_PASSWORD = "563029"

# 出力先フォルダー
OUTPUT_DIR = r"C:\Users\tanig\OneDrive\開発言語\谷口ツール\HUAC学科ツール\HUAC学科ツール\ＤＢバックアップ"

# 7-Zipのパス（通常のインストール先）
SEVEN_ZIP_PATH = r"C:\Program Files\7-Zip\7z.exe"

# テーブル情報（テーブル名とカラム名）
TABLES = {
    "学生管理セグ": [
        "学籍番号", "氏名", "状況cd", "出題区分", "解答状況cd",
        "パスワード", "最終ログイン日時"
    ],
    "復習問題セグ": [
        "学籍番号", "分野", "区分", "問題番号", "処理年月日",
        "出題区分", "復習状況"
    ],
    "履歴管理セグ": [
        "学籍番号", "処理年月日", "状況cd",
        "問題番号１", "解答結果１",
        "問題番号２", "解答結果２",
        "問題番号３", "解答結果３",
        "問題番号４", "解答結果４",
        "問題番号５", "解答結果５",
        "解答日時"
    ],
}


def checkDB():
    gakusei_list = GK0S101D.get_gakusei_list()
    sekkyo_list = []
    for ix1 in range(len(gakusei_list)):
        rireki_list = GK0S102D.get_rireki_list(gakusei_list[ix1][0])
        kaitou_umu = 0
        if rireki_list:
            for ix2 in range(len(rireki_list)):
                if rireki_list[ix2][2] == 0:
                    kaitou_umu = kaitou_umu + 1
            if (kaitou_umu >= 2 and gakusei_list[ix1][3] == 1) or (kaitou_umu >= 1 and gakusei_list[ix1][3] == 2):
                sekkyo_list.append([gakusei_list[ix1][0],gakusei_list[ix1][1]])
            else:
                ret_cd = GK0S101D.update_jokyoCD(gakusei_list[ix1][0],0)
    GK1S0102.send_mail(sekkyo_list)
    jikayo_list = GK0S101D.select_jikayo()
    # if jikayo_list:
    #     for ix1 in range(len(jikayo_list)):
    #         ret_cd = GK0S103D.delete_fukushu(jikayo_list[ix1][0])


def create_rireki():
    gakusei_list = GK0S101D.get_gakusei_list()
    shoriYYYYMMDD = datetime.datetime.today().strftime("%Y%m%d")
    for ix1 in range(len(gakusei_list)):
        print(gakusei_list[ix1])
        mondai_list = []
        if gakusei_list[ix1][3] == 1:
            for bunya in ["法規", "工学", "気象", "情報", "その他"]:
                mondai = GK0S11XD.get_mondai(bunya)
                random_row = random.choice(mondai)
                mondai_list.append(f"{random_row[0]}{random_row[1]}{random_row[2]}")
        elif gakusei_list[ix1][3] == 2:
            mondai = GK0S11XD.get_mondai("赤帽")
            mondai_array = random.sample(mondai,5)
            for ix2 in range(5):
                mondai_list.append(f"{mondai_array[ix2][0]}{mondai_array[ix2][1]}{mondai_array[ix2][2]}")
        GK0S102D.insert_rireki(gakusei_list[ix1][0], shoriYYYYMMDD, mondai_list)


def backUpDB():
    """メイン処理"""
    print("=" * 60)
    print("データベースバックアップ処理開始")
    print("=" * 60)
    
    # 処理年月日取得
    process_date = datetime.now().strftime("%Y%m%d")
    print(f"処理年月日: {process_date}")
    print(f"出力先: {OUTPUT_DIR}")
    print()
    
    # 出力ディレクトリ作成
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # 一時ディレクトリ作成
    temp_dir = tempfile.mkdtemp()
    
    try:
        csv_files = []
        csv_files = GK1S0103.create_csv()            
        # ZIPファイル作成（7-Zip使用）
        zip_filename = f"ＤＢバックアップ_{process_date}.zip"
        zip_path = os.path.join(OUTPUT_DIR, zip_filename)
        
        GK1S0103.create_password_zip_7z(csv_files, zip_path, ZIP_PASSWORD)
        
        print("\n" + "=" * 60)
        print("処理完了")
        print("=" * 60)
        print(f"\n作成されたファイル:")
        print(f"  {zip_path}")
        print(f"\nZIP内のファイル:")
        for csv_file in csv_files:
            print(f"  - {os.path.basename(csv_file)}")
        print(f"\nZIPパスワード: {ZIP_PASSWORD}")
        
    finally:
        # 一時ディレクトリ削除
        shutil.rmtree(temp_dir)
        print("\n一時ファイルを削除しました")

