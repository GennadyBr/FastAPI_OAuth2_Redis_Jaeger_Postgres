import argparse
import psycopg2
from psycopg2 import Error
import uuid
import os
from dotenv import load_dotenv

load_dotenv()

# создаем флаги для ввода аргументов из консоли
parser = argparse.ArgumentParser(description="Example of a single flag acting as a boolean and an option.")
parser.add_argument('--name', default="admin", type=str)
parser.add_argument('--surname', default="admin", type=str)
parser.add_argument('--login', default="admin", type=str)
parser.add_argument('--email', type=str)
parser.add_argument('--password', type=str)
args = parser.parse_args()

try:
    # Подключиться к существующей базе данных
    with psycopg2.connect(user=os.environ['PG_DB_USER'],
                                  password=os.environ['PG_DB_PASSWORD'],
                                  host=os.environ['PG_DB_HOST'],
                                  port=os.environ['PG_DB_PORT'],
                                  database="postgres") as connection:

      cursor = connection.cursor()
      # добавление пользователя в таблицу user
      query = """ INSERT INTO users (uuid, name, surname, login, email, is_active, password) VALUES (%s,%s,%s,%s,%s,%s,%s)"""
      user_id = str(uuid.uuid4())
      params = (user_id, args.name, args.surname, args.login, args.email, True, args.password)
      cursor.execute(query, params)

      # получение ID super_user из базы role
      query = "select uuid from role where name='super_user'"
      cursor.execute(query)
      role_id = str(cursor.fetchone()[0])

      # добавление пользователя в таблицу user_role
      query = """ INSERT INTO user_role (uuid, user_id, role_id) VALUES (%s,%s,%s)"""
      params = (str(uuid.uuid4()), user_id, role_id)
      cursor.execute(query, params)

      connection.commit()

except (Exception, Error) as error:
    print("Ошибка при работе с PostgreSQL", error)
finally:
    if connection:
        cursor.close()
        connection.close()
