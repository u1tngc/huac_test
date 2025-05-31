#PGM-ID:GK1S01DB
#PGM-NAME:GK自家用DB操作

import psycopg2

# データベース接続情報を定数として定義
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


def insert_root_segment(data):
    try:
        conn = psycopg2.connect(**DB_CONFIG)  # 定数を展開して接続

        with conn.cursor() as cur:
            sql = 'INSERT INTO 学生管理セグ (学籍番号, 氏名, 状況CD, 解答状況CD, パスワード) VALUES (%s, %s, %s, %s, %s)'

            cur.execute(sql, data)
            conn.commit()

        conn.close()
        return 0  # 成功時のリターンコード

    except psycopg2.Error as e:
        return 1

    except Exception as e:
        return 2


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
        return []

    except Exception as e:
        return []
    

def get_mondai(bunya):
    try:
        conn = psycopg2.connect(**DB_CONFIG)  # 定数を展開して接続

        with conn.cursor() as cur:
            sql = f'SELECT * FROM "{bunya}問題セグ"'

            cur.execute(sql)
            result = cur.fetchall()  

        conn.close()

        return [list(row) for row in result]

    except psycopg2.Error as e:
        return []

    except Exception as e:
        return []


def get_gakusei(id,name):
    try:
        conn = psycopg2.connect(**DB_CONFIG)  # 定数を展開して接続

        with conn.cursor() as cur:
            if id:
                sql = 'SELECT 学籍番号, 氏名, 状況CD", 解答状況CD FROM 学生管理セグ WHERE 学籍番号 = %s'
                data = (id,)
            else:
                sql = 'SELECT 学籍番号, 氏名, 状況CD", 解答状況CD FROM 学生管理セグ WHERE 氏名 = %s'
                data = (name,)
            cur.execute(sql,data)
            result = cur.fetchone()  

        conn.close()
        return list(result)

    except psycopg2.Error as e:
        return []

    except Exception as e:
        return []
    

def update_gakusei(list):
    try:
        conn = psycopg2.connect(**DB_CONFIG)  # 定数を展開して接続

        with conn.cursor() as cur:
            sql = 'UPDATE 学生管理セグ SET 氏名 = %s, 状況CD = %s, 解答状況CD = %s WHERE 学籍番号 = %s'
            data = (list[1], list[2], list[3], list[0]) 

            cur.execute(sql, data)
            conn.commit()

        conn.close()

        return 0  # 成功時のリターンコード
    except psycopg2.Error as e:
        return 1
    except Exception as e:
        return 2
    

def get_gakuseiAll():
    try:
        conn = psycopg2.connect(**DB_CONFIG)  # 定数を展開して接続

        with conn.cursor() as cur:
            sql = 'SELECT * FROM "学生管理セグ"'

            cur.execute(sql)
            result = cur.fetchall()  

        conn.close()

        return [list(row) for row in result]

    except psycopg2.Error as e:
        return []

    except Exception as e:
        return []


def update_lastLogin(id):
    try:
        conn = psycopg2.connect(**DB_CONFIG)  # 定数を展開して接続

        with conn.cursor() as cur:
            sql = """
            UPDATE 学生管理セグ SET 最終ログイン日時 = CURRENT_TIMESTAMP AT TIME ZONE 'Asia/Tokyo' WHERE 学籍番号 = %s
            """
            data = (id,) 

            cur.execute(sql, data)
            conn.commit()

        conn.close()

        return 0  # 成功時のリターンコード
    except psycopg2.Error as e:
        return 1
    except Exception as e:
        return 2
    

def update_password(id,password):
    try:
        conn = psycopg2.connect(**DB_CONFIG)  # 定数を展開して接続

        with conn.cursor() as cur:
            sql = """
            UPDATE 学生管理セグ SET パスワード = %s WHERE 学籍番号 = %s
            """
            data = (password, id) 

            cur.execute(sql, data)
            conn.commit()

        conn.close()

        return 0  # 成功時のリターンコード
    except psycopg2.Error as e:
        return 1
    except Exception as e:
        return 2

"""
# 実行例
result = select_gakusei("16A3184")
print(len(result))
print(result)
"""
"""
data = ("N563029", "谷口雄一", 9, 2, "tani0206")
insert_root_segment()
"""