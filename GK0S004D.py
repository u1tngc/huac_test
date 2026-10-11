#PGM-ID:GK0S004D
#PGM-NAME:GK極秘管理セグI/O(オンライン)
#最終更新日:2026/09/05

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

def insert_Gokuhidata(id):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        with conn.cursor() as cur:
            sql = 'INSERT INTO "極秘管理セグ" (学籍番号, 極秘可能数) VALUES (%s, 0)'
            data = (id, )
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

def get_gokuhiJougen(id):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        with conn.cursor() as cur:
            sql = 'SELECT 極秘可能数 FROM "極秘管理セグ" WHERE 学籍番号 = %s'
            data = (id,)
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
    finally:
        if conn:
            conn.close()

def add_gokuhiJougen(id, amount):
    conn = None
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        with conn.cursor() as cur:
            sql = 'INSERT INTO "極秘管理セグ"(学籍番号, 極秘可能数) VALUES (%s, %s) ON CONFLICT (学籍番号) DO UPDATE SET 極秘可能数 = "極秘管理セグ".極秘可能数 + EXCLUDED.極秘可能数'
            data = (id, amount)
            cur.execute(sql, data)
            conn.commit()
            return 0
    except psycopg2.Error as e:
        print(f'エラー内容{e}')
        return 1
    except Exception.Error as e:
        print(f'エラー内容{e}')
        return 2
    finally:
        if conn:
            conn.close()

