from flask_sqlalchemy import SQLAlchemy

# Initialize SQLAlchemy
db = SQLAlchemy()

# Import models
from .base import BaseModel

from .role import Role
from .user import User
from .speciality import Speciality
from .section import Section
from .teacher import Teacher
from .group import Group
from .student import Student
from .staff import Staff
from .teacher_section import TeacherSection
from .teacher_group import TeacherGroup
from .request import Request
from .change_group_request import ChangeGroupRequest
from .section_change_request import SectionChangeRequest
from .notification import Notification
from .swap_group_request import SwapGroupRequest
from .swap_section_request import SwapSectionRequest

