from functools import wraps
import sys
from flask import request
from onthology_app.db import get_db

from flask_restful import Resource, reqparse, fields, marshal_with
from onthology_app.models.user import User
from onthology_app.status.messages import messages
import json
from flask import g

parser = reqparse.RequestParser()
# default location is flask.Request.values and flask.Request.json
# check help text careful it must be string
parser.add_argument("username", required=True, help=messages["auth-username-help"]["message"])
parser.add_argument("password", required=True, help=messages["auth-password-help"]["message"])


class Auth(Resource):

    # @marshal_with(resource_fields)
    def get(self):
        try:
            auth_token = request.headers["Authorization"].split()
            return User.check_auth_token(auth_token[1])
        except KeyError:
            return {"error": messages["no-auth-token"]}

    def post(self):
        args = parser.parse_args()
        return User.authenticate(get_db(), args["username"], args["password"])

    # required for preflight requests for browser based apps
    def options(self):
        return ["GET", "POST"]


class AdminUsers(Resource):

    def get(self):
        try:
            auth_token = request.headers["Authorization"].split()
            info = User.check_auth_token(auth_token[1])
            if "error" in info:
                return info
            if "email" in info:
                # get the role of the user
                user = User.get_user_by_email(get_db(), info["email"])
                role = user.get_urole()
                if role == "admin":
                    users = User.get_users(get_db())
                    return {
                        "users": User.serialize_list(users)
                    }
            return {"error": "Access Denied"}
        except KeyError:
            return {"error": messages["no-auth-token"]}

    # required for preflight requests for browser based apps
    def options(self):
        return ["GET"]


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user is None:
            return {"error": "Access Denied"}
        return f(*args, **kwargs)

    return decorated_function