#PGM-ID:GK0S051D
#PGM-NAME:GK養成状況管理セグI/O(オンライン)
#最終更新日:2025/12/21

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

def get_yoseiJokyo(id):
    try:
        conn = psycopg2.connect(**DB_CONFIG)  
        with conn.cursor() as cur:
            sql = "SELECT * FROM 養成状況管理セグ WHERE 学籍番号 = %s"
            data = (id,)
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
    
def get_yoseiJokyoSum(id):
    try:
        conn = psycopg2.connect(**DB_CONFIG)  
        with conn.cursor() as cur:
            sql = """
                SELECT 
                    k.分野,
                    ROUND(COUNT(CASE WHEN y.養成日 <> '' THEN 1 END) * 100.0 / NULLIF(COUNT(*), 0)) AS 割合
                FROM 養成状況管理セグ y
                JOIN 養成項目管理セグ k ON y.養成cd = k.養成cd
                WHERE y.学籍番号 = %s
                GROUP BY k.分野
            """
            data = (id,)
            cur.execute(sql, data)
            rows = cur.fetchall()
        conn.close()
        
        分野リスト = ['法規', '工学', '気象', '情報', '衛生', '六項目']
        分野マップ = {分野: 0 for 分野 in 分野リスト}
        for row in rows:
            if row[0] in 分野マップ:
                分野マップ[row[0]] = int(row[1]) if row[1] is not None else 0
        
        return [分野マップ[分野] for 分野 in 分野リスト]
    except psycopg2.Error as e:
        print(f'エラー内容：{e}')
        return ""
    except Exception as e:
        print(f'エラー内容：{e}')
        return ""


def get_yoseiSumAll():
    try:
        conn = psycopg2.connect(**DB_CONFIG)  
        with conn.cursor() as cur:
            sql = """
                SELECT 
                    g.氏名,
                    k.分野,
                    ROUND(COUNT(CASE WHEN y.養成日 <> '' THEN 1 END) * 100.0 / NULLIF(COUNT(*), 0)) AS 割合
                FROM 養成状況管理セグ y
                JOIN 養成項目管理セグ k ON y.養成cd = k.養成cd
                JOIN 学生管理セグ g ON y.学籍番号 = g.学籍番号
                GROUP BY y.学籍番号, g.氏名, k.分野
                ORDER BY y.学籍番号
            """
            cur.execute(sql)
            rows = cur.fetchall()
        conn.close()
        return [list(row) for row in rows]
    except psycopg2.Error as e:
        print(f'エラー内容：{e}')
        return ""
    except Exception as e:
        print(f'エラー内容：{e}')
        return ""