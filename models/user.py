from .base import BaseModel, db

class User(BaseModel):
    __tablename__ = 'users'
    
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    hashed_password = db.Column(db.String(255), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.role_id'), nullable=False)
    
    teachers = db.relationship('Teacher', backref='user', lazy=True)
    students = db.relationship('Student', backref='user', lazy=True)
    staffs = db.relationship('Staff', backref='user', lazy=True)
    notifications = db.relationship('Notification', backref='user', lazy=True)
    
    def to_dict(self):
        return {
            'user_id': self.user_id,
            'email': self.email,
            'role_id': self.role_id,
            'hashed_password': self.hashed_password,
            'role': self.role.to_dict() if self.role else None, 
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    