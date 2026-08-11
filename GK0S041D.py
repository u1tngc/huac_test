#PGM-ID:GK0S041D
#PGM-NAME:GK各種CHK管理セグI/O(オンライン)
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


def insert_chkList(id, datakbn):
    try:
        conn = psycopg2.connect(**DB_CONFIG)  
        with conn.cursor() as cur:
            sql = "INSERT INTO 各種chk管理セグ (学籍番号, データ種類) VALUES (%s, %s)"
            data = (id, datakbn)
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
    

def get_chkListAll():
    try:
        conn = psycopg2.connect(**DB_CONFIG)  
        with conn.cursor() as cur:
            sql = '''
                SELECT 
                    c.学籍番号,
                    s.氏名,
                    c.データ種類,
                    c.法規,
                    c.気象,
                    c.工学,
                    c.情報,
                    c.学生chk,
                    c.教官chk
                FROM "各種chk管理セグ" c
                JOIN "学生管理セグ" s ON c.学籍番号 = s.学籍番号
                ORDER BY c.学籍番号, c.データ種類
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


def get_chkList(id):
    try:
        conn = psycopg2.connect(**DB_CONFIG)  
        with conn.cursor() as cur:
            sql = '''
                SELECT 
                    c.学籍番号,
                    s.氏名,
                    c.データ種類,
                    c.法規,
                    c.気象,
                    c.工学,
                    c.情報,
                    c.学生chk,
                    c.教官chk
                FROM "各種chk管理セグ" c
                JOIN "学生管理セグ" s ON c.学籍番号 = s.学籍番号
                WHERE c.学籍番号 = %s
                ORDER BY c.学籍番号, c.データ種類
            '''
            data = (id,)
            cur.execute(sql, data)
            result = cur.fetchall()  
        conn.close()
        return [list(row) for row in result]
    except psycopg2.Error as e:
        print(f'エラー内容：{e}')
        return []
    except Exception as e:
        print(f'エラー内容：{e}')
        return []
    

def update_chkList(update_chkList):
    print(update_chkList)
    try:
        conn = psycopg2.connect(**DB_CONFIG)  
        with conn.cursor() as cur:
            sql = '''
                UPDATE "各種chk管理セグ"
                SET 法規 = %s,
                    気象 = %s,
                    工学 = %s,
                    情報 = %s,
                    学生chk = %s,
                    教官chk = %s
                WHERE 学籍番号 = %s AND データ種類 = %s
            '''
            data = (
                update_chkList[2],
                update_chkList[3],
                update_chkList[4],
                update_chkList[5],
                update_chkList[6],
                update_chkList[7],
                update_chkList[0],
                update_chkList[1]
            )
            cur.execute(sql, data)
            conn.commit()
        return 0  
    except psycopg2.Error as e:
        print(f'エラー内容：{e}')
        return 1  
    except Exception as e:
        print(f'エラー内容：{e}')
        return 2   
    finally:
        if conn:
            conn.close()


def get_chk_info(gakuseki):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        with conn.cursor() as cur:
            sql = 'SELECT 法規, 気象, 工学, 情報, 学生chk, 教官chk FROM 各種chk管理セグ WHERE 学籍番号 = %s AND データ種類 = %s'
            data = (gakuseki, 2)
            cur.execute(sql, data)
            result = cur.fetchone()
        conn.close()
        return list(result) if result else ['', '', '', '', '', '']
    except psycopg2.Error as e:
        print(f'エラー内容：{e}')
        return ['', '', '', '', '', '']
    except Exception as e:
        print(f'エラー内容：{e}')
        return ['', '', '', '', '', '']
