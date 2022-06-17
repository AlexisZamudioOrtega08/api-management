from database.db import db
from typing import Tuple, Optional
from models.billing import Billing as BillingModel


class Key(db.Model):
    __tablename__ = "auth_keys"
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True, index=True)
    key = db.Column(db.String(80), unique=True, nullable=False, index=True)
    billing_id = db.Column(
        db.Integer(), db.ForeignKey("billings.id"), nullable=False, index=True
    )
    is_active = db.Column(db.Boolean(), nullable=False, server_default="1")
    created_at = db.Column(db.DateTime(), nullable=False, server_default=db.func.now())
    updated_at = db.Column(
        db.DateTime(),
        nullable=False,
        server_default=db.func.now(),
        onupdate=db.func.now(),
    )

    def __init__(self, key, user_id):
        self.key = key
        self.billing_id = BillingModel.find_by(user_id=user_id)
        if self.billing_id is None:
            raise Exception("A billing was not found for the given user.")
        else:
            self.billing_id = self.billing_id.id

    def json(self):
        return {
            "id": self.id,
            "key": self.key,
            "billing_id": self.billing_id,
            "is_active": self.is_active,
            "created_at": str(self.created_at),
            "updated_at": str(self.updated_at),
        }

    @classmethod
    def find_by(cls, all=False, **kwargs) -> list:
        """
        Find a key by the given parameters.
        :param all: If True, return all keys.
        :param kwargs: The parameters to search for.
        :return: The key(s) found.
        """
        if all:
            return cls.query.filter_by(**kwargs).all()
        else:
            return cls.query.filter_by(**kwargs).first()

    @classmethod
    def find_all(cls):
        return cls.query.all()

    @classmethod
    def filtering(cls, offset: int, limit: int, **kwargs) -> Tuple[list, int]:
        """
        Filter the users by the given parameters.
        :param offset: The offset to start the query.
        :param limit: The limit of the query.
        :param kwargs: The parameters to search for.
        :return: The users found and the total number of users.
        """
        if kwargs:
            if kwargs.get("updated_at"):
                keys = (
                    cls.query.filter(
                        cls.updated_at.like(kwargs.get("updated_at") + "%")
                    )
                    .offset(offset)
                    .limit(limit)
                    .all()
                )
                count = cls.query.filter(
                    cls.updated_at.like(kwargs.get("updated_at") + "%")
                ).count()
            elif kwargs.get("all"):
                keys = cls.query.offset(offset).limit(limit).all()
                count = cls.query.count()
            else:
                keys = cls.query.filter_by(**kwargs).offset(offset).limit(limit).all()
                count = cls.query.filter_by(**kwargs).count()
        else:
            keys = []
            count = 0
        return keys, count

    def save_to_db(self):
        db.session.add(self)

    def delete_from_db(self):
        db.session.delete(self)

    def deactivate(self):
        self.is_active = False
        self.save_to_db()

    def activate(self):
        self.is_active = True

    def commit(self, to_return=False) -> int:
        """
        Commit the changes to the database.
        :return: The id of the object if required.
        """
        db.session.commit()
        if to_return:
            db.session.refresh(self)
            return self.id

    def rollback(self):
        db.session.rollback()
