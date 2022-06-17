from database.db import db
from models.user import User as UserModel


class Billing(db.Model):
    __tablename__ = "billings"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, index=True)
    balance = db.Column(db.Float, nullable=False, default=100)
    billing_address = db.Column(db.String(255), nullable=False)
    flag = db.Column(db.Integer, nullable=False, default=0)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False, index=True
    )
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        server_default=db.func.now(),
        onupdate=db.func.now(),
    )
    auth_keys = db.relationship(
        "Key", backref="billing", lazy=True, cascade="all, delete"
    )

    def __init__(self, user_id, billing_address=None, balance=None, flag=None):
        self.user_id = user_id
        if billing_address is None:
            self.billing_address = UserModel.find_by(id=user_id).address
        else:
            self.billing_address = billing_address
        if balance is not None:
            self.balance = balance
        if flag is not None:
            self.flag = flag

    def json(self):
        return {
            "id": self.id,
            "balance": self.balance,
            "billing_address": self.billing_address,
            "flag": self.flag,
            "user_id": self.user_id,
            "created_at": str(self.created_at),
            "updated_at": str(self.updated_at),
        }

    @classmethod
    def find_by(cls, all=False, **kwargs) -> object or list:
        """
        Finds a user by the given parameters.
        :param all: If True, returns a list of all items matching the query.
        :param kwargs: The parameters to search for.
        :return: The user that matches the given parameters.
        """
        if all:
            return cls.query.filter_by(**kwargs).all()
        else:
            return cls.query.filter_by(**kwargs).first()

    @classmethod
    def find_all(cls):
        return cls.query.all()

    @classmethod
    def filtering(cls, offset, limit, **kwargs):
        if kwargs:
            if kwargs.get("updated_at"):
                billings = (
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
                billings = cls.query.offset(offset).limit(limit).all()
                count = cls.query.count()
            else:
                billings = (
                    cls.query.filter_by(**kwargs).offset(offset).limit(limit).all()
                )
                count = cls.query.filter_by(**kwargs).count()
        else:
            billings = []
            count = 0

        return billings, count

    def save_to_db(self):
        db.session.add(self)

    def delete_from_db(self):
        db.session.delete(self)

    def commit(self, to_return=False) -> object:
        """
        Commits the changes to the database.
        :param to_return: If True, returns the id of the object.
        :return: The id of the object or None.
        """

        db.session.commit()
        if to_return:
            db.session.refresh(self)
            return self.json()

    def rollback(self):
        db.session.rollback()
