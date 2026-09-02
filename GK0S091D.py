#PGM-ID:GK0S091D
#PGM-NAME:GK定時稼働管理セグI/O(オンライン)
#最終更新日:2026/09/01

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

def get_testInfo():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        with conn.cursor() as cur:
            sql = f'''
                SELECT 機能cd, 日, 月, 火, 水, 木, 金, 土
                FROM 定時稼働管理セグ where 機能cd = 'XA01' or 機能cd = 'XA11' 
                ORDER BY 機能cd
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

def update_test(array):
    try:
        conn = psycopg2.connect(**DB_CONFIG)  
        with conn.cursor() as cur:
            sql = 'UPDATE 定時稼働管理セグ SET 日 = %s, 月 = %s, 火 = %s, 水 = %s, 木 = %s, 金 = %s, 土 = %s WHERE 機能cd = %s'
            data = (array[1], array[2], array[3], array[4], array[5], array[6], array[7], array[0]) 
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