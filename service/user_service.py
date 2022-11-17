import psycopg2

CREATE_USERS_TABLE = ("""
    CREATE TABLE IF NOT EXISTS users (id SERIAL PRIMARY KEY, group_id INTEGER, 
        first_name TEXT, last_name TEXT, email TEXT, password TEXT);
""")

class User_Service:
    def __init__(self, url):
        self.connection = psycopg2.connect(url)
        with self.connection:
            with self.connection.cursor() as cursor:
                cursor.execute(CREATE_USERS_TABLE)

    def create(self, group_id, first_name, last_name, email, password):
        INSERT_USER = ("""
            INSERT INTO users (group_id, first_name, last_name, email, password) 
            VALUES (%s, %s, %s, %s, %s) RETURNING id;
        """)

        SELECT_USER_COUNT_BY_EMAIL = ("""
            SELECT COUNT(*)
            FROM users
            WHERE email = %s;
        """)

        with self.connection:
            with self.connection.cursor() as cursor:
                cursor.execute(CREATE_USERS_TABLE)
                cursor.execute(SELECT_USER_COUNT_BY_EMAIL, (email,))
                existing_user_count = cursor.fetchone()[0]
                if existing_user_count > 0:
                    return {"message": f"User {email} already exists."}, 403
                cursor.execute(INSERT_USER, (group_id, first_name, last_name, email, password))
                user_id = cursor.fetchone()[0]
        return {"id": user_id, "message": f"User {email} added."}, 201
    
    def delete(self, id):
        DELETE_USER = ("""
            DELETE FROM users where id = %s
        """)

        with self.connection:
            with self.connection.cursor() as cursor:
                cursor.execute(CREATE_USERS_TABLE)
                cursor.execute(DELETE_USER, (id,))

        return {"message": f"User {id} deleted."}, 204