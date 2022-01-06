import os
from flask import Flask, render_template
from sqlalchemy.inspection import inspect

class Serializer(object):

    def serialize(self):
        return {c: getattr(self, c) for c in inspect(self).attrs.keys()}

    #@staticmethod
    #def serialize_pandas(df):
        #return df.to_dict(orient='records')


    @staticmethod
    def serialize_list(l):
        return [m.serialize() for m in l]

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_mapping(
        SECRET_KEY='lswefkjnwefkjn24556jhnkv34534'
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('settings.py', silent=True)
        #['DATABASE_CONNECTION_URL'])
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    from onthology_app.db import init_app
    init_app(app)

    from onthology_app.api import init_api
    init_api(app)

    from onthology_app.icd import init_icd
    init_icd(app)


    return app