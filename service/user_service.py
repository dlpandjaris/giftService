import re
import psycopg2
from werkzeug.security import generate_password_hash,check_password_hash

CREATE_USERS_TABLE = ("""
    CREATE TABLE IF NOT EXISTS users (id SERIAL PRIMARY KEY, 
        first_name TEXT, last_name TEXT, email TEXT, password TEXT);
""")

class User_Service:
    def __init__(self, url):
        self.connection = psycopg2.connect(url)
        with self.connection:
            with self.connection.cursor() as cursor:
                cursor.execute(CREATE_USERS_TABLE)

    def create(self, user):
        SELECT_USER_COUNT_BY_EMAIL = ("""
            SELECT COUNT(*)
            FROM users
            WHERE email = %s;
        """)

        INSERT_USER = ("""
            INSERT INTO users (first_name, last_name, email, password) 
            VALUES (%s, %s, %s, %s) RETURNING id;
        """)

        print(user)
        try:
            first_name = user['first_name']
            last_name = user['last_name']
            email = user['email']
            password = user['password']
        except KeyError:
            return {"message": "Bad request."}, 400

        weaknesses = self.check_password_strength(password)
        if weaknesses != '':
            return {"message": weaknesses}, 400

        password_hash = generate_password_hash(password, method='sha256')

        with self.connection:
            with self.connection.cursor() as cursor:
                cursor.execute(CREATE_USERS_TABLE)
                cursor.execute(SELECT_USER_COUNT_BY_EMAIL, (email,))
                existing_user_count = cursor.fetchone()[0]
                if existing_user_count > 0:
                    return {"message": f"User {email} already exists."}, 403
                cursor.execute(INSERT_USER, (first_name, last_name, email, password_hash))
                user_id = cursor.fetchone()[0]
        return {"id": user_id, "message": f"User {email} added."}, 201
    
    def delete(self, id):
        DELETE_USER = ("""
            DELETE FROM users where id = %s;
        """)

        with self.connection:
            with self.connection.cursor() as cursor:
                cursor.execute(CREATE_USERS_TABLE)
                cursor.execute(DELETE_USER, (id,))

        return {"message": f"User {id} deleted."}, 204

    def authenticate(self, user):
        AUTHENTICATE_USER = ("""
            SELECT password FROM users
            WHERE email = %s
        """)

        try: 
            email = user["email"]
            password = user['password']
        except KeyError:
            return {"message": "Bad request."}, 400
        with self.connection:
            with self.connection.cursor() as cursor:
                cursor.execute(CREATE_USERS_TABLE)
                cursor.execute(AUTHENTICATE_USER, (email,))
                try: 
                    password_hash = cursor.fetchone()[0]
                except TypeError:
                    return {"message": f"Email not found."}, 400
                if not password_hash:
                    print(password_hash)
                if check_password_hash(password_hash, password):
                    return {"message": f"Login Success!"}, 201
                else:
                    return {"message": f"Password incorrect."}, 404

    @staticmethod
    def check_password_strength(password):
        message = ''
        if len(password) < 8:
            message += 'Password needs at least 8 characters\n'
        if len(re.findall('[a-z]', password)) == 0:
            message += 'Password needs at least 1 lowercase letter\n'
        if len(re.findall('[A-Z]', password)) == 0:
            message += 'Password needs at least 1 uppercase letter\n'
        if len(re.findall('[0-9]', password)) == 0:
            message += 'Password needs at least 1 number\n'
        return message