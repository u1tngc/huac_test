#PGM-ID:GK0S003D
#PGM-NAME:GK復習問題セグ(オンライン)
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


def check_fukushu(user_id, mondaiNo):
    try:
        conn = psycopg2.connect(**DB_CONFIG)  
        with conn.cursor() as cur:
            sql = 'SELECT * FROM "復習問題セグ" WHERE 学籍番号 = %s AND 分野 = %s AND 区分 = %s AND 問題番号 = %s'
            data = (user_id, mondaiNo[0:1], mondaiNo[1:2], mondaiNo[2:])
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
    

def insert_fukushu(id, mondaiNo, today):
    try:
        conn = psycopg2.connect(**DB_CONFIG)  
        with conn.cursor() as cur:
            sql = 'INSERT INTO "復習問題セグ" (学籍番号, 分野, 区分, 問題番号, 処理年月日) VALUES (%s, %s, %s, %s, %s)'
            data = (id, mondaiNo[0:1], mondaiNo[1:2], mondaiNo[2:], today)
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


def update_fukushu(user_id, mondaiNo, today):
    try:
        conn = psycopg2.connect(**DB_CONFIG)  
        with conn.cursor() as cur:
            sql = 'UPDATE "復習問題セグ" SET 処理年月日 = %s WHERE 学籍番号 = %s AND 分野 = %s AND 区分 = %s AND 問題番号 = %s'
            data = (today, user_id, mondaiNo[0:1], mondaiNo[1:2], mondaiNo[2:])
            cur.execute(sql, data)
            conn.commit()
        return 0  
    except psycopg2.Error as e:
        print(f'エラー内容：{e}')
        return 1
    except Exception as e:
        print(f'エラー内容：{e}')
        return 2