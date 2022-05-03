from typing import List
from db import db
from exceptions import APIError


class BaseModel(db.Model):
    __abstract__ = True
    __model_name__ = "base_model"

    id = db.Column(db.Integer, primary_key=True)

    @classmethod
    def find_by_id(cls, _id: int) -> "BaseModel":
        return cls.query.filter_by(id=_id).first()

    @classmethod
    def find_by_id_or_404(cls, _id: int) -> "BaseModel":
        obj = cls.query.filter_by(id=_id).first()
        if obj is None:
            raise APIError(
                status_code=404,
                title="The requested resource could not be found",
                messages={
                    cls.__model_name__: [
                        "Not found",
                    ]
                },
                data={
                    "{}_id".format(cls.__model_name__): id,
                },
                valid_data={},
            )
        return obj

    @classmethod
    def find_all(cls) -> List["BaseModel"]:
        return cls.query.all()

    def save_to_db(self) -> "None":
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self) -> "None":
        db.session.delete(self)
        db.session.commit()
