from flask_restful import Api
from onthology_app.api.auth import Auth, AdminUsers
from onthology_app.models.user import User
from onthology_app.api.icd import CodeInfo,DescriptionInfo,DescriptionInfoFromCSV,UpdateJobDetails,IcdJobStatus
from flask import g, request


def init_api(app):
    api = Api(app)

    @app.before_request
    def before_request():
        g.user = None
        if "Authorization" in request.headers:
            auth_token = request.headers["Authorization"].split()
            if len(auth_token) > 1:
                user_info = User.check_auth_token(auth_token[1])
                if "error" not in user_info:
                    g.user = user_info

    api.add_resource(Auth, '/api/auth')

    api.add_resource(AdminUsers, '/api/users')

    api.add_resource(CodeInfo, '/api/icdcode/<string:icdcode>')

    api.add_resource(DescriptionInfo, '/api/icddesc/<string:description>')

    api.add_resource(DescriptionInfoFromCSV, '/api/icddescfiles')

    api.add_resource(UpdateJobDetails, '/api/updatejobstatus')

    api.add_resource(IcdJobStatus, '/api/jobstatus/<string:audit_id>')



    #api.add_resource(Onto, '/api/onto/<string:ontology>/<string:info>')

    #api.add_resource(OntoInfo, '/api/onto/info/<string:ontology>/<string:info_type>/<string:name>')

    #api.add_resource(OntoSparql, '/api/sparql/')

    #api.add_resource(OntoKnowledge, '/api/knowledge/')

    #api.add_resource(OntoInstance, '/api/onto/instance/<string:ontology>')
