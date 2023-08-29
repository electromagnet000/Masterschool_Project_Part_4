from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey
from flask_login import UserMixin

db = SQLAlchemy()

"""
Classes
"""

class Movie(db.Model):

    __tablename__ = "movies"

    imdb_id = db.Column(db.String, primary_key=True)
    title = db.Column(db.String)
    year = db.Column(db.Integer)
    poster = db.Column(db.String)
    imdb_rating = db.Column(db.String)
    data = db.relationship("Data", backref="movies")


    def __repr__(self):
        return f'{self.name}'

class User(db.Model, UserMixin):

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)

    data = db.relationship("Data", backref="data_user")

    def __repr__(self):
        return f'{self.username}'

class Data(db.Model):

    __tablename__ = "data"

    data_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    movie_imdb_id = db.Column(db.String, db.ForeignKey("movies.imdb_id"))

    movie = db.relationship("Movie", back_populates="data")
    user = db.relationship("User", backref="data_user", foreign_keys=[user_id])

    def __repr__(self):
        return f'{self.name}'



