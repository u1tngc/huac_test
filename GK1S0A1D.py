#PGM-ID:GK0S0A1D
#PGM-NAME:GK擬似谷口履歴セグI/O(オンライン)
#最終更新日:2026/02/04

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

# DB_CONFIG = {
#     "dbname": "huac_gakka", 
#     "user": "taniguchi_tanglin_ic", 
#     "password": "N6eEqr20vmfNV-_McGwfkA", 
#     "host": "huac-tngc-6767.jxf.gcp-asia-southeast1.cockroachlabs.cloud", 
#     "port": 26257,
#     "sslmode": "require",
#     "sslcert": "",
#     "sslkey": "",
#     "sslrootcert": "",
#     "target_session_attrs": "read-write"
# }

def insert_taniguchi(id, kbn,bunya, kaiwa):
    try:
        conn = psycopg2.connect(**DB_CONFIG)  
        with conn.cursor() as cur:
            sql = "INSERT INTO 擬似谷口履歴セグ (学籍番号, 処理日時, 問答区分, 分野, 会話) VALUES (%s, CURRENT_TIMESTAMP AT TIME ZONE 'Asia/Tokyo', %s, %s, %s)"
            data = (id, kbn, bunya, kaiwa)
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


def get_taniguchi(id):
    try:
        conn = psycopg2.connect(**DB_CONFIG)  
        with conn.cursor() as cur:
            sql = 'SELECT * FROM "擬似谷口履歴セグ" WHERE 学籍番号 = %s'
            cur.execute(sql, (id,))
            result = cur.fetchall()  
        conn.close()
        return [list(row) for row in result]
    except psycopg2.Error as e:
        print(f'エラー内容：{e}')
        return []
    except Exception as e:
        print(f'エラー内容：{e}')
        return []