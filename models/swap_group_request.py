from .base import BaseModel, db

class SwapGroupRequest(BaseModel):
    __tablename__ = 'swap_group_requests'
    
    swap_group_request_id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    request_id = db.Column(db.Integer, db.ForeignKey('requests.request_id'), nullable=False)
    current_student_id = db.Column(db.Integer, db.ForeignKey('students.student_id'), nullable=False)
    requested_student_id = db.Column(db.Integer, db.ForeignKey('students.student_id'), nullable=False)
    
    def to_dict(self):
        return {
            'swap_group_request_id': self.swap_group_request_id,
            'request_id': self.request_id,
            'request': self.request.to_dict() if self.request else None,
            'current_student_id': self.current_student_id,
            'current_student': self.current_student.to_dict() if self.current_student else None,
            'requested_student_id': self.requested_student_id,
            'requested_student': self.requested_student.to_dict() if self.requested_student else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }