#PGM-ID:GK0S082D
#PGM-NAME:GKタスク管理セグI/O(オンライン)
#最終更新日:2026/09/04

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

def get_task01(user_id):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        with conn.cursor() as cur:
            if user_id:
                sql = "SELECT * FROM タスク管理セグ WHERE 担当 = %s"
                data = (user_id,)
                cur.execute(sql, data)
            else:
                sql = "SELECT * FROM タスク管理セグ"
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

def get_task02(ymd):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        with conn.cursor() as cur:
            sql = '''
                SELECT * FROM タスク管理セグ
                WHERE (進捗 <> 100 AND タスクid <= %s)
                OR タスクid > %s
                ORDER BY 管理区分, タスクid, 枝番
            '''
            #WHERE句のプレースホルダが2個のため同じ値を2つ渡す
            data = (ymd, ymd)
            cur.execute(sql,data)                
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


def get_maxTaskId(kanriKbn):
    """指定管理区分の最大タスクidを返す（進捗・年度で絞り込まない全件対象）
       戻り値：(rc, タスクid)  rc 0=正常 1=DBエラー / 明細無しの場合はタスクid=None"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        with conn.cursor() as cur:
            sql = '''
                SELECT MAX(タスクid) FROM タスク管理セグ
                 WHERE 管理区分 = %s
            '''
            data = (kanriKbn,)
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


def get_maxEdaNo02(kanriKbn, taskId):
    """指定管理区分・タスクidの最大枝番を返す
       戻り値：(rc, 枝番)  rc 0=正常 1=DBエラー / 明細無しの場合は枝番=None"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        with conn.cursor() as cur:
            sql = '''
                SELECT MAX(枝番) FROM タスク管理セグ
                 WHERE 管理区分 = %s AND タスクid = %s
            '''
            data = (kanriKbn, taskId)
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


def insert_task(kanriKbn, taskId, edaNo, naiyo, tanto, iraimoto, kigen, memo, shinchoku):
    """タスク管理セグへ1件登録する  戻り値：0=正常 1=DBエラー 2=その他エラー"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        with conn.cursor() as cur:
            sql = '''
                INSERT INTO タスク管理セグ (管理区分, タスクid, 枝番, タスク内容, 担当, 依頼元, 期限, メモ, 進捗)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            '''
            data = (kanriKbn, taskId, edaNo, naiyo, tanto, iraimoto, kigen, memo, shinchoku)
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


def update_task(kanriKbn, taskId, edaNo, naiyo, tanto, kigen, memo, shinchoku):
    """タスク管理セグを1件訂正する（依頼元は訂正対象外）
       戻り値：0=正常 1=DBエラー 2=その他エラー"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        with conn.cursor() as cur:
            sql = '''
                UPDATE タスク管理セグ
                   SET タスク内容 = %s, 担当 = %s, 期限 = %s, メモ = %s, 進捗 = %s
                 WHERE 管理区分 = %s AND タスクid = %s AND 枝番 = %s
            '''
            data = (naiyo, tanto, kigen, memo, shinchoku, kanriKbn, taskId, edaNo)
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


def delete_task(delList):
    """タスク管理セグを一括削除する
       delListは [管理区分, タスクid, 枝番, ...] の二次配列
       1件でも失敗した場合はコミットせず全て取り消す
       戻り値：0=正常 1=DBエラー 2=その他エラー"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        with conn.cursor() as cur:
            sql = '''
                DELETE FROM タスク管理セグ
                 WHERE 管理区分 = %s AND タスクid = %s AND 枝番 = %s
            '''
            for ix1 in range(len(delList)):
                data = (delList[ix1][0], delList[ix1][1], delList[ix1][2])
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
