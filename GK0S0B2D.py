#PGM-ID:GK0S0B2D
#PGM-NAME:GKソロ状況管理セグI/O
#最終更新日:2026/09/15

import psycopg2
import os

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

def get_soloJokyo(id, ymd):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        with conn.cursor() as cur:
            sql = '''
                SELECT 適用年月日, ソロ発数, ２３移行有無
                  FROM ソロ状況管理セグ
                 WHERE 学籍番号 = %s AND 適用年月日 <= %s
                 ORDER BY 適用年月日 DESC
                 LIMIT 1
            '''
            data = (id, ymd)
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


def get_soloJokyoAll(ymd):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        with conn.cursor() as cur:
            sql = '''
                SELECT 学籍番号, 適用年月日, ソロ発数, ２３移行有無
                  FROM ソロ状況管理セグ
                 WHERE 適用年月日 <= %s
                 ORDER BY 学籍番号, 適用年月日
            '''
            data = (ymd,)
            cur.execute(sql, data)
            result = cur.fetchall()
        conn.close()
        return [list(row) for row in result] if result else []
    except psycopg2.Error as e:
        print(f'エラー内容：{e}')
        return []
    except Exception as e:
        print(f'エラー内容：{e}')
        return []
