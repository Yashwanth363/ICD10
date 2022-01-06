from sqlalchemy import  Integer, VARCHAR, Boolean,DateTime,Column, Sequence, text, Text
import datetime

from onthology_app.db import Base
from onthology_app import Serializer
from flask import current_app
from onthology_app.status.messages import messages
from sqlalchemy.orm import relationship

import jwt

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
ph = PasswordHasher()

class User(Base,Serializer):
    __tablename__ = 'user'
    __table_args__ = {'schema': 'tform_db'}
    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    name = Column(VARCHAR(64))
    username = Column(VARCHAR(64), unique=True, nullable=False)
    password = Column(VARCHAR(255))
    email = Column(VARCHAR(64), unique=True, nullable=False)
    urole = Column(VARCHAR(80), default='basic')

    ######
    #requests
    #created_date
    #end_date
    #updated_date


    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.datetime.utcnow)

    @staticmethod
    def create_user(db, username, name, password, email):
        ph = PasswordHasher()
        hash = ph.hash(password)
        user = User(username=username, name=name, password=hash, email=email)
        db.add(user)
        db.commit()
        return user

    def get_urole(self):
        return self.urole

    def serialize(self):
        d = Serializer.serialize(self)
        del d['password']
        del d['created_at']
        del d['updated_at']
        return d

    @staticmethod
    def get_user_by_username(db, username):
        return db.query(User).filter_by(username=username).first()

    @staticmethod
    def get_user_by_email(db, email):
        return db.query(User).filter_by(email=email).first()

    @staticmethod
    def get_users(db):
        return db.query(User).all()

    @staticmethod
    def check_auth_token(auth_token):
        try:
            return jwt.decode(auth_token, current_app.config['JWT_SECRET'], algorithms='HS256')
        except jwt.exceptions.DecodeError:
            return {"error": messages["auth-token-invalid"]}
        except jwt.ExpiredSignatureError:
            # Signature has expired
            return {"error": messages["auth-token-expired"]}

    @staticmethod
    def authenticate(db, username, password):
        try:
            user = User.get_user_by_username(db, username)
            error = None
            if user is None:
                error = messages["login-invalid-username"]
            else:
                ph.verify(user.password, password)
        except VerifyMismatchError:
            error = messages["login-invalid-password"]
        # except:
        # error = messages["common-exception"] + str(sys.exc_info())

        if error is None:
            return user.auth_token()
        else:
            return {"error": error}

    def auth_token(self):
        expiration_time = datetime.datetime.utcnow() + datetime.timedelta(seconds=60 * 60 * current_app.config['JWT_EXPIRATION_TIME'])
        encoded_jwt = jwt.encode({'name': self.name,
                                  "email": self.email, "id": self.id, "exp": expiration_time, "role": self.urole},
                                 current_app.config['JWT_SECRET'], algorithm='HS256')
        token = str(encoded_jwt)
        info = self.check_auth_token(token)

        return {
            "data": {
                "user": {
                    "name": self.name,
                    "email": self.email,
                    "username": self.username,
                    "id": self.id,

                },
                "role": self.urole,
                "token": token,
                "exp": info["exp"]
            }
        }

