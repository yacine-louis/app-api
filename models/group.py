from .base import BaseModel, db

class Group(BaseModel):
    __tablename__ = 'groups'
    
    group_id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    section_id = db.Column(db.Integer, db.ForeignKey('sections.section_id'), nullable=False)
    group_type = db.Column(db.String(64), nullable=False)
    group_name = db.Column(db.String(64), nullable=False)
    max_capacity = db.Column(db.Integer, nullable=False)
    
    students_tutorial = db.relationship('Student', foreign_keys='Student.tutorial_group_id', backref='tutorial_group', lazy=True)
    students_lab = db.relationship('Student', foreign_keys='Student.lab_group_id', backref='lab_group', lazy=True)
    teacher_groups = db.relationship('TeacherGroup', backref='group', lazy=True)
    change_group_requests_current = db.relationship('ChangeGroupRequest', foreign_keys='ChangeGroupRequest.current_group_id', backref='current_group', lazy=True)
    change_group_requests_requested = db.relationship('ChangeGroupRequest', foreign_keys='ChangeGroupRequest.requested_group_id', backref='requested_group', lazy=True)
    def to_dict(self):
        return {
            'group_id': self.group_id,
            'section_id': self.section_id,
            'section': self.section.to_dict() if self.section else None,
            'group_type': self.group_type,
            'group_name': self.group_name,
            'max_capacity': self.max_capacity,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }