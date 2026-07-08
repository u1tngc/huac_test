#PGM-ID:GK0S071D
#PGM-NAME:GKMSG送信履歴セグI/O(オンライン)
#最終更新日:2026/07/08

import datetime
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

def insert_msg_history(user_id, category, title, body):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        now = datetime.datetime.now(datetime.timezone.utc)
        
        with conn.cursor() as cur:
            sql = '''
                INSERT INTO MSG送信履歴セグ (学籍番号, 送信日時, 区分, タイトル, 本文)
                VALUES (%s, %s, %s, %s, %s)
            '''
            data = (user_id, now, category, title, body)
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


# def get_msg_history(user_id):
#     try:
#         conn = psycopg2.connect(**DB_CONFIG)
#         with conn.cursor() as cur:
#             sql = 'SELECT * FROM "MSG送信履歴セグ" WHERE 学籍番号 = %s ORDER BY 送信日時 DESC'
#             data = (user_id,)
#             cur.execute(sql, data)
#             result = cur.fetchall()
#         conn.close()
#         return [list(row) for row in result] if result else []
#     except psycopg2.Error as e:
#         print(f'エラー内容：{e}')
#         return []
#     except Exception as e:
#         print(f'エラー内容：{e}')
#         return []


# def get_msg_history_by_category(user_id, category):
#     try:
#         conn = psycopg2.connect(**DB_CONFIG)
#         with conn.cursor() as cur:
#             sql = 'SELECT * FROM "MSG送信履歴セグ" WHERE 学籍番号 = %s AND 区分 = %s ORDER BY 送信日時 DESC'
#             data = (user_id, category)
#             cur.execute(sql, data)
#             result = cur.fetchall()
#         conn.close()
#         return [list(row) for row in result] if result else []
#     except psycopg2.Error as e:
#         print(f'エラー内容：{e}')
#         return []
#     except Exception as e:
#         print(f'エラー内容：{e}')
#         return []


# def count_msg_by_category(user_id, category):
#     try:
#         conn = psycopg2.connect(**DB_CONFIG)
#         with conn.cursor() as cur:
#             sql = 'SELECT COUNT(*) FROM "MSG送信履歴セグ" WHERE 学籍番号 = %s AND 区分 = %s'
#             data = (user_id, category)
#             cur.execute(sql, data)
#             result = cur.fetchone()
#         conn.close()
#         return result[0] if result else 0
#     except psycopg2.Error as e:
#         print(f'エラー内容：{e}')
#         return 0
#     except Exception as e:
#         print(f'エラー内容：{e}')
#         return 0
