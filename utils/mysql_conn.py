import pymysql

def connect(ip, port, username, password, db):
    conn = pymysql.connect(
        host = ip,
        port = port,
        user = username,
        password = password,
        database = db,
        charset = 'utf8'
    )
    return conn

def fetch_data(conn, sql):
    cursor = conn.cursor()
    try:
        cursor.execute(sql)
        data = cursor.fetchall()
        return data
    except Exception as e:
        print(e)
        return []