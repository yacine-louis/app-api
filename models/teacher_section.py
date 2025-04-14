from .base import BaseModel, db

class TeacherSection(BaseModel):
    __tablename__ = 'teacher_sections'
    
    teacher_section_id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.teacher_id'), nullable=False)
    section_id = db.Column(db.Integer, db.ForeignKey('sections.section_id'), nullable=False)
    
    def to_dict(self):
        return {
            'teacher_section_id': self.teacher_section_id,
            'teacher_id': self.teacher_id,
            'teacher': self.teacher.to_dict() if self.teacher else None,
            'section_id': self.section_id,
            'section': self.section.to_dict() if self.section else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }