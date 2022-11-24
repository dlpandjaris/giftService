import psycopg2
from flask import jsonify

CREATE_GROUPS_TABLE = ("""
  CREATE TABLE IF NOT EXISTS groups (id SERIAL PRIMARY KEY, name TEXT);
""")

class Group_Service:
  def __init__(self, database_url, api_key):
    self.connection = psycopg2.connect(database_url)
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

  def delete(self, id):
    DELETE_GROUP = ("""
      DELETE FROM groups where id = %s
    """)

    with self.connection:
      with self.connection.cursor() as cursor:
        cursor.execute(CREATE_GROUPS_TABLE)
        cursor.execute(DELETE_GROUP, (id,))

    return {"message": f"Group {id} deleted."}, 204

  def get_all_groups(self):
    GET_ALL_GROUPS = "SELECT * FROM groups;"

    with self.connection:
      with self.connection.cursor() as cursor:
        cursor.execute(CREATE_GROUPS_TABLE)
        cursor.execute(GET_ALL_GROUPS)
        groups = cursor.fetchall()
    return jsonify(groups), 201

  def get_group_counts(self):
    # SELECT_GROUP_COUNTS = ("""
    #   SELECT 
    #     groups.name AS group, 
    #     COUNT(*) AS user_count
    #   FROM users 
    #   INNER JOIN groups 
    #     ON groups.id = users.group_id
    #   GROUP BY groups.name;
    # """)

    # groups = []
    # with self.connection:
    #   with self.connection.cursor() as cursor:
    #     cursor.execute(SELECT_GROUP_COUNTS)
    #     query = cursor.fetchall()
    #     for row in query:
    #       group = {"group": row[0], "user_count": row[1]}
    #       groups.append(group)
    # return groups
    pass