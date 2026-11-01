#PGM-ID:GK0S099D
#PGM-NAME:GKログ管理セグI/O(オンライン)
#最終更新日:2026/01/10

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


def insertLog(gakuseki, shobuncd, shobun_datetime, biko):
    """ログ管理セグにデータを登録"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        with conn.cursor() as cur:
            sql = '''
                INSERT INTO ログ管理セグ (学籍番号, 処分CD, 処分日時, 備考)
                VALUES (%s, %s, %s, %s)
            '''
            data = (gakuseki, shobuncd, shobun_datetime, biko)
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

def get_alertNum(id,date):
    try:
        conn = psycopg2.connect(**DB_CONFIG)  
        with conn.cursor() as cur:
            sql = """
            SELECT COUNT(*) AS 未解答件数 FROM 通報管理セグ
            WHERE 学籍番号 = %s AND 通報年月日 >= %s
            """
            data = (id,date)
            cur.execute(sql,data)
            result = cur.fetchone()  
        conn.close()
        if result:
            return result[0]
        else:
            return None
    except psycopg2.Error as e:
        print(f'エラー内容：{e}')
        return None
    except Exception as e:
        print(f'エラー内容：{e}')
        return None