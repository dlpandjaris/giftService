import re
import psycopg2
from psycopg2.extras import RealDictCursor
from werkzeug.security import generate_password_hash,check_password_hash
from flask import jsonify

import uuid
import jwt
import datetime

CREATE_USERS_TABLE = ("""
  CREATE TABLE IF NOT EXISTS users (id TEXT, first_name TEXT, 
  last_name TEXT, email TEXT, password TEXT, token TEXT, role TEXT);
""")

class User_Service:
  def __init__(self, database_url, api_key):
    self.connection = psycopg2.connect(database_url)
    self.api_key = api_key
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
      INSERT INTO users (id, first_name, last_name, email, password, role) 
      VALUES (%s, %s, %s, %s, %s, 'user') RETURNING id;
    """)

    try:
      user_id = str(uuid.uuid4())
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
        cursor.execute(INSERT_USER, (user_id, first_name, last_name, email, password_hash))
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
      SELECT first_name, last_name, role, password FROM users
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
          record = cursor.fetchone()
          full_name = f'{record[0]} {record[1]}'
          role = record[2]
          password_hash = record[3]
        except TypeError:
          return {"message": f"Email not found."}, 400
        if check_password_hash(password_hash, password):
          token = jwt.encode({'name' : full_name, 'role': role,  'exp' : datetime.datetime.utcnow() + datetime.timedelta(hours=1)}, self.api_key, "HS256")
          return {"token": token, "message": f"Login Success!"}, 201
        else:
          return {"message": f"Password incorrect."}, 404
  
  def get_all_users(self):
    GET_ALL_USERS = "SELECT * FROM users;"

    with self.connection:
      with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute(CREATE_USERS_TABLE)
        cursor.execute(GET_ALL_USERS)
        users = cursor.fetchall()
        return jsonify(users), 201

  def get_user_by_id(self, user_id):
    GET_USER_BY_ID = ("""
      SELECT * FROM users
      WHERE id = %s;
    """)

    with self.connection:
      with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute(CREATE_USERS_TABLE)
        cursor.execute(GET_USER_BY_ID, (user_id,))
        user = cursor.fetchone()
        if user:
          print(user)
          return jsonify(user)
        else:
          return {"message": "User not found"}, 400

  def decode_token(self, token):
    return jwt.decode(token, self.api_key, algorithms=["HS256"])

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