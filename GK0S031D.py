#PGM-ID:GK0S031D
#PGM-NAME:GK学科試験管理セグI/O(オンライン)
#最終更新日:2026/01/24

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


def insert_data(id):
    try:
        conn = psycopg2.connect(**DB_CONFIG)  
        with conn.cursor() as cur:
            sql = "INSERT INTO 学科試験管理セグ (学籍番号) VALUES (%s)"
            data = (id,)
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
    

def get_gakkaShiken(id):
    try:
        conn = psycopg2.connect(**DB_CONFIG)  
        with conn.cursor() as cur:
            sql = 'SELECT * FROM 学科試験管理セグ WHERE 学籍番号 = %s'
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
    

def update_gakkaShiken(updateInfo):
    try:
        conn = psycopg2.connect(**DB_CONFIG)  
        with conn.cursor() as cur:
            sql = 'UPDATE 学科試験管理セグ SET 法規 = %s, 工学 = %s, 気象 = %s, 航法 = %s, 航特 = %s, 有効期限 = %s, 更新日 = %s WHERE 学籍番号 = %s'
            data = (updateInfo[1], updateInfo[2], updateInfo[3], updateInfo[4], updateInfo[5], updateInfo[6], updateInfo[7], updateInfo[0]) 
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
    

def get_gakkaShikenAll():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        with conn.cursor() as cur:
            sql = '''
                SELECT s.氏名,
                       g.法規,
                       g.工学,
                       g.気象,
                       g.航法,
                       g.航特,
                       g.有効期限,
                       g.更新日,
                       g.備考
                FROM "学科試験管理セグ" g
                JOIN "学生管理セグ" s
                  ON g.学籍番号 = s.学籍番号
            '''
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


def get_shiken_info(gakuseki):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        with conn.cursor() as cur:
            sql = 'SELECT 法規, 工学, 気象, 航法, 有効期限 FROM 学科試験管理セグ WHERE 学籍番号 = %s'
            data = (gakuseki,)
            cur.execute(sql, data)
            result = cur.fetchone()
        conn.close()
        return list(result) if result else [0, 0, 0, 0, '']
    except psycopg2.Error as e:
        print(f'エラー内容：{e}')
        return [0, 0, 0, 0, '']
    except Exception as e:
        print(f'エラー内容：{e}')
        return [0, 0, 0, 0, '']
