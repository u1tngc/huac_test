#PGM-ID:GK1S01DB
#PGM-NAME:GK自家用DB操作(オンライン)

import os

import psycopg2


DB_CONFIG = {
    "dbname": "huac_gakka", 
    "user": "taniguchi_tanglin_ic", 
    "password": "N6eEqr20vmfNV-_McGwfkA", 
    "host": "huac-tngc-6767.jxf.gcp-asia-southeast1.cockroachlabs.cloud", 
    "port": 26257,
    "sslmode": "require",
    "sslcert": "",
    "sslkey": "",
    "sslrootcert": "",
    "target_session_attrs": "read-write"
}


def insert_gakusei(id, name, status_cd,kanri_cd):
    try:
        conn = psycopg2.connect(**DB_CONFIG)  
        with conn.cursor() as cur:
            sql = "INSERT INTO 学生管理セグ (学籍番号, 氏名, 状況CD, 出題区分, 解答状況CD, パスワード) VALUES (%s, %s, %s, %s, %s, %s)"
            data = (id, name, status_cd, kanri_cd, 0, '245422kz')
            cur.execute(sql, data)
            conn.commit()
        return 0  
    except psycopg2.IntegrityError as e:
        print(f'エラー内容：{e}')
        return 3  # 主キー衝突エラー
    except psycopg2.Error as e:
        print(f'エラー内容：{e}')
        return 1  
    except Exception as e:
        print(f'エラー内容：{e}')
        return 2   
    finally:
        if conn:
            conn.close() 


def select_gakusei(id):
    try:
        conn = psycopg2.connect(**DB_CONFIG)  # 定数を展開して接続
        with conn.cursor() as cur:
            sql = 'SELECT * FROM "学生管理セグ" WHERE "学籍番号" = %s'
            data = (id,)  
            cur.execute(sql, data)
            result = cur.fetchone()  
        conn.close()
        return list(result) if result else []
    except psycopg2.Error as e:
        print(f'エラー内容：{e}')
        return []
    except Exception as e:
        print(f'エラー内容：{e}')
        return []
    

def get_mondai(bunya):
    try:
        conn = psycopg2.connect(**DB_CONFIG)  
        with conn.cursor() as cur:
            sql = f'SELECT * FROM "{bunya}問題セグ"'
            cur.execute(sql)
            result = cur.fetchall()  
        conn.close()
        return [list(row) for row in result]
    except psycopg2.Error as e:
        print(f'エラー内容：{e}')
        return []
    except Exception as e:
        print(f'エラー内容：{e}')
        return []


def get_gakusei(id,name):
    try:
        conn = psycopg2.connect(**DB_CONFIG)  
        with conn.cursor() as cur:
            if id:
                sql = 'SELECT 学籍番号, 氏名, 状況CD, 解答状況CD FROM 学生管理セグ WHERE 学籍番号 = %s'
                data = (id,)
            else:
                sql = 'SELECT 学籍番号, 氏名, 状況CD, 解答状況CD FROM 学生管理セグ WHERE 氏名 = %s'
                data = (name,)
            cur.execute(sql,data)
            result = cur.fetchone()  
        conn.close()
        return list(result)
    except psycopg2.Error as e:
        print(f'エラー内容：{e}')
        return []
    except Exception as e:
        print(f'エラー内容：{e}')
        return []
    

def update_gakusei(list):
    try:
        conn = psycopg2.connect(**DB_CONFIG)  
        with conn.cursor() as cur:
            sql = 'UPDATE 学生管理セグ SET 氏名 = %s, 状況CD = %s, 出題区分 = %s,解答状況CD = %s WHERE 学籍番号 = %s'
            data = (list[1], list[2], list[3], list[4], list[0]) 
            cur.execute(sql, data)
            conn.commit()
        conn.close()
        return 0 
    except psycopg2.Error as e:
        print(f'エラー内容：{e}')
        return 1
    except Exception as e:
        print(f'エラー内容：{e}')
        return 2
    

def get_gakuseiAll():
    try:
        conn = psycopg2.connect(**DB_CONFIG)  
        with conn.cursor() as cur:
            sql = 'SELECT * FROM "学生管理セグ"'
            cur.execute(sql)
            result = cur.fetchall()  
        conn.close()
        return [list(row) for row in result]
    except psycopg2.Error as e:
        print(f'エラー内容：{e}')
        return []
    except Exception as e:
        print(f'エラー内容：{e}')
        return []


def update_lastLogin(id):
    try:
        conn = psycopg2.connect(**DB_CONFIG) 
        with conn.cursor() as cur:
            sql = """
            UPDATE 学生管理セグ SET 最終ログイン日時 = CURRENT_TIMESTAMP AT TIME ZONE 'Asia/Tokyo' WHERE 学籍番号 = %s
            """
            data = (id,) 
            cur.execute(sql, data)
            conn.commit()
        conn.close()
        return 0  
    except psycopg2.Error as e:
        print(f'エラー内容：{e}')
        return 1
    except Exception as e:
        print(f'エラー内容：{e}')
        return 2
    

def update_password(id,password):
    try:
        conn = psycopg2.connect(**DB_CONFIG)  
        with conn.cursor() as cur:
            sql = """
            UPDATE 学生管理セグ SET パスワード = %s WHERE 学籍番号 = %s
            """
            data = (password, id) 
            cur.execute(sql, data)
            conn.commit()
        conn.close()
        return 0  
    except psycopg2.Error as e:
        print(f'エラー内容：{e}')
        return 1
    except Exception as e:
        print(f'エラー内容：{e}')
        return 2


