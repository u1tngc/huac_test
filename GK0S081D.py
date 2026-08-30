#PGM-ID:GK0S081D
#PGM-NAME:GK学生状況DBI/O(オンライン)
#最終更新日:2026/08/29

import datetime
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

def get_rirekiAll(user_id):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        with conn.cursor() as cur:
            sql = '''
                SELECT 学籍番号, 管理区分, 管理番号, 枝番, 起票者, 開始年月日, 内容
                  FROM 会話履歴セグ
                 WHERE 学籍番号 = %s
                 ORDER BY 管理区分, 管理番号, 枝番
            '''
            data = (user_id,)
            cur.execute(sql, data)
            result = cur.fetchall()
        conn.close()
        return [list(row) for row in result] if result else []
    except psycopg2.Error as e:
        print(f'エラー内容：{e}')
        return []
    except Exception as e:
        print(f'エラー内容：{e}')
        return []

def get_kanriName():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        with conn.cursor() as cur:
            sql = '''
                SELECT * FROM 管理区分管理セグ
            '''
            cur.execute(sql,)
            result = cur.fetchall()
        conn.close()
        return [list(row) for row in result] if result else []
    except psycopg2.Error as e:
        print(f'エラー内容：{e}')
        return []
    except Exception as e:
        print(f'エラー内容：{e}')
        return []


def get_maxKanriNo(gakuseiID, kanriKbn):
    """指定学籍番号・管理区分の最大管理番号を返す
       戻り値：(rc, 管理番号)  rc 0=正常 1=DBエラー / 明細無しの場合は管理番号=None"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        with conn.cursor() as cur:
            sql = '''
                SELECT MAX(管理番号) FROM 会話履歴セグ
                 WHERE 学籍番号 = %s AND 管理区分 = %s
            '''
            data = (gakuseiID, kanriKbn)
            cur.execute(sql, data)
            result = cur.fetchone()
        conn.close()
        return 0, result[0] if result else None
    except psycopg2.Error as e:
        print(f'エラー内容：{e}')
        return 1, None
    except Exception as e:
        print(f'エラー内容：{e}')
        return 1, None


def get_maxEdaNo(gakuseiID, kanriKbn, kanriNo):
    """指定学籍番号・管理区分・管理番号の最大枝番を返す
       戻り値：(rc, 枝番)  rc 0=正常 1=DBエラー / 明細無しの場合は枝番=None"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        with conn.cursor() as cur:
            sql = '''
                SELECT MAX(枝番) FROM 会話履歴セグ
                 WHERE 学籍番号 = %s AND 管理区分 = %s AND 管理番号 = %s
            '''
            data = (gakuseiID, kanriKbn, kanriNo)
            cur.execute(sql, data)
            result = cur.fetchone()
        conn.close()
        return 0, result[0] if result else None
    except psycopg2.Error as e:
        print(f'エラー内容：{e}')
        return 1, None
    except Exception as e:
        print(f'エラー内容：{e}')
        return 1, None


def insert_rireki(gakuseiID, kanriKbn, kanriNo, edaNo, kihyosha, ymd, naiyo):
    """会話履歴セグへ1件登録する  戻り値：0=正常 1=DBエラー 2=その他エラー"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        with conn.cursor() as cur:
            sql = '''
                INSERT INTO 会話履歴セグ (学籍番号, 管理区分, 管理番号, 枝番, 起票者, 開始年月日, 内容)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            '''
            data = (gakuseiID, kanriKbn, kanriNo, edaNo, kihyosha, ymd, naiyo)
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


def get_rirekiByNo(gakuseiID, kanriKbn, kanriNo):
    """指定学籍番号・管理区分・管理番号の全枝番を枝番順で返す"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        with conn.cursor() as cur:
            sql = '''
                SELECT 学籍番号, 管理区分, 管理番号, 枝番, 起票者, 開始年月日, 内容
                  FROM 会話履歴セグ
                 WHERE 学籍番号 = %s AND 管理区分 = %s AND 管理番号 = %s
                 ORDER BY 枝番
            '''
            data = (gakuseiID, kanriKbn, kanriNo)
            cur.execute(sql, data)
            result = cur.fetchall()
        conn.close()
        return [list(row) for row in result] if result else []
    except psycopg2.Error as e:
        print(f'エラー内容：{e}')
        return []
    except Exception as e:
        print(f'エラー内容：{e}')
        return []
