from db import db
from datetime import datetime, timedelta


def tomorrows_date():
    return datetime.utcnow() + timedelta(days=1)


class Timestamp(object):
    creation_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    expiration_date = db.Column(db.DateTime, nullable=False, default=tomorrows_date)
    finish_date = db.Column(db.DateTime)
