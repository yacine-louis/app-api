from .base import BaseModel, db

class Staff(BaseModel):
    __tablename__ = 'staffs'
    
    staff_id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    first_name = db.Column(db.String(64), nullable=False)
    last_name = db.Column(db.String(64), nullable=False)
    grade = db.Column(db.String(128), nullable=False)
    
    def to_dict(self):
        return {
            'staff_id': self.staff_id,
            'user_id': self.user_id,
            'user': self.user.to_dict() if self.user else None,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'grade': self.grade,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }