#PGM-ID:GK0S061D
#PGM-NAME:GK養成計画管理セグI/O(オンライン)
#最終更新日:2026/01/27

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

# DB_CONFIG = {
#     "dbname": "huac_gakka", 
#     "user": "taniguchi_tanglin_ic", 
#     "password": "N6eEqr20vmfNV-_McGwfkA", 
#     "host": "huac-tngc-6767.jxf.gcp-asia-southeast1.cockroachlabs.cloud", 
#     "port": 26257,
#     "sslmode": "require",
#     "sslcert": "",
#     "sslkey": "",
#     "sslrootcert": "",
#     "target_session_attrs": "read-write"
# }


def get_keikaku_all():
    """養成計画管理セグの全データを取得"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        with conn.cursor() as cur:
            sql = 'SELECT 学籍番号, チーム, 養成分野, 養成予定年月, 担当者 FROM 養成計画管理セグ ORDER BY チーム, 養成分野, 養成予定年月'
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


def get_team_list():
    """チーム一覧を取得"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        with conn.cursor() as cur:
            sql = 'SELECT DISTINCT チーム FROM 養成計画管理セグ ORDER BY チーム'
            cur.execute(sql)
            result = cur.fetchall()
        conn.close()
        return [row[0] for row in result]
    except psycopg2.Error as e:
        print(f'エラー内容：{e}')
        return []
    except Exception as e:
        print(f'エラー内容：{e}')
        return []


def get_team_members(team):
    """指定チームの学生一覧を取得"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        with conn.cursor() as cur:
            sql = 'SELECT DISTINCT 学籍番号 FROM 養成計画管理セグ WHERE チーム = %s'
            data = (team,)
            cur.execute(sql, data)
            result = cur.fetchall()
        conn.close()
        return [row[0] for row in result]
    except psycopg2.Error as e:
        print(f'エラー内容：{e}')
        return []
    except Exception as e:
        print(f'エラー内容：{e}')
        return []


def get_team_bunnya_info(team, bunnya):
    """チーム・分野ごとの情報（担当者、予定年月）を取得"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        with conn.cursor() as cur:
            sql = '''
                SELECT DISTINCT 担当者, MIN(養成予定年月) as 開始月, MAX(養成予定年月) as 終了月
                FROM 養成計画管理セグ 
                WHERE チーム = %s AND 養成分野 = %s AND 担当者 != ''
                GROUP BY 担当者
            '''
            data = (team, bunnya)
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


def get_team_schedule(team):
    """チームのスケジュール情報を取得（分野ごとの開始・終了月）"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        with conn.cursor() as cur:
            sql = '''
                SELECT 養成分野, MIN(養成予定年月) as 開始月, MAX(養成予定年月) as 終了月
                FROM 養成計画管理セグ 
                WHERE チーム = %s
                GROUP BY 養成分野
                ORDER BY MIN(養成予定年月)
            '''
            data = (team,)
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


def get_tantousha_by_team_bunnya(team, bunnya):
    """チーム・分野の担当者一覧を取得"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        with conn.cursor() as cur:
            sql = '''
                SELECT DISTINCT 担当者 
                FROM 養成計画管理セグ 
                WHERE チーム = %s AND 養成分野 = %s AND 担当者 != ''
            '''
            data = (team, bunnya)
            cur.execute(sql, data)
            result = cur.fetchall()
        conn.close()
        return [row[0] for row in result]
    except psycopg2.Error as e:
        print(f'エラー内容：{e}')
        return []
    except Exception as e:
        print(f'エラー内容：{e}')
        return []
    

def get_gantt_base_data():
    """ガントチャート用の基本データを一括取得"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        with conn.cursor() as cur:
            sql = """
                SELECT 
                    チーム,
                    学籍番号,
                    養成分野,
                    養成予定年月,
                    担当者
                FROM 養成計画管理セグ
                ORDER BY チーム, 養成分野, 養成予定年月
            """
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