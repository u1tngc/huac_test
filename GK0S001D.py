#PGM-ID:GK0S001D
#PGM-NAME:GK学生管理セグI/O(オンライン)
#最終更新日:2026/06/24

import os

import psycopg2
import bcrypt

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

def insert_gakusei(id, name, status_cd, kanri_cd, shikaku_cd):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        with conn.cursor() as cur:
            sql = "INSERT INTO 学生管理セグ (学籍番号, 氏名, 権限, 出題区分, 資格, パスワード) VALUES (%s, %s, %s, %s, %s, %s)"
            data = (id, name, status_cd, kanri_cd, shikaku_cd, hash_password('245422kz'))
            cur.execute(sql, data)
            conn.commit()
        return 0
    except psycopg2.IntegrityError as e:
        print(f'エラー内容：{e}')
        return 3
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

def get_gakusei(id):
    try:
        conn = psycopg2.connect(**DB_CONFIG)  
        with conn.cursor() as cur:
            sql = 'SELECT 学籍番号, 氏名, 権限, 出題区分, 資格 FROM 学生管理セグ WHERE 学籍番号 = %s'
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

def update_gakusei(list):
    try:
        conn = psycopg2.connect(**DB_CONFIG)  
        with conn.cursor() as cur:
            sql = 'UPDATE 学生管理セグ SET 氏名 = %s, 権限 = %s, 出題区分 = %s,資格 = %s WHERE 学籍番号 = %s'
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

def update_password(id, password):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        with conn.cursor() as cur:
            sql = "UPDATE 学生管理セグ SET パスワード = %s WHERE 学籍番号 = %s"
            data = (hash_password(password), id)
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

def get_gakuseiInfo01():
    try:
        conn = psycopg2.connect(**DB_CONFIG)  
        with conn.cursor() as cur:
            sql = 'SELECT 学籍番号, 氏名 FROM "学生管理セグ" WHERE 出題区分 != 0'
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

def get_gakuseiInfo00(authority):
    try:
        conn = psycopg2.connect(**DB_CONFIG)  
        if authority == 9:
            with conn.cursor() as cur:
                sql = 'SELECT 学籍番号, 氏名 FROM "学生管理セグ"'
                cur.execute(sql)
                result = cur.fetchall()  
            conn.close()
        else:
            with conn.cursor() as cur:
                sql = 'SELECT 学籍番号, 氏名 FROM "学生管理セグ" WHERE 権限 != %s AND 権限 != %s'
                data = (7,9)
                cur.execute(sql,data)
                result = cur.fetchall()  
            conn.close()            
        return [list(row) for row in result]
    except psycopg2.Error as e:
        print(f'エラー内容：{e}')
        return ""
    except Exception as e:
        print(f'エラー内容：{e}')
        return ""

def get_gakuseiInfo02():
    try:
        conn = psycopg2.connect(**DB_CONFIG)  
        with conn.cursor() as cur:
            sql = 'SELECT 学籍番号, 氏名 FROM "学生管理セグ" WHERE 資格 != 2'
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

def get_renkyosei():
    try:
        conn = psycopg2.connect(**DB_CONFIG)  
        with conn.cursor() as cur:
            sql = 'SELECT 学籍番号, 氏名 FROM "学生管理セグ" WHERE 資格 = %s'
            data = (0,)
            cur.execute(sql,data)
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
    
def update_password1(id, password):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        with conn.cursor() as cur:
            sql = "UPDATE ユーザー管理セグ SET パスワード = %s WHERE ユーザーid = %s"
            data = (hash_password(password), id)
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

def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def get_gakkahan():
    try:
        conn = psycopg2.connect(**DB_CONFIG)  
        with conn.cursor() as cur:
            sql = 'SELECT 学籍番号, 氏名 FROM "学生管理セグ" WHERE 権限 IN (6, 7, 9)'
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