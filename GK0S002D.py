#PGM-ID:GK0S002D
#PGM-NAME:GK履歴管理セグI/O(オンライン)
#最終更新日:

import os

import psycopg2


DB_CONFIG = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "port": 26257,
    "sslmode": "require",
    "sslcert": "",
    "sslkey": "",
    "sslrootcert": "",
    "target_session_attrs": "read-write"
}


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



def get_rireki(user_id):
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


def get_rirekiAll():
    try:
        conn = psycopg2.connect(**DB_CONFIG)  
        with conn.cursor() as cur:
            sql = 'SELECT * FROM "履歴管理セグ"'
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