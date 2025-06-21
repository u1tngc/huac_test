#PGM-ID:GK0S01XD
#PGM-NAME:GK●●問題セグI/O(オンライン)
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