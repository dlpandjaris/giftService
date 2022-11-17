import psycopg2

CREATE_GROUPS_TABLE = ("""
    CREATE TABLE IF NOT EXISTS groups (id SERIAL PRIMARY KEY, name TEXT);
""")

class Group_Service:
    def __init__(self, url):
        self.connection = psycopg2.connect(url)
        with self.connection:
            with self.connection.cursor() as cursor:
                cursor.execute(CREATE_GROUPS_TABLE)

    def create(self, name):
        INSERT_GROUP_RETURN_ID = "INSERT INTO groups (name) VALUES (%s) RETURNING id;"
        
        with self.connection:
            with self.connection.cursor() as cursor:
                cursor.execute(CREATE_GROUPS_TABLE)
                cursor.execute(INSERT_GROUP_RETURN_ID, (name,))
                group_id = cursor.fetchone()[0]
        return {"id": group_id, "message": f"Group {name} created."}, 201

    def get_group_counts(self):
        SELECT_GROUP_COUNTS = ("""
            SELECT 
                groups.name AS group, 
                COUNT(*) AS user_count
            FROM users 
            INNER JOIN groups 
                ON groups.id = users.group_id
            GROUP BY groups.name;
        """)

        groups = []
        with self.connection:
            with self.connection.cursor() as cursor:
                cursor.execute(SELECT_GROUP_COUNTS)
                query = cursor.fetchall()
                for row in query:
                    group = {"group": row[0], "user_count": row[1]}
                    groups.append(group)
        return groups

    def delete(self, id):
        DELETE_GROUP = ("""
            DELETE FROM groups where id = %s
        """)

        with self.connection:
            with self.connection.cursor() as cursor:
                cursor.execute(CREATE_GROUPS_TABLE)
                cursor.execute(DELETE_GROUP, (id,))

        return {"message": f"Group {id} deleted."}, 204