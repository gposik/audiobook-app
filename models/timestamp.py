from db import db
from datetime import datetime, timedelta
from sqlalchemy.sql import func
from sqlalchemy.ext.hybrid import hybrid_property


def tomorrows_date() -> "datetime":
    return datetime.utcnow() + timedelta(days=1)


class Timestamp(object):
    creation_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    modification_date = db.Column(
        db.DateTime, server_default=func.now(), onupdate=func.current_timestamp()
    )
    expiration_date = db.Column(db.DateTime, nullable=False, default=tomorrows_date)

    @hybrid_property
    def is_expired(self) -> bool:
        return datetime.utcnow() >= self.expiration_date
