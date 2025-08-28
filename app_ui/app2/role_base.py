import uuid
import logging
import re
from enum import Enum
from typing import Dict, Set, Optional
from datetime import datetime
import pytz

class Role(Enum):
    ADMIN = "admin"
    HR = "hr" 
    TECH = "tech"
    ACCOUNT = "account"
    EMPLOYEE="employee"
    USER = "user"

    def get_permissions(self) -> Set[str]:
        ROLE_PERMISSIONS = {
            "admin": {"read_all", "write_all", "delete_all", "manage_users", "view_roles"},
            "hr": {"read_employee", "write_employee","manage_roles", "manage_leave", "view_payroll"},
            "tech": {"access_systems", "modify_configurations", "view_logs"},
            "account": {"view_finances", "process_payments", "generate_reports"},
            "employee":{"upload_file","update_file","read_file"},
            "user": {"view_profile", "update_profile", "submit_requests"}
        }
        return ROLE_PERMISSIONS.get(self.value, set())
