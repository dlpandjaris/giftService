import os
from dotenv import load_dotenv
from flask import Flask, request, json
from werkzeug.security import generate_password_hash,check_password_hash

from functools import wraps
import uuid
import jwt
import datetime

from service.group_service import Group_Service
from service.user_service import User_Service

load_dotenv()

app = Flask(__name__)
url = os.getenv("DATABASE_URL")
api_key = os.getenv("API_KEY")

group_service = Group_Service(url)
user_service = User_Service(url)

def readyness():
    return "Send it"

@app.post("/user/create")
def create_user():
    data = request.get_json()
    group_id = data["group_id"]
    first_name = data["first_name"]
    last_name = data["last_name"]
    email = data["email"]
    password = data["password"]
    return user_service.create(group_id, first_name, last_name, email, password)

@app.delete("/user/delete/<int:id>")
def delete_user(id):
    return user_service.delete(id)

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
