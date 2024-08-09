import mysql.connector
from decouple import config

DB = config("DB")
LOGIN = config("LOGIN")
PASSWORD = config("PASSWORD")
HOST = config("HOST")

def get_proxies() -> list[dict]:
    # connect
    conn = mysql.connector.connect(
        host=HOST,
        user=LOGIN,
        password=PASSWORD,
        database=DB
    )
    cursor = conn.cursor(dictionary=True)

    valid_proxies = []

    try:
        cursor.execute("SELECT * FROM valid_proxies")

        valid_proxies = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


    return valid_proxies


if __name__ == '__main__':
    print(get_proxies())
    print(type(get_proxies()))
