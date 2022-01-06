import pandas as pd
from collections import OrderedDict
from serpapi import GoogleSearch
from flask import request,Response
import spacy
import werkzeug
import os
from werkzeug.utils import secure_filename
import time
import uuid

from onthology_app.api.auth import login_required
from flask_restful import Resource, reqparse, fields, marshal_with
from onthology_app.icd import get_details_from_code,get_details_from_description,process_data_in_csv_file,allowed_file_types,update_database,get_job_status_by_id
from onthology_app.models.user import User
from onthology_app.models.job import Job
from onthology_app.status.messages import messages
from onthology_app import Serializer
from flask import g
import sys

parser = reqparse.RequestParser()
# default location is flask.Request.values and flask.Request.json
# check help text careful it must be string
parser.add_argument("file", required=True, type=werkzeug.datastructures.FileStorage, location = 'files', help=messages["no-file-help"]["message"])
parser.add_argument("emailid", required=True, help=messages["no-email-help"]["message"])


class CodeInfo(Resource):

    def post(self,icdcode):
        try:
            auth_token = request.headers["Authorization"].split()
            info = User.check_auth_token(auth_token[1])
            if "error" in info:
                return info
            if "email" in info:
                icddata = get_details_from_code(icdcode)
                return icddata
            return {"error": "Access Denied"}
        except KeyError:
            return {"error": messages["no-auth-token"]}



class DescriptionInfo(Resource):

    def get(self,description):
        try:
            auth_token = request.headers["Authorization"].split()
            info = User.check_auth_token(auth_token[1])
            if "error" in info:
                return info
            if "email" in info:
                icddata = get_details_from_description(description)
                return icddata
            return {"error": "Access Denied"}
        except KeyError:
            return {"error": messages["no-auth-token"]}


class DescriptionInfoFromCSV(Resource):

    def post(self):
        try:
            auth_token = request.headers["Authorization"].split()
            info = User.check_auth_token(auth_token[1])
            if "error" in info:
                return info
            if "email" in info:
                args = parser.parse_args()

                csv_file = args['file']
                email_id = args['emailid']

                print("EMAIL ID")
                print(email_id)
                print(type(email_id))

                if csv_file.filename == '':
                    return {"error": messages["no-file"]}

                if not allowed_file_types(csv_file.filename):
                    return {"error": messages["only-csv-file-allowed"]}

                if email_id == '':
                    return {"error": messages["no-email-help"]}

                local_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
                original_filename = secure_filename(csv_file.filename)
                fname = os.path.splitext(original_filename)[0] + '_' + time.strftime("%Y%m%d_%H%M%S") + '.csv'
                csv_file.save(local_path + "/static/uploaded_files/" +fname)
                input_data = pd.read_csv(local_path + "/static/uploaded_files/" + fname )
                input_data.columns = map(str.lower, input_data.columns)



                if 'icd_description' in input_data:

                    icd_data = process_data_in_csv_file(input_data,email_id,original_filename)
                    return icd_data
                else:
                    return {"error": messages["column-not-available"]}

        except KeyError:
            return {"error": messages["no-auth-token"]}


class UpdateJobDetails(Resource):

    def post(self):
        print("wow")
        return update_database()


class IcdJobStatus(Resource,Serializer):


    def get(self,audit_id):
        data = get_job_status_by_id(audit_id)

        print("data")
        print(data)
        return Job.serialize(data)

