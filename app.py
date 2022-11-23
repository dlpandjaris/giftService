import os
from dotenv import load_dotenv
from flask import Flask, request, json
from flask_cors import CORS

from functools import wraps
import uuid
import jwt
import datetime

from service.group_service import Group_Service
from service.user_service import User_Service

load_dotenv()

app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "http://localhost:4200"}})
url = os.getenv("DATABASE_URL")
api_key = os.getenv("API_KEY")

group_service = Group_Service(url)
user_service = User_Service(url)

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

@app.post("/group/create")
def create_group():
    data = request.get_json()
    name = data["name"]
    return group_service.create(name)

@app.delete("/group/delete/<int:id>")
def delete_group(id):
    return group_service.delete(id)

@app.get("/group/get-group-counts")
def get_group_counts():
    groups = group_service.get_group_counts()
    return json.dumps(groups)
