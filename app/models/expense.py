from app.extensions import db
from datetime import datetime

class Expense(db.Model):
    __tablename__ = "expenses"

    id=db.Column(db.Integer,primary_key=True)
    amount=db.Column(db.Float,nullable=False)
    category=db.Column(db.String(50),nullable=False)
    date=db.Column(db.DateTime,default=datetime.utcnow)
    user_id=db.Column(db.Integer,db.ForeignKey("user.id"),nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "amount": self.amount,
            "category": self.category,
            "date": self.date.strftime("%Y-%m-%d %H:%M:%S"),
            "user_id": self.user_id
        }