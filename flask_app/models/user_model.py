from flask_app.config.mysqlconnection import connectToMySQL
from flask import flash
# from flask_bcrypt import Bcrypt        
# bcrypt = Bcrypt(app)     # we are creating an object called bcrypt, 
#                          # which is made by invoking the function Bcrypt with our app as an argument
# Attributions:
# email Regex: https://uibakery.io/regex-library/email-regex-python
# pw Regexes: 
# Attribution: https://stackoverflow.com/questions/46582497/python-regex-for-password-validation
# Attribution: https://www.geeksforgeeks.org/password-validation-in-python/
# 

from flask_app import DB
TABLE = "users"

import re
ALPHAONLY = re.compile(r"^[a-zA-Z]+$")
ALPHANUMERIC = re.compile(r"^[a-zA-Z0-9]+$")
ISVALIDEMAIL = re.compile(r"^\S+@\S+\.\S+$")
# ISVALIDPASSWORD = re.compile(r"^(?=.*[\d])(?=.*[a-z])(?=.*[A-Z])[A-Za-z\d]{8,20}$")

class User:
    def __init__(self, data):
        self.id = int(data['id'])       # what's passing in a non-int?
        self.first_name = data['first_name']
        self.last_name = data['last_name']
        self.fullname = self.first_name + " " + self.last_name
        self.password  = data['password']
        self.email = data['email']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
    def __repr__(self):
        return f'id:{self.id}, fn: {self.first_name}, ln: {self.last_name}, full: {self.fullname}, em: {self.email}, pw: {self.password}'

# CRUD
# Create
    @classmethod
    def save(cls, data):
        query = f"""
            INSERT INTO {TABLE} (first_name,last_name, password, email) 
            VALUES (%(first_name)s,%(last_name)s,%(password)s,%(email)s)
            """

        return connectToMySQL(DB).query_db(query , data)

# Read
# Read by id
    @classmethod
    def get_by_id(cls, data):
        query = f"SELECT * FROM {TABLE} WHERE id = %(id)s;"
        row = connectToMySQL(DB).query_db(query, data)

        if not row:
            return False
        
        return cls(row[0])

    # Used for logging in
    @classmethod
    def get_by_email(cls, data):
        query = f"SELECT * FROM {TABLE} WHERE email = %(email)s;"
        results = connectToMySQL(DB).query_db(query, data)
 
        if not results or len(results) == 0 :
            return None
        
        user = results[0]
        return cls(user)

# Read all
    @classmethod
    def get_all(cls, data):
        query = f"""SELECT * FROM {TABLE} WHERE id != %(id)s ORDER BY first_name 
        """
        results = connectToMySQL(DB).query_db(query, data)
        # print('d=',data,'q=', query, 'r=', results)

        if not results or len(results) == 0:
            return False

        list_of_instances = []
        for row in results:
            data = {
                **row
            }
            instance = cls(data)
            list_of_instances.append(instance)

        return list_of_instances

# ----------------------   Validations   ----------------------
    @staticmethod
    def validate_registration(data):
        already_registered_user = User.get_by_email({'email' : data['email']})
        is_valid = True

        # --------------  First Name  --------------  data
        if len( data["first_name"] ) < 1:
            flash("First name required", "first_name")
            is_valid = False
        elif len( data["first_name"] ) < 3:
            flash("First name must be at least 3 characters", "first_name")
            is_valid = False
        elif not ALPHAONLY.match(data['first_name']):
            flash("Name can only contain letters from the alphabet", "first_name")
            is_valid = False

        # --------------  Last Name  --------------  
        if len( data["last_name"] ) < 1:
            flash("Last name required", "last_name")
            is_valid = False
        elif len( data["last_name"] ) < 3:
            flash("Last name must be at least 3 characters", "last_name")
            is_valid = False
        elif not ALPHAONLY.match(data['last_name']):
            flash("Name can only contain letters from the alphabet", "last_name")
            is_valid = False

        # --------------  Email  --------------  
        if len( data['email'] ) < 1:
            flash("Email required", "email")
            is_valid = False
        # --------------  Email in valid format  --------------  
        elif not ISVALIDEMAIL.match(data['email']):
            flash("Invalid email address", "email")
            is_valid = False
        # --------------  Email not previously registered  --------------  
        else:
            is_conflicted = User.get_by_email({'email' : data['email']})
            if is_conflicted:
                flash("Invalid email address: Address already registered.", "email")
                is_valid = False

        # --------------  Password lengths  --------------  
        if len( data["password"] ) < 1:
            flash("Password required", "password")
            is_valid = False
        elif len( data['password'] ) < 8:
            flash("Password must be at least 8 characters", "password")
            is_valid = False
        elif len( data['password'] ) > 20:
            flash("Password must not exceed 20 characters", "password")
            is_valid = False

        # --------------  Password === Confirmed PW --------------  
        if data['password'] != data['confirm_pass']:
            flash("Passwords must be identical", "password")
            # flash("Passwords must be identical", "confirm_pass") # Desired IFF providing error feedback paired to the specific input?
            is_valid = False

        # # --------------  Ninja Bonus: Password  --------------  
        # if not ISVALIDPASSWORD.match(data['password']):
        #     flash("Password requires at least one lowercase & uppercase letter & a digit", "password")
        #     is_valid = False


        return is_valid

