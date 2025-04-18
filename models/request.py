from .base import BaseModel, db
from enum import Enum
from models.change_group_request import ChangeGroupRequest
from models.change_section_request import ChangeSectionRequest
from models.swap_group_request import SwapGroupRequest
from models.swap_section_request import SwapSectionRequest

class Request(BaseModel):
    __tablename__ = 'requests'
    
    request_id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.student_id'), nullable=False)
    status = db.Column(db.String(64), nullable=False)
    reason = db.Column(db.Text, nullable=False)
    urgency = db.Column(db.String(64), nullable=False)
    comment = db.Column(db.String(255), nullable=True)
    
    change_group_requests = db.relationship('ChangeGroupRequest', backref='request', lazy=True)
    change_section_requests = db.relationship('ChangeSectionRequest', backref='request', lazy=True)
    swap_group_requests = db.relationship('SwapGroupRequest', backref='request', lazy=True)
    swap_section_requests = db.relationship('SwapSectionRequest', backref='request', lazy=True)
    
    def to_dict(self):
        return {
            'request_id': self.request_id,
            'student_id': self.student_id,
            'student': self.student.to_dict() if self.student else None,
            'status': self.status,
            'reason': self.reason,
            'urgency': self.urgency,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
class RequestStatus(str, Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"
    appealed = "appealed"

class RequestType(str, Enum):
    group = "group"
    section = "section"
    swap = "swap"

class RequestUrgency(int, Enum):
    low = 1
    medium = 2
    high = 3

def filter_by_request_type(requests, request_type):
    if type == 'group':
        #we only keep group related
        requests = requests.filter(
            ChangeSectionRequest.request_id == None,
            SwapSectionRequest.request_id == None
        )
    elif type == 'section':
        #only keep section related
        requests = requests.filter(
            ChangeGroupRequest.request_id == None,
            SwapGroupRequest.request_id == None
        )
    elif type == 'swap':
        #only keep swap related
        requests = requests.filter(
            ChangeGroupRequest.request_id == None,
            ChangeSectionRequest.request_id == None
        )
    return requests


def get_request_type(row):
    if hasattr(row, 'change_group_request') and row.change_group_request:
        return 'group'
    if hasattr(row, 'change_section_request') and row.change_section_request:
        return 'section'
    if hasattr(row, 'swap_group_request') and row.swap_group_request:
        return 'swap'
    if hasattr(row, 'swap_section_request') and row.swap_section_request:
        return 'swap'
    return 'unknown'

