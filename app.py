import os
from dotenv import load_dotenv
from flask import Flask, request, json
from flask_cors import CORS
from functools import wraps

from service.group_service import Group_Service
from service.user_service import User_Service

load_dotenv()

app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "http://localhost:4200"}})

database_url = os.getenv("DATABASE_URL")
api_key = os.getenv("API_KEY")

group_service = Group_Service(database_url, api_key)
user_service = User_Service(database_url, api_key)

def token_required(f):
  @wraps(f)
  def decorator(*args, **kwargs):
    token = None
    if 'Authorization' in request.headers:
      token = request.headers['Authorization']

    if not token:
      return {'message': 'a valid token is missing'}, 401
    try:
      data = user_service.decode_token(token)
      current_user = user_service.get_user_by_id(data['id'])
    except:
      return {'message': 'token is invalid'}, 401

    return f(*args, **kwargs)
  return decorator



@app.get("/")
def readyness():
  return "Send it"

@app.post("/user/create")
def create_user():
  user = request.get_json()
  return user_service.create(user)

@app.delete("/user/delete/<int:id>")
def delete_user(id):
  return user_service.delete(id)

@app.post("/user/authenticate")
def authenticate_user():
  user = request.get_json()
  return user_service.authenticate(user)

@app.get("/user/<string:id>")
def get_user_by_id(id):
  return user_service.get_user_by_id(id)

@app.get('/user')
def get_all_users():
  return user_service.get_all_users()



@app.post("/group/create")
@token_required
def create_group():
  data = request.get_json()
  name = data["name"]
  return group_service.create(name)

@app.delete("/group/delete/<int:id>")
@token_required
def delete_group(id):
  return group_service.delete(id)

@app.get("/group")
@token_required
def get_all_groups():
  return group_service.get_all_groups()

@app.get("/group/get-group-counts")
def get_group_counts():
  groups = group_service.get_group_counts()
  return json.dumps(groups)
