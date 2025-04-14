from .base import BaseModel, db

class ChangeGroupRequest(BaseModel):
    __tablename__ = 'change_group_requests'
    
    change_group_request_id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    request_id = db.Column(db.Integer, db.ForeignKey('requests.request_id'), nullable=False)
    current_group_id = db.Column(db.Integer, db.ForeignKey('groups.group_id'), nullable=False)
    requested_group_id = db.Column(db.Integer, db.ForeignKey('groups.group_id'), nullable=False)
    
    def to_dict(self):
        return {
            'change_group_request_id': self.change_group_request_id,
            'request_id': self.request_id,
            'request': self.request.to_dict() if self.request else None,
            'current_group_id': self.current_group_id,
            'current_group': self.current_group.to_dict() if self.current_group else None,
            'requested_group_id': self.requested_group_id,
            'requested_group': self.requested_group.to_dict() if self.requested_group else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }