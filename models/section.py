from .base import BaseModel, db

class Section(BaseModel):
    __tablename__ = 'sections'
    
    section_id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    speciality_id = db.Column(db.Integer, db.ForeignKey('specialities.speciality_id'), nullable=False)
    name = db.Column(db.String(64), nullable=False)
    max_capacity = db.Column(db.Integer, nullable=False)
    
    groups = db.relationship('Group', backref='section', lazy=True)
    students = db.relationship('Student', backref='section', lazy=True)
    teacher_sections = db.relationship('TeacherSection', backref='section', lazy=True)
    
    def to_dict(self):
        return {
            'section_id': self.section_id,
            'speciality_id': self.speciality_id,
            'speciality': self.speciality.to_dict() if self.speciality else None,
            'name': self.name,
            'max_capacity': self.max_capacity,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }