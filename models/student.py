from .base import BaseModel, db
import bcrypt

class Student(BaseModel):
    __tablename__ = 'students'
    
    student_id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    matricule = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(64), nullable=False)
    last_name = db.Column(db.String(64), nullable=False)
    birth_date = db.Column(db.Date, nullable=False)
    nationality = db.Column(db.String(64), nullable=False)
    gender = db.Column(db.String(64), nullable=False)
    disability = db.Column(db.Boolean, nullable=False)
    phone_number = db.Column(db.String(64), nullable=False)
    observation = db.Column(db.String(255), nullable=False)
    speciality_id = db.Column(db.Integer, db.ForeignKey('specialities.speciality_id'), nullable=False)
    section_id = db.Column(db.Integer, db.ForeignKey('sections.section_id'), nullable=False)
    tutorial_group_id = db.Column(db.Integer, db.ForeignKey('groups.group_id'), nullable=False)
    lab_group_id = db.Column(db.Integer, db.ForeignKey('groups.group_id'), nullable=False)
    
    requests = db.relationship('Request', backref='student', lazy=True)
    swap_group_requests_current = db.relationship('SwapGroupRequest', foreign_keys='SwapGroupRequest.current_student_id', backref='current_student', lazy=True)
    swap_group_requests_requested = db.relationship('SwapGroupRequest', foreign_keys='SwapGroupRequest.requested_student_id', backref='requested_student', lazy=True)
    swap_section_requests_current = db.relationship('SwapSectionRequest', foreign_keys='SwapSectionRequest.current_student_id', backref='current_student', lazy=True)
    swap_section_requests_requested = db.relationship('SwapSectionRequest', foreign_keys='SwapSectionRequest.requested_student_id', backref='requested_student', lazy=True)
    def to_dict(self):
        return {
            'student_id': self.student_id,
            'user_id': self.user_id,
            'user': self.user.to_dict() if self.user else None,
            'matricule': self.matricule,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'birth_date': self.birth_date.strftime('%d/%m/%Y') if self.birth_date else None,
            'nationality': self.nationality,
            'gender': self.gender,
            'disability': self.disability,
            'phone_number': self.phone_number,
            'observation': self.observation,
            'speciality_id': self.speciality_id,
            'speciality': self.speciality.to_dict() if self.speciality else None,
            'section_id': self.section_id,
            'section': self.section.to_dict() if self.section else None,
            'tutorial_group_id': self.tutorial_group_id,
            'tutorial_group': self.tutorial_group.to_dict() if self.tutorial_group else None,
            'lab_group_id': self.lab_group_id,
            'lab_group': self.lab_group.to_dict() if self.lab_group else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @staticmethod
    def validate_student(data, db):
        # check speciality exist
        speciality = db.session.execute(db.select(Speciality).filter_by(speciality_id=data["speciality_id"])).first()
        if not speciality:
            return {"error": "Invalid speciality"} 
        
        # check if section exist and within the same speciality
        section = db.session.execute(db.select(Section).filter_by(section_id=data["section_id"], speciality_id=data["speciality_id"])).first()
        
        if not section:
            return {"error": "Invalid section"}
            
        # check if valid group_td within the section
        group_td = db.session.execute(db.select(Group).filter_by(group_type="TD", group_id=data["tutorial_group_id"], section_id=data["section_id"])).first()
        if not group_td:
            return {"error": "Invalid group TD"}
            
        # check if valid group_tp within the section
        group_tp = db.session.execute(db.select(Group).filter_by(group_type="TP", group_id=data["lab_group_id"], section_id=data["section_id"])).first()
        if not group_tp:
            return {"error": "Invalid group TP"}
        
        return None
    
    def hash_password(password):
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed_password.decode('utf-8')

    def check_password(input_password, stored_hash):
        return bcrypt.checkpw(
            input_password.encode('utf-8'),
            stored_hash.encode('utf-8')
        )