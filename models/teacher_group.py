from .base import BaseModel, db

class TeacherGroup(BaseModel):
    __tablename__ = 'teacher_groups'
    
    teacher_groups_id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.teacher_id'), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.group_id'), nullable=False)
    
    def to_dict(self):
        return {
            'teacher_groups_id': self.teacher_groups_id,
            'teacher_id': self.teacher_id,
            'teacher': self.teacher.to_dict() if self.teacher else None,
            'group_id': self.group_id,
            'group': self.group.to_dict() if self.group else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }