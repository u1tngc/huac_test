#PGM-ID:GK0S001D
#PGM-NAME:GK学生管理セグI/O(オンライン)
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

def insert_gakusei(id, name, status_cd,kanri_cd):
    try:
        conn = psycopg2.connect(**DB_CONFIG)  
        with conn.cursor() as cur:
            sql = "INSERT INTO 学生管理セグ (学籍番号, 氏名, 状況CD, 出題区分, 解答状況CD, パスワード) VALUES (%s, %s, %s, %s, %s, %s)"
            data = (id, name, status_cd, kanri_cd, 0, '245422kz')
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


def select_gakusei(id):
    try:
        conn = psycopg2.connect(**DB_CONFIG)  # 定数を展開して接続
        with conn.cursor() as cur:
            sql = 'SELECT * FROM "学生管理セグ" WHERE "学籍番号" = %s'
            data = (id,)  
            cur.execute(sql, data)
            result = cur.fetchone()  
        conn.close()
        return list(result) if result else []
    except psycopg2.Error as e:
        print(f'エラー内容：{e}')
        return []
    except Exception as e:
        print(f'エラー内容：{e}')
        return []


def get_gakusei(id,name):
    try:
        conn = psycopg2.connect(**DB_CONFIG)  
        with conn.cursor() as cur:
            if id:
                sql = 'SELECT 学籍番号, 氏名, 状況CD, 出題区分, 解答状況CD FROM 学生管理セグ WHERE 学籍番号 = %s'
                data = (id,)
            else:
                sql = 'SELECT 学籍番号, 氏名, 状況CD, 出題区分, 解答状況CD FROM 学生管理セグ WHERE 氏名 = %s'
                data = (name,)
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
    

def update_gakusei(list):
    try:
        conn = psycopg2.connect(**DB_CONFIG)  
        with conn.cursor() as cur:
            sql = 'UPDATE 学生管理セグ SET 氏名 = %s, 状況CD = %s, 出題区分 = %s,解答状況CD = %s WHERE 学籍番号 = %s'
            data = (list[1], list[2], list[3], list[4], list[0]) 
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
    

def get_gakuseiAll():
    try:
        conn = psycopg2.connect(**DB_CONFIG)  
        with conn.cursor() as cur:
            sql = 'SELECT * FROM "学生管理セグ"'
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


def update_lastLogin(id):
    try:
        conn = psycopg2.connect(**DB_CONFIG) 
        with conn.cursor() as cur:
            sql = """
            UPDATE 学生管理セグ SET 最終ログイン日時 = CURRENT_TIMESTAMP AT TIME ZONE 'Asia/Tokyo' WHERE 学籍番号 = %s
            """
            data = (id,) 
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
    

def update_password(id,password):
    try:
        conn = psycopg2.connect(**DB_CONFIG)  
        with conn.cursor() as cur:
            sql = """
            UPDATE 学生管理セグ SET パスワード = %s WHERE 学籍番号 = %s
            """
            data = (password, id) 
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
    

def update_kaitoJyokyoCD(user_id):
    try:
        conn = psycopg2.connect(**DB_CONFIG)  
        with conn.cursor() as cur:
            sql = 'UPDATE 学生管理セグ SET 解答状況CD = 0 WHERE 学籍番号 = %s'
            data = (user_id,) 
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
    

def get_gakuseiInfo():
    try:
        conn = psycopg2.connect(**DB_CONFIG)  
        with conn.cursor() as cur:
            sql = 'SELECT 学籍番号, 氏名 FROM "学生管理セグ" WHERE 出題区分 = 0'
            cur.execute(sql)
            result = cur.fetchall()  
        conn.close()
        return [list(row) for row in result]
    except psycopg2.Error as e:
        print(f'エラー内容：{e}')
        return ""
    except Exception as e:
        print(f'エラー内容：{e}')
        return ""
    

def get_gakuseiName(id):
    try:
        conn = psycopg2.connect(**DB_CONFIG)  
        with conn.cursor() as cur:
            sql = 'SELECT 氏名 FROM "学生管理セグ" WHERE 学籍番号 = %s'
            data = (id,)
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