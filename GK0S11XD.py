#PGM-ID:GK0S11XD
#PGM-NAME:GK●●問題セグI/O(バッチ)

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