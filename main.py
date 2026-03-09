# Rules of a ReST API:
# 1. Data is transfered in key-value pairs (JSON) - Universal key value pair format.
#     Python we use convert JSON to a dictionary in JavaScript we can use JSON directly as a JSON object.
# 2. Define a URL or URI or Route
# 3. Define an HTTP method (GET, POST, PUT, DELETE)
# 4. Define a Status code (200, 201, 400, 404, 500)

from flask import Flask, request, jsonify
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from database import Base, User
from flask_cors import CORS


app = Flask(__name__)
CORS(app)


allowed_methods = ["GET", "POST", "PUT", "DELETE", "PATCH"]


DATABASE_URL = "postgresql+psycopg2://postgres:postgres@localhost:5433/flask_crash_api"

# Connecting SQLAlchemy to PostgreSQL database using create_engine
engine = create_engine(DATABASE_URL, echo=True)


# Create a session to call query methods
session = sessionmaker(bind=engine)
my_session = session()


# create tables automatically based on the defined classes in database.py
Base.metadata.create_all(engine)



@app.route("/", methods=allowed_methods)
def home():
    if request.method.upper() == "GET":
        msg = {"Flask API version": "1.0"}
        return jsonify(msg), 200
    else:
        return jsonify({"error": "Method not allowed"}), 405
    
    

@app.route("/users", methods=allowed_methods)
def users():
    if request.method.upper() == 'GET':
        #Return a list of users from table using SQLAlchemy
        query = select(User)
        users = my_session.scalars(query).all()
        data = []
        for user in users:
            data.append({
                "id": user.id,
                "name": user.name,
                "location": user.location
            })
        return jsonify({"data": data}), 200
    
    elif request.method.upper() == 'POST':
        #Convert JSON to Dictionary
        data = request.get_json()
        #Check if all fields are received
        if data["name"] == "" or data["location"] == "":
            return jsonify({"error": "Name and Location cannot be empty!"}), 400
        else:
            #Store user in users table using SQLAlchemy
            new_user = User(name=data["name"], location=data["location"])
            my_session.add(new_user)
            my_session.commit()
            return jsonify({"message": f"User created successfully! {data['name']} from {data['location']}"}), 201
        
    else:
        return jsonify({"error" : "Method Not Allowed!"}), 405
    

""" @app.route("/register", methods=allowed_methods)
def register():
    data = request.get_json

    if data["username"] == "" or data["email"] == "" or data["password"]:
            return jsonify({"error": "Fields cannot be empty!"}), 400
        else:
            #Store user in users table using SQLAlchemy
            new_user = User(username=data["username"], email=data["email"], password=data["password"])
            my_session.add(new_user)
            my_session.commit()
            return jsonify({"message": f"User created successfully! {data['username']} "}), 201 """







app.run(debug=True)