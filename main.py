# Rules of a ReST API:
# 1. Data is transfered in key-value pairs (JSON) - Universal key value pair format.
#     Python we use convert JSON to a dictionary in JavaScript we can use JSON directly as a JSON object.
# 2. Define a URL or URI or Route
# 3. Define an HTTP method (GET, POST, PUT, DELETE)
# 4. Define a Status code (200, 201, 400, 404, 500)

import sentry_sdk
from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
from flask_bcrypt import Bcrypt
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from database import Base, Employee, Authentication
from flask_cors import CORS

app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = "ajkgaijeroannnv"

CORS(app)

sentry_sdk.init(
    dsn="https://04b6c7d9310f40f382043999b7073f58@o4511094688579584.ingest.de.sentry.io/4511094767288400",
    # Add data like request headers and IP for users,
    # see https://docs.sentry.io/platforms/python/data-management/data-collected/ for more info
    send_default_pii=True,
)

jwt = JWTManager(app)

bcrypt = Bcrypt(app)

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
      
# A route to handle GET and POST requests for employees.
@app.route("/employees", methods=allowed_methods)
@jwt_required()
def employees():
    try:
        if request.method.upper() == 'GET':
            #Return a list of employees from table using SQLAlchemy
            employee_list = []
            query = select(Employee)
            my_employee = list(my_session.scalars(query).all())
            
            for employee in my_employee:
                employee_list.append({
                    "id": employee.id,
                    "name": employee.name,
                    "location": employee.location,
                    "age": employee.age
                })
            return jsonify({"data": employee_list}), 200
        
        elif request.method.upper() == 'POST':
            #Convert JSON to Dictionary
            data = request.get_json()
            #Check if all fields are received
            if data["name"] == "" or data["location"] == "" or data["age"] == "":
                return jsonify({"error": "Name, Location, and Age cannot be empty!"}), 400
            else:
                #Store employee in employees table using SQLAlchemy
                new_employee = Employee(name=data["name"], location=data["location"], age=data["age"])
                my_session.add(new_employee)
                my_session.commit()
                my_session.close()
                
                return jsonify({"message": f"Employee created successfully! {data['name']} from {data['location']}"}), 201
            
        else:
            return jsonify({"error" : "Method Not Allowed!"}), 405

    except Exception as e:
        print("ERROR:", str(e))
        return jsonify({"error": "Server error"}), 500
    
# Register route to create a new user in the user_authentication table with full_name, email, and password fields. 
# Check if email already exists before creating a new user. Return appropriate status codes and messages for success and error cases.
@app.route("/register", methods=allowed_methods)
def register():
    try:
        if request.method.upper() == 'POST':
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

            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

            new_user = Authentication(
                full_name=full_name,
                email=email,
                password=hashed_password
            )

            my_session.add(new_user)
            my_session.commit()

            # Generate a unique token using the user email
            token = create_access_token(identity=data["email"])

            return jsonify({"message": f"User created successfully! {full_name}", "token": token}), 201

    except Exception as e:
        print("ERROR:", str(e)) 
        return jsonify({"error": "Server error"}), 500

# Login route to authenticate users based on email and password stored in the user_authentication table
@app.route("/login", methods=allowed_methods)
def login():
    try:
        if request.method.upper() == 'POST':
            data = request.get_json()

            if not data:
                return jsonify({"error": "No data received"}), 400

            email = data.get("email")
            password = data.get("password")

            if not email or not password:
                return jsonify({"error": "Email and Password cannot be empty!"}), 400

            query = select(Authentication).where(Authentication.email == email)
            auth = my_session.scalars(query).first()
            print("Queried User:---------------", auth)

            #check if user exists BEFORE checking password
            if not auth:
                return jsonify({"error": "User not found!"}), 404

            check_password = bcrypt.check_password_hash(auth.password, password)

            if not check_password:
                return jsonify({"error": "Incorrect password!"}), 401

            token = create_access_token(identity=auth.email)

            return jsonify({
                "message": f"Login successful! Welcome {auth.full_name}",
                "token": token
            }), 200

    except Exception as e:
        print("ERROR:", str(e))
        return jsonify({"error": "Server error"}), 500
   


app.run(debug=True)