def check_rireki(user):
    try:
        conn = psycopg2.connect(**DB_CONFIG)  # 定数を展開して接続
        with conn.cursor() as cur:
            sql = 'SELECT * FROM "履歴管理セグ" WHERE 学籍番号 = %s AND 状況CD = %s'
            data = (user,0,)  
            cur.execute(sql, data)
            result = cur.fetchone()  
        conn.close()
        return list(result) if result else []
    except psycopg2.Error as e:
        print(f'エラー内容：{e}')
        return []
    except Exception as e:
        print(f'エラー内容：{e}')
        return []
    

def update_rireki01(user_id, shoriYMD, mondai_no,column, result):
    try:
        conn = psycopg2.connect(**DB_CONFIG)  
        with conn.cursor() as cur:
            sql_map = {
                "解答結果１": 'UPDATE 履歴管理セグ SET 解答結果１ = %s WHERE 学籍番号 = %s AND 処理年月日 = %s AND 問題番号１ = %s',
                "解答結果２": 'UPDATE 履歴管理セグ SET 解答結果２ = %s WHERE 学籍番号 = %s AND 処理年月日 = %s AND 問題番号２ = %s',
                "解答結果３": 'UPDATE 履歴管理セグ SET 解答結果３ = %s WHERE 学籍番号 = %s AND 処理年月日 = %s AND 問題番号３ = %s',
                "解答結果４": 'UPDATE 履歴管理セグ SET 解答結果４ = %s WHERE 学籍番号 = %s AND 処理年月日 = %s AND 問題番号４ = %s',
                "解答結果５": 'UPDATE 履歴管理セグ SET 解答結果５ = %s WHERE 学籍番号 = %s AND 処理年月日 = %s AND 問題番号５ = %s'
            }
            sql = sql_map.get(column)
            data = (int(result), user_id, shoriYMD, mondai_no) 
            cur.execute(sql, data)
            conn.commit()
        conn.close()
        return 0  
    except psycopg2.Error as e:
        print(f'エラー内容：{e}')
        return 1
    except Exception as e:
        print(f'エラー内容：{e}')
        return 2
    

def update_rireki02(user_id, shoriYMD):
    try:
        conn = psycopg2.connect(**DB_CONFIG)  
        with conn.cursor() as cur:
            sql = 'UPDATE 履歴管理セグ SET 状況CD = 9 WHERE 学籍番号 = %s AND 処理年月日 = %s'
            data = (user_id, shoriYMD) 
            cur.execute(sql, data)
            conn.commit()
        conn.close()
        return 0  
    except psycopg2.Error as e:
        print(f'エラー内容：{e}')
        return 1
    except Exception as e:
        print(f'エラー内容：{e}')
        return 2


def get_test(bunya, kubun, mondai_no):
    conn = None
    try:
        conn = psycopg2.connect(**DB_CONFIG)  
        with conn.cursor() as cur:
            sql_map = {
                "A": 'SELECT * FROM "法規問題セグ" WHERE 区分 = %s AND 問題番号 = %s',
                "B": 'SELECT * FROM "工学問題セグ" WHERE 区分 = %s AND 問題番号 = %s',
                "C": 'SELECT * FROM "気象問題セグ" WHERE 区分 = %s AND 問題番号 = %s',
                "D": 'SELECT * FROM "情報問題セグ" WHERE 区分 = %s AND 問題番号 = %s',
                "E": 'SELECT * FROM "その他問題セグ" WHERE 区分 = %s AND 問題番号 = %s'
            }
            sql = sql_map.get(bunya)

            if sql is None:
                print(f"無効な分野指定: {bunya}")
                return None  

            cur.execute(sql, (kubun, mondai_no))
            result = cur.fetchone()
            return list(result) if result else None

    except psycopg2.Error as e:
        print(f"データベースエラー: {e}")
        return None

    except Exception as e:
        print(f"予期せぬエラー: {e}")
        return None

    finally:
        if conn:
            conn.close()  # 接続を確実に閉じる


def get_rirekiAll(user_id):
    try:
        conn = psycopg2.connect(**DB_CONFIG)  
        with conn.cursor() as cur:
            sql = 'SELECT * FROM "履歴管理セグ" WHERE 学籍番号 = %s'
            data = (user_id,)
            cur.execute(sql,data)
            result = cur.fetchall()  
        conn.close()
        return [list(row) for row in result]
    except psycopg2.Error as e:
        print(f'エラー内容：{e}')
        return []
    except Exception as e:
        print(f'エラー内容：{e}')
        return []
    

def update_kaitoJyokyoCD(user_id):
    try:
        conn = psycopg2.connect(**DB_CONFIG)  
        with conn.cursor() as cur:
            sql = 'UPDATE 学生管理セグ SET 解答状況CD = 0 WHERE 学籍番号 = %s'
            data = (user_id,) 
            cur.execute(sql, data)
            conn.commit()
        conn.close()
        return 0  
    except psycopg2.Error as e:
        print(f'エラー内容：{e}')
        return 1
    except Exception as e:
        print(f'エラー内容：{e}')
        return 2