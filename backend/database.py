from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Voucher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(100), unique=True, nullable=False)
    type = db.Column(db.String(20), nullable=False)
    expiry = db.Column(db.Date, nullable=False)
