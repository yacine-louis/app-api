from .base import BaseModel, db

class ChangeSectionRequest(BaseModel):
    __tablename__ = 'change_section_requests'
    
    section_change_request_id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    request_id = db.Column(db.Integer, db.ForeignKey('requests.request_id'), nullable=False)
    current_section_id = db.Column(db.Integer, db.ForeignKey('sections.section_id'), nullable=False)
    requested_section_id = db.Column(db.Integer, db.ForeignKey('sections.section_id'), nullable=False)
    
    def to_dict(self):
        return {
            'section_change_request_id': self.section_change_request_id,
            'request_id': self.request_id,
            'request': self.request.to_dict() if self.request else None,
            'current_section_id': self.current_section_id,
            'current_section': self.current_section.to_dict() if self.current_section else None,
            'requested_section_id': self.requested_section_id,
            'requested_section': self.requested_section.to_dict() if self.requested_section else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }