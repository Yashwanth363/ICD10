from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

from sqlalchemy.exc import IntegrityError
from psycopg2 import OperationalError
import click
from flask import current_app, g
from flask.cli import with_appcontext

from onthology_app.models.user import User
from onthology_app.models.job import Job

def get_db():
    if 'db' not in g:
        engine = create_engine(current_app.config['DATABASE_CONNECTION_URL'],pool_recycle=current_app.config['DATABASE_POOL_RECYCLE'],echo=current_app.config['DB_ECHO'])

        Session = sessionmaker(bind=engine)
        session = Session()
        g.db = session

    return g.db

def create_default_users():
    db = get_db()
    User.create_user(db,"admin","Admin","admin@123","admin@test.in")
    User.create_user(db,"user","User","user@123","user@test.in")

def init_db():
    engine = create_engine(current_app.config['DATABASE_CONNECTION_URL'],pool_recycle=current_app.config['DATABASE_POOL_RECYCLE'],echo=current_app.config['DB_ECHO'])
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

@click.command('create-default-users')
@with_appcontext
def create_default_users_command():
    """Creates default users"""
    create_default_users()
    click.echo('Created default users')

@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clears the existing data and creates new tables."""
    init_db()
    click.echo('Initialized the database.')

def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

def init_app(app):
    # cleaning up after returning the response
    app.teardown_appcontext(close_db)
    # adds a command to flask command
    app.cli.add_command(init_db_command)
    app.cli.add_command(create_default_users_command)