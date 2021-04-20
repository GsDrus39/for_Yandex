from flask_login import UserMixin
from . import db


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))
    urole = db.Column(db.String(80))


class Line(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.Time)
    seats = db.Column(db.String(100))
    prices = db.Column(db.String(100))
    from_ = db.Column(db.String(100))
    to_ = db.Column(db.String(100))


class Ticket(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    flight_date = db.Column(db.Date)
    fio = db.Column(db.String(100))
    plane_id = db.Column(db.Integer, db.ForeignKey('line.id'))
