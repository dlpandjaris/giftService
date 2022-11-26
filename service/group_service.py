import psycopg2
from psycopg2.extras import RealDictCursor
from flask import jsonify
import uuid

CREATE_GROUPS_TABLE = ("""
  CREATE TABLE IF NOT EXISTS groups (id TEXT, name TEXT);
""")

GET_GROUP_BY_ID = ("""
  SELECT * FROM groups WHERE id = %s
""")

class Group_Service:
  def __init__(self, database_url, api_key):
    self.connection = psycopg2.connect(database_url)
    with self.connection:
      with self.connection.cursor() as cursor:
        cursor.execute(CREATE_GROUPS_TABLE)

  def create(self, group):
    INSERT_GROUP_RETURN_ID = "INSERT INTO groups (id, name) VALUES (%s, %s) RETURNING id;"
    
    try:
      group_id = str(uuid.uuid4())
      name = group['name']
    except KeyError:
      return {'message': "Must include group name."}, 400

    with self.connection:
      with self.connection.cursor() as cursor:
        cursor.execute(CREATE_GROUPS_TABLE)
        cursor.execute(INSERT_GROUP_RETURN_ID, (group_id, name))
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
      with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute(CREATE_GROUPS_TABLE)
        cursor.execute(GET_ALL_GROUPS)
        groups = cursor.fetchall()
        return jsonify(groups), 201

  def get_group_by_id(self, group_id):
    with self.connection:
      with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute(CREATE_GROUPS_TABLE)
        cursor.execute(GET_GROUP_BY_ID, (group_id,))
        group = cursor.fetchone()
        return group

  def update_group(self, group):
    UPDATE_GROUP = ("""
      UPDATE groups
      SET name = %s
      WHERE id = %s
      RETURNING name;
    """)

    try:
      group_id = group['id']
      name = group['name']
    except KeyError:
      return {"message": "Bad request."}, 400

    with self.connection:
      with self.connection.cursor() as cursor:
        cursor.execute(GET_GROUP_BY_ID, (group_id,))
        exists = cursor.fetchone()
        if exists:
          cursor.execute(UPDATE_GROUP, (name, group_id))
          name = cursor.fetchone()[0]
          return {"message": f"Group {name} updated."}, 200
        else:
          return {"message": "Group not found."}, 400

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