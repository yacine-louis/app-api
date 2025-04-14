from .base import BaseModel, db

class Speciality(BaseModel):
    __tablename__ = 'specialities'
    
    speciality_id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    name = db.Column(db.String(128), nullable=False, unique=True)
    education_level = db.Column(db.Integer, nullable=False)
    
    sections = db.relationship('Section', backref='speciality', lazy=True)
    students = db.relationship('Student', backref='speciality', lazy=True)
    
    def to_dict(self):
        return {
            'speciality_id': self.speciality_id,
            'name': self.name,
            'education_level': self.education_level,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }