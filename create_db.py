from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey, PrimaryKeyConstraint
from sqlalchemy.orm import relationship

db = SQLAlchemy()


class Bands(db.Model):
    __tablename__ = "bands"

    # имя колонки = специальный тип (тип данных, первичный ключ)
    id = db.Column(db.Integer, primary_key=True)
    band_name = db.Column(db.Text)
    verbs = db.Column(db.Integer)
    nouns = db.Column(db.Integer)
    adjectives = db.Column(db.Integer)
    adverbs = db.Column(db.Integer)
    propernouns = db.Column(db.Integer)

    # соединяем
    band_id = db.relationship('Texts')

class Texts(db.Model):
    __tablename__ = "texts"

    song_id = db.Column(db.Integer, primary_key=True)
    song_name = db.Column(db.Text)
    band_id = db.Column(db.Integer, ForeignKey('bands.id'))
    text = db.Column(db.Text)