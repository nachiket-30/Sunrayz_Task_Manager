import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root123",
    database="sunrayz_db"
)

print("Database Connected Successfully!")

conn.close()
