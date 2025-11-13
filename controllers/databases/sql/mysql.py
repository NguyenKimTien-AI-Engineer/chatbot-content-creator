import mysql.connector
from contextlib import contextmanager

from configs import constant


def connect_mysql():
    try:
        return mysql.connector.connect(
            host=constant.MYSQL_DB_HOST,
            user=constant.MYSQL_DB_USER,
            password=constant.MYSQL_DB_PASSWORD,
            database=constant.MYSQL_DB_NAME,
            autocommit=True
        )
    except mysql.connector.Error as err:
        print(f"\n[LOG SYSTEM]\nLỗi kết nối MySQL: {err}")
        return None


@contextmanager
def get_cursor():
    connection = connect_mysql()

    if connection is None:
        raise ConnectionError("Không thể kết nối đến MySQL.")
    cursor = connection.cursor(dictionary=True)
    try:
        yield cursor
    except mysql.connector.Error as err:
        print(f"\n[LOG SYSTEM]\nLỗi MySQL: {err}")
        connection.rollback()
        raise
    else:
        connection.commit()
    finally:
        cursor.close()
        connection.close()