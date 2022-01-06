from os import environ

DATABASE_CONNECTION_URL = environ.get('DATABASE_CONNECTION_URL')

# DB_ECHO = bool(environ.get('DB_ECHO')) it always returning True
DB_ECHO = False
if environ.get('DB_ECHO') == "True":
    DB_ECHO = True
JWT_SECRET = environ.get('JWT_SECRET')

expiration_time = environ.get('JWT_EXPIRATION_TIME') if environ.get('JWT_EXPIRATION_TIME') != None else 24
JWT_EXPIRATION_TIME = float(expiration_time)

expiration_time_oauth = environ.get('JWT_EXPIRATION_TIME_OAUTH') if environ.get('JWT_EXPIRATION_TIME_OAUTH') != None else 0.167
JWT_EXPIRATION_TIME_OAUTH = float(expiration_time_oauth)

SECRET_KEY = environ.get('SECRET_KEY')

db_pool_recycle = environ.get('DATABASE_POOL_RECYCLE') if environ.get('DATABASE_POOL_RECYCLE') != None else 3000
DATABASE_POOL_RECYCLE = int(db_pool_recycle)

SERP_API_KEY = environ.get('SERP_API_KEY')