import pymysql

# 连接到MySQL服务器
conn = pymysql.connect(
    host='localhost',
    port=3306,
    user='admin',
    password='admin'
)

try:
    # 创建数据库
    cursor = conn.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS hex_auth CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
    print("Database created successfully!")
finally:
    conn.close()