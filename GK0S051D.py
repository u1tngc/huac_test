#PGM-ID:GK0S051D
#PGM-NAME:GK養成状況管理セグI/O(オンライン)
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
    
def get_yoseiAllData():
    """全学生の養成状況データを取得"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)  
        with conn.cursor() as cur:
            # 養成項目一覧を取得
            sql_items = """
                SELECT 養成cd, 分野, 養成名 
                FROM 養成項目管理セグ 
                ORDER BY 養成cd
            """
            cur.execute(sql_items)
            items = cur.fetchall()
            
            # 学生一覧を取得（資格=0の練許生のみ）
            sql_students = """
                SELECT 学籍番号, 氏名 
                FROM 学生管理セグ 
                WHERE 資格 = 0
                ORDER BY 学籍番号
            """
            cur.execute(sql_students)
            students = cur.fetchall()
            
            # 全養成状況データを取得
            sql_status = """
                SELECT 学籍番号, 養成cd, 養成日 
                FROM 養成状況管理セグ
            """
            cur.execute(sql_status)
            statuses = cur.fetchall()
            
            # 各学生の進捗率を取得
            sql_progress = """
                SELECT 
                    y.学籍番号,
                    k.分野,
                    ROUND(COUNT(CASE WHEN y.養成日 <> '' THEN 1 END) * 100.0 / NULLIF(COUNT(*), 0)) AS 割合
                FROM 養成状況管理セグ y
                JOIN 養成項目管理セグ k ON y.養成cd = k.養成cd
                JOIN 学生管理セグ g ON y.学籍番号 = g.学籍番号
                WHERE g.資格 = 0
                GROUP BY y.学籍番号, k.分野
            """
            cur.execute(sql_progress)
            progress = cur.fetchall()
            
        conn.close()
        return {
            'items': [list(row) for row in items],
            'students': [list(row) for row in students],
            'statuses': [list(row) for row in statuses],
            'progress': [list(row) for row in progress]
        }
    except psycopg2.Error as e:
        print(f'エラー内容:{e}')
        return None
    except Exception as e:
        print(f'エラー内容:{e}')
        return None

def get_yoseiDate(id,code):
    try:
        conn = psycopg2.connect(**DB_CONFIG)  
        with conn.cursor() as cur:
            sql = "SELECT 養成日 FROM 養成状況管理セグ WHERE 学籍番号 = %s AND 養成cd = %s"
            data = (id,code,)
            cur.execute(sql,data)
            result = cur.fetchone()  
        conn.close()
        return result[0] if result else ""
    except psycopg2.Error as e:
        print(f'エラー内容：{e}')
        return []
    except Exception as e:
        print(f'エラー内容：{e}')
        return []

def update_yoseiJokyo(yoseiKamoku,id,yoseidate):
    try:
        conn = psycopg2.connect(**DB_CONFIG)  
        with conn.cursor() as cur:
            if yoseidate == "":
                sql = 'UPDATE 養成状況管理セグ SET 養成日 = %s, 状況 = 0 WHERE 養成cd = %s AND 学籍番号 = %s'
            else:
                sql = 'UPDATE 養成状況管理セグ SET 養成日 = %s, 状況 = 1 WHERE 養成cd = %s AND 学籍番号 = %s'
            data = (yoseidate, yoseiKamoku, id) 
            cur.execute(sql, data)
            conn.commit()
        conn.close()
        return ""  
    except psycopg2.Error as e:
        print(f'エラー内容：{e}')
        return "養成状況の更新に失敗しました。"
    except Exception as e:
        print(f'エラー内容：{e}')
        return "養成状況の更新に失敗しました。"
    
def get_yoreiRate(yoseiKamoku, id):
    try:
        conn = psycopg2.connect(**DB_CONFIG)  
        with conn.cursor() as cur:
            sql = """
                SELECT 
                ROUND(COUNT(CASE WHEN y.状況 = 1 THEN 1 END) * 100.0 / NULLIF(COUNT(*), 0)) AS 割合
                FROM 養成項目管理セグ k
                LEFT JOIN 養成状況管理セグ y ON k.養成cd = y.養成cd AND y.学籍番号 = %s
                WHERE k.分野 = %s
            """
            data = (id, yoseiKamoku,)
            cur.execute(sql, data)
            result = cur.fetchone()  
        conn.close()
        print(result)
        return int(result[0]) if result and result[0] is not None else 0
    except psycopg2.Error as e:
        print(f'エラー内容：{e}')
        return 0
    except Exception as e:
        print(f'エラー内容：{e}')
        return 0
    

def get_yoseiDateAll():
    """全学生の養成状況を一括取得（ガントチャート用）"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        with conn.cursor() as cur:
            sql = """
                SELECT 学籍番号, 養成cd, 養成日 
                FROM 養成状況管理セグ 
                WHERE 養成日 != ''
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