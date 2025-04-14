from .base import BaseModel, db

class Request(BaseModel):
    __tablename__ = 'requests'
    
    request_id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.student_id'), nullable=False)
    status = db.Column(db.String(64), nullable=False)
    reason = db.Column(db.Text, nullable=False)
    
    change_group_requests = db.relationship('ChangeGroupRequest', backref='request', lazy=True)
    section_change_requests = db.relationship('SectionChangeRequest', backref='request', lazy=True)
    swap_group_requests = db.relationship('SwapGroupRequest', backref='request', lazy=True)
    swap_section_requests = db.relationship('SwapSectionRequest', backref='request', lazy=True)
    
    def to_dict(self):
        return {
            'request_id': self.request_id,
            'student_id': self.student_id,
            'student': self.student.to_dict() if self.student else None,
            'status': self.status,
            'reason': self.reason,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }