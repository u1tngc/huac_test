#PGM-ID:GK0S0B3D
#PGM-NAME:GK合宿日程管理セグI/O
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

def get_gasshuku():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        with conn.cursor() as cur:
            sql = '''
                SELECT 年度, 開始年月, 枝番, 名称, 開始年月日, 終了年月日, ソロ不可日数
                  FROM 合宿日程管理セグ
                 ORDER BY 開始年月日, 枝番
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


def get_gasshukuByNendo(nendo):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        with conn.cursor() as cur:
            sql = '''
                SELECT 年度, 開始年月, 枝番, 名称, 開始年月日, 終了年月日, ソロ不可日数
                  FROM 合宿日程管理セグ
                 WHERE 年度 = %s
                 ORDER BY 開始年月日, 枝番
            '''
            data = (nendo,)
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
