from . import db
from datetime import datetime

class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow())
    source_ip = db.Column(db.String(15), nullable=False)
    destination_ip = db.Column(db.String(50))
    query_type = db.Column(db.String(10))
    query_data = db.Column(db.Text)

    def __repr__(self):
        return f"<Log {self.id}>"
