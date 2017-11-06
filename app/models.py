from app import db

class Symbol(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)
    whitelisted = db.Column(db.Boolean, default=True)
    historic_values = db.relationship('HistoricValue')
    

class HistoricValue(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    symbol_id = db.Column(db.Integer, db.ForeignKey("symbol.id"))
    symbol = db.relationship('Symbol')
    closing_price = db.Column(db.Numeric)
    date = db.Column(db.Date)

