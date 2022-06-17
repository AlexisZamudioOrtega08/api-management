import random
from typing import Tuple, Optional
from database.db import db
from werkzeug.security import check_password_hash, generate_password_hash


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, index=True)
    first_name = db.Column(db.String(80), nullable=False, index=True)
    last_name = db.Column(db.String(80), nullable=False, index=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password = db.Column(db.String(120), nullable=False, index=True)
    email = db.Column(db.String(80), unique=True, nullable=False, index=True)
    verified = db.Column(db.Boolean, default=False, nullable=False)
    address = db.Column(db.String(80), nullable=False)
    role = db.Column(db.Integer, nullable=False, index=True, default="1")
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        server_default=db.func.now(),
        onupdate=db.func.now(),
    )
    billings = db.relationship(
        "Billing", backref="user", lazy=True, cascade="all, delete"
    )
    # logs = db.relationship('Log', backref='user', lazy=True)

    def __init__(
        self,
        first_name,
        last_name,
        username,
        password,
        address,
        email,
        role: Optional[str] = None,
    ):
        self.first_name = first_name
        self.last_name = last_name
        self.username = username
        self.password = self.crate_hash(password)
        self.email = email
        self.address = address
        self.role = role

    def json(self):
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "username": self.username,
            "email": self.email,
            "password": self.password,
            "verified": self.verified,
            "address": self.address,
            "role": self.role,
            "created_at": str(self.created_at),
            "updated_at": str(self.updated_at),
        }

    def identity(self):
        return {
            "id": self.id,
            "username": self.username,
            "verified": self.verified,
            "role": self.role,
        }

    @classmethod
    def check_password(cls, hashed_password: str, password: str) -> bool:
        """
        Check if the password is correct.
        :param hashed_password: The hashed password.
        :param password: The password to check.
        :return: True if the password is correct, False otherwise.
        """
        return check_password_hash(hashed_password, password)

    @classmethod
    def crate_hash(cls, password: str) -> str:
        """
        Create a hash of the password.
        :param password: The password to hash.
        :return: The hashed password.
        """
        hash = generate_password_hash(password, method="pbkdf2:sha256", salt_length=16)
        return hash

    @classmethod
    def find_by(cls, all: bool = False, **kwargs) -> object:
        """
        Find a user by the given parameters.
        :param all: If True, return all users.
        :param kwargs: The parameters to search for.
        :return: The user(s) found.
        """
        if all:
            return cls.query.filter_by(**kwargs).all()
        else:
            return cls.query.filter_by(**kwargs).first()

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
                users = (
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
                users = cls.query.offset(offset).limit(limit).all()
                count = cls.query.count()
            else:
                users = cls.query.filter_by(**kwargs).offset(offset).limit(limit).all()
                count = cls.query.filter_by(**kwargs).count()
        else:
            users = []
            count = 0
        return users, count

    @classmethod
    def find_all(cls):
        return cls.query.all()

    @classmethod
    def create_otp(cls, email: str) -> str:
        """
        Create a one-time password.
        :param email: The email of the user.
        :return: The one-time password.
        """
        otp = random.randint(100000, 999999)
        return otp

    def save_to_db(self):
        db.session.add(self)

    def delete_from_db(self):
        db.session.delete(self)

    def commit(self, id: bool = False) -> int:
        """
        Commit the changes to the database.
        :return: The id of the object if required.
        """
        db.session.commit()
        if id:
            db.session.refresh(self)
            return self.id

    def rollback(self):
        db.session.rollback()
