import argparse
import psycopg2
from psycopg2 import Error
import uuid
import os
# from dotenv import load_dotenv
import bcrypt
from core.config import user_db_settings

# load_dotenv()

if __name__ == '__main__':
    SUPER_USER = 'super_user'

    # создаем флаги для ввода аргументов из консоли
    parser = argparse.ArgumentParser(description="Creation super_user of user table and user_role")
    parser.add_argument('--name', default="admin", type=str, help="Put name of super_user, ex: admin")
    parser.add_argument('--surname', default="admin", type=str, help="Put surname of super_user, ex: admin")
    parser.add_argument('--login', default="admin", type=str, help="Put login of super_user, ex: admin")
    parser.add_argument('--email', type=str, help="Put login of super_user, ex: admin@gmail.com")
    parser.add_argument('--password', type=str, help="Put password of super_user")
    args = parser.parse_args()

    try:
        # Подключиться к существующей базе данных
        with psycopg2.connect(user=user_db_settings.user,
                                      password=user_db_settings.password.get_secret_value(),
                                      host=user_db_settings.service_name,
                                      port=user_db_settings.port,
                                      database=user_db_settings.name) as connection:

            cursor = connection.cursor()

            salt = bcrypt.gensalt()
            pwd_hash = bcrypt.hashpw(args.password.encode('utf-8'), salt)

            # добавление пользователя в таблицу user
            query = """ INSERT INTO users (uuid, name, surname, login, email, is_active, password) VALUES (%s,%s,%s,%s,%s,%s,%s)"""
            user_id = str(uuid.uuid4())
            params = (user_id, args.name, args.surname, args.login, args.email, True, pwd_hash)
            cursor.execute(query, params)

            # получение ID super_user из базы role
            query = f"""SELECT uuid FROM role WHERE name='{SUPER_USER}'"""
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
