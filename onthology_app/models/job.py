from sqlalchemy import  Integer, VARCHAR, Boolean,DateTime,Column, Sequence, text, Text
import datetime

from onthology_app.db import Base
from onthology_app import Serializer
from flask import current_app
from onthology_app.status.messages import messages
from sqlalchemy.orm import relationship


class Job(Base):
    __tablename__ = 'job'
    __table_args__ = {'schema': 'tform_db'}

    job_id = Column(VARCHAR(64), primary_key=True)
    status = Column(VARCHAR(64),  nullable=False)
    job_start_time = Column(DateTime, default=datetime.datetime.utcnow)
    job_end_time = Column(DateTime)
    email = Column(VARCHAR(64),  nullable=False)

    def create_job(db, job_id, status, email):
        job = Job(job_id=job_id, status=status, email=email)
        db.add(job)
        db.commit()
        return job

    def serialize(self):
        d = Serializer.serialize(self)
        del d['job_start_time']
        del d['job_end_time']
        return d

    @staticmethod
    def get_job_by_jobid(db, job_id):
        return db.query(job).filter_by(job_id=job_id).first()


    def update_job(db, job_id, job_end_time, status):
        job = db.query(job).filter_by(job_id=job_id).first()
        job.job_end_time = job_end_time
        job.status = status
        return job

