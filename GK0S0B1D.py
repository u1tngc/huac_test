#PGM-ID:GK0S0B1D
#PGM-NAME:GKユーザー管理セグI/O
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

def get_userName(id):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        with conn.cursor() as cur:
            sql = '''
                SELECT 氏名 FROM ユーザー管理セグ WHERE ユーザーid = %s
            '''
            data = (id,)
            cur.execute(sql, data)
            result = cur.fetchone()
        conn.close()
        return result[0] if result else ""
    except psycopg2.Error as e:
        print(f'エラー内容：{e}')
        return ""
    except Exception as e:
        print(f'エラー内容：{e}')
        return ""


def get_stuList():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        with conn.cursor() as cur:
            sql = '''
                SELECT ユーザーid, 氏名
                  FROM ユーザー管理セグ
                 WHERE 権限 IN (0,1)
                 ORDER BY ユーザーid
            '''
            cur.execute(sql,)
            result = cur.fetchall()
        conn.close()
        return [list(row) for row in result] if result else []
    except psycopg2.Error as e:
        print(f'エラー内容：{e}')
        return []
    except Exception as e:
        print(f'エラー内容：{e}')
        return []
