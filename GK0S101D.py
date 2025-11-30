#PGM-ID:GK0S101D
#PGM-NAME:GK学生管理セグI/O(バッチ)

import psycopg2

DB_CONFIG = {
    "dbname": "huac_gakka", 
    "user": "taniguchi_tanglin_ic", 
    "password": "N6eEqr20vmfNV-_McGwfkA", 
    "host": "huac-tngc-6767.jxf.gcp-asia-southeast1.cockroachlabs.cloud", 
    "port": 26257,
    "sslmode": "require",
    "sslcert": "",
    "sslkey": "",
    "sslrootcert": "",
    "target_session_attrs": "read-write"
}


def get_gakusei_list():
    try:
        conn = psycopg2.connect(**DB_CONFIG)  
        with conn.cursor() as cur:
            sql = 'SELECT * FROM "学生管理セグ" WHERE "出題区分" != %s'
            data = (0,)
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
    

def select_jikayo():
    try:
        conn = psycopg2.connect(**DB_CONFIG)  
        with conn.cursor() as cur:
            sql = 'SELECT * FROM "学生管理セグ" WHERE "出題区分" = %s'
            data = (1,)
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