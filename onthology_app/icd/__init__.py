import pandas as pd
from collections import OrderedDict
from serpapi import GoogleSearch
from onthology_app import Serializer
from onthology_app.db import get_db
from onthology_app.status.messages import messages
from onthology_app.models.job import Job
import os
import json
import icd10
from datetime import datetime
from flask import current_app
import simple_icd_10 as icd
from threading import Thread
import uuid
import concurrent.futures
import atexit
from shutil import copyfile
import os
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import time
import smtplib, ssl,email


def allowed_file_types(filename):
    ALLOWED_EXTENSIONS = set(['csv'])
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def convert_df_to_json(df):
    code = df['Code'].unique().flat[0]
    description_list = df['Description'].to_list()
    return  {
        "code" : code,
        "description" : description_list
    }

def convert_desc_df_to_json(df):
    js = df.to_dict(orient='records')
    return  js

def get_job_status_by_id(id):
    db = get_db()
    return db.query(Job).filter_by(job_id=id).first()



def get_details_from_code(icdcode):
    inputicd = icdcode.replace('.', '').upper()
    local_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    train_data = pd.read_csv(local_path + "/static/ICD_Hier4_rev1_final.csv", encoding='unicode_escape')
    train_data['Code'] = train_data['Code'].str.replace('.', '')
    train_data['Code'] = train_data['Code'].str.strip()
    rslt_df = train_data[train_data['Code'] == inputicd]
    if rslt_df.empty:
        cd = icd10.find(inputicd)
        if cd is None:
            return {"error": messages["code-not-available"]}
        else:
            return {
                "code" : inputicd,
                "description" : cd.description
            }

    else:
        val = convert_df_to_json(rslt_df)
        return val

def get_details_from_description_with_key(description,api_key):
    ds = []
    dk = []
    ip = description
    params = {
        "engine": "google",
        "q": ip + " icd 10 data",
        "location": "United States",
        "hl": "en",
        "gl": "us",
        "google_domain": "google.com",
        "api_key": api_key,
        #"api_key": current_app.config['SERP_API_KEY'],
    }
    search = GoogleSearch(params)
    results = search.get_dict()
    if "organic_results" in results.keys():
        for result in results["organic_results"]:
            j = result['link']

            if (len(j.split('/')[-1]) <= 10) and not (j.split('/')[-1]).endswith('-') and not (
                    j.split('/')[-1]).endswith('html') and not (j.split('/')[-1]).endswith('htm') and not (
                    j.split('/')[-1]).endswith('pdf'):
                if icd.is_valid_item(j.split('/')[-1]) or icd10.exists(j.split('/')[-1]):
                    ds.append(j.split('/')[-1])
    if ds:
        for code in ds:
            if icd.is_valid_item(code):
                cd = icd.get_description(code)
                dk.append(cd)
            else:
                cd = icd10.find(code)
                dk.append(cd.description)
    df_single = pd.DataFrame(list(zip(ds, dk)), columns=['Perdicted_Code', 'Predicted_Description'])
    df_single['Perdicted_Code'] = df_single['Perdicted_Code'].astype(str).str.replace(".", "")
    val = convert_desc_df_to_json(df_single)
    return val

def process_data_in_csv_file(input_data,email_id,fname):


    api_key = current_app.config['SERP_API_KEY']
    try:
        db = get_db()
        job_id = str(uuid.uuid1()).replace('-','')
        Job.create_job(db, job_id, 'started', email_id)
        thread = Thread(target=process_data_after_response,args=(api_key,input_data,job_id,email_id,fname,))
        thread.start()

        #with concurrent.futures.ThreadPoolExecutor() as executor:
            #future = executor.submit(process_data_after_response,api_key,input_data,job_id)
            #return_value = future.result()
            #print("THis is from the main function")
            #print(return_value)

        return {'info':'success','audit_id':job_id}

    except:
        print("Caught exception")



def get_details_from_description(description):

    api_key = current_app.config['SERP_API_KEY']
    data = get_details_from_description_with_key(description,api_key)
    return data

def process_data_after_response(key,input_data,job_id,email_id,filename):

    local_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

    unwanted = ['-',',','(',')','[',']','/','@','<','~','%','\d+',"'",':','.']

    for i in unwanted:
        input_data['icd_description'] = input_data['icd_description'].str.replace(i, '')

    for ind, data in input_data.iterrows():
        icd_data = get_details_from_description_with_key(data['icd_description'],key)
        input_data.at[ind, 'Perdicted_Code'] = icd_data[0]['Perdicted_Code']
        input_data.at[ind, 'Predicted_Description'] = icd_data[0]['Predicted_Description']

    print("Final output data")
    print(input_data)

    #################################################################################################
    subject = "ICD10 prediction job completed"
    body = "Submitted ICD10 Job completed. Please find the attached output file."
    sender_email = "vsudhakar.clearsense@gmail.com"
    receiver_email = email_id
    password = "0Clearsense)"

    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject

    message.attach(MIMEText(body, "plain"))

    fname = os.path.splitext(filename)[0] + '_' + time.strftime("%Y%m%d_%H%M%S") + '.csv'

    input_data.to_csv(local_path + "/static/processed_files/" + fname)

    email_filename = local_path + "/static/processed_files/" + fname

    with open(email_filename, "rb") as attachment:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())

    encoders.encode_base64(part)

    part.add_header(
        "Content-Disposition",
        f"attachment; filename= {filename}",
    )

    message.attach(part)
    email_text = message.as_string()

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, email_text)

    #################################################################################################

    f = open(local_path + "/static/job_list.txt", "a")
    f.write(job_id+'\n')
    f.close()

def update_database():

    local_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

    if os.stat(local_path + "/static/job_list.txt").st_size != 0:
        db = get_db()
        copyfile(local_path + "/static/job_list.txt", local_path + "/static/job_list_temp.txt")
        #num_lines = sum(1 for line in open(local_path + "/static/job_list.txt"))
        #print("total no of lines")
        #print(num_lines)

        with open(local_path + "/static/job_list_temp.txt") as fp:
            lines = fp.readlines()

        line_without_newline = [item.replace('\n','') for item in lines]

        job_test = db.query(Job).filter(Job.job_id.in_(line_without_newline)).update({Job.status : 'succeeded' })


        db.commit()

        with open(local_path + "/static/job_list.txt","w") as fp:
            for line in line_without_newline:
                if line.strip("\n") != line:
                    fp.write(line)

        os.remove(local_path + "/static/job_list_temp.txt")

def init_icd(app):
    pass
