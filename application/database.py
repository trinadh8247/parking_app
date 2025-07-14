from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone_number = db.Column(db.String(15), nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(10), nullable=False, default='user')

class Parking_lot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    prime_location_name = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, nullable=False)
    pincode = db.Column(db.String(10), nullable=False)
    maximum_number_of_spot = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='active')

    spot = db.relationship('Parking_spot', backref=db.backref('lot', lazy=True))


class Parking_spot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lot_id = db.Column(db.Integer, db.ForeignKey('parking_lot.id'), nullable=False)
    status = db.Column(db.String(10), nullable=False)
    is_active = db.Column(db.Boolean, default=True)

    reservations = db.relationship('Reserve_spot', backref='spot', lazy=True)


class Reserve_spot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    spot_id = db.Column(db.Integer, db.ForeignKey('parking_spot.id'), nullable=False)  
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    end_time = db.Column(db.DateTime)
    total_cost = db.Column(db.Float)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) 
    vehicle_number = db.Column(db.String(20), nullable=False)
    user = db.relationship('User', backref='reservations', lazy=True)
    


   

# this is my schema now only edit the database part and dont give me editied word tjust give me text , i will paste it in my doc