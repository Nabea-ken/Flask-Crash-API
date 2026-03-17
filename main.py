# Rules of a ReST API:
# 1. Data is transfered in key-value pairs (JSON) - Universal key value pair format.
#     Python we use convert JSON to a dictionary in JavaScript we can use JSON directly as a JSON object.
# 2. Define a URL or URI or Route
# 3. Define an HTTP method (GET, POST, PUT, DELETE)
# 4. Define a Status code (200, 201, 400, 404, 500)

from flask import Flask, request, jsonify
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from database import Base, User, Authentication
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

# Drop all tables


# Casa
@app.route("/", methods=allowed_methods)
def home():
    if request.method.upper() == "GET":
        msg = {"Flask API version": "1.0"}
        return jsonify(msg), 200
    else:
        return jsonify({"error": "Method not allowed"}), 405
    
    
# A route to handle GET and POST requests for users.
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
                "location": user.location,
                "age": user.age
            })
        return jsonify({"data": data}), 200
    
    elif request.method.upper() == 'POST':
        #Convert JSON to Dictionary
        data = request.get_json()
        #Check if all fields are received
        if data["name"] == "" or data["location"] == "" or data["age"] == "":
            return jsonify({"error": "Name, Location, and Age cannot be empty!"}), 400
        else:
            #Store user in users table using SQLAlchemy
            new_user = User(name=data["name"], location=data["location"], age=data["age"])
            my_session.add(new_user)
            my_session.commit()
            return jsonify({"message": f"User created successfully! {data['name']} from {data['location']}"}), 201
        
    else:
        return jsonify({"error" : "Method Not Allowed!"}), 405
    

# Register route to create a new user in the user_authentication table with full_name, email, and password fields. 
# Check if email already exists before creating a new user. Return appropriate status codes and messages for success and error cases.
@app.route("/register", methods=allowed_methods)
def register():
    try:
        data = request.get_json()

        #debug
        print("Incoming:", data)  

        if not data:
            return jsonify({"error": "No data received"}), 400

        full_name = data.get("full_name")
        email = data.get("email")
        password = data.get("password")

        if not full_name or not email or not password:
            return jsonify({"error": "Full Name, Email, and Password cannot be empty!"}), 400
        

        existing_user = my_session.query(Authentication).filter_by(email=data["email"]).first()

        if existing_user:
            return jsonify({"error": "Email already registered"}), 409

        new_user = Authentication(
            full_name=full_name,
            email=email,
            password=password
        )

        my_session.add(new_user)
        my_session.commit()

        return jsonify({"message": f"User created successfully! {full_name}"}), 201

        

    except Exception as e:
        print("ERROR:", str(e)) 
        return jsonify({"error": "Server error"}), 500


# Login route to authenticate users based on email and password stored in the user_authentication table
@app.route("/login", methods=allowed_methods)
def login():
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "No data received"}), 400

        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return jsonify({"error": "Email and Password cannot be empty!"}), 400

        query = select(Authentication).where(Authentication.email == email)
        user = my_session.scalars(query).first()

        if user is None:
            return jsonify({"error": "User not found!"}), 404

        if user.password == password:
            return jsonify({"message": f"Login successful! Welcome {user.full_name}"}), 200
        else:
            return jsonify({"error": "Incorrect password!"}), 401

    except Exception as e:
        print("ERROR:", str(e))
        return jsonify({"error": "Server error"}), 500
    

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