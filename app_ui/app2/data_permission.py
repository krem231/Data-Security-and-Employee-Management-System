from role_base import Role
from functools import wraps
from typing import Callable, Set, Dict, Any, Optional
import logging
import mysql.connector

logging.basicConfig(
	level=logging.INFO,
	format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
	handlers=[
		logging.FileHandler("access_control.log"),
		logging.StreamHandler()
	]
)
logger = logging.getLogger(__name__)

mydb = mysql.connector.connect(
	host="localhost",
	user="root",
	password="11111",
	database="nhan_vien"
)
mycursor = mydb.cursor(dictionary=True)

def data_name():
	department_file = {
		"role_id": {
			"hr": {
				"job_id": {
					"personnel": {
						"danh_sách_nhân_viên.xlsx": ["read", "write"],
						"bảng_lương.xlsx": ["read", "write"],
						"danh_sách_chấm_công.xlsx": ["read", "write"],
						"nghỉ_phép.xlsx": ["read", "write"]
					},
					"recruitment": {
						"đăng_thông_tin_tuyển_dụng.docx": ["read", "write"],
						"cv_ứng_viên/": ["read"],
						"lịch_phỏng_vấn.xlsx": ["read", "write"]
					},
					"performance": {
						"bảng_đánh_giá.xlsx": ["read", "write"],
						"đánh_giá_cả_năm.docx": ["read", "write"]
					},
					"policies": {
						"sổ_tay_nhân_viên.pdf": ["read"],
						"chính_sách_công_ty.pdf": ["read", "write"],
						"quy_trình.pdf": ["read", "write"]
					}
				}
			},
			"tech": {
				"job_id": {
					"projects": {
						"project_documentation/": ["read", "write"],
						"source_code/": ["read", "write"],
						"technical_specs.docx": ["read", "write"],
						"deployment_logs.txt": ["read", "write"]
					},
					"infrastructure": {
						"network_configs.yaml": ["read", "write"],
						"server_logs/": ["read", "write"],
						"security_policies.pdf": ["read"],
						"backup_schedules.xlsx": ["read", "write"]
					},
					"support": {
						"incident_reports.xlsx": ["read", "write"],
						"troubleshooting_guides.pdf": ["read"],
						"maintenance_logs.xlsx": ["read", "write"]
					}
				}
			},
			"finance": {
				"job_id": {
					"budgets": {
						"ngân_sách_cả_năm.xlsx": ["read", "write"],
						"báo_cáo_ngân_sách.xlsx": ["read", "write"],
						"ngân_sách_các_phòng_ban.xlsx": ["read", "write"]
					},
					"transactions": {
						"giao_dịch/": ["read", "write"],
						"hóa_đơn/": ["read"],
						"lịch_sử_giao_dịch.xlsx": ["read"]
					},
					"reports": {
						"báo_cáo_tài_chính.xlsx": ["read", "write"],
						"thuế.pdf": ["read", "write"],
						"kiểm_toán.pdf": ["read", "write"]
					},
					"payroll": {
						"lương.xlsx": ["read", "write"],
						"tính_thuế.xlsx": ["read", "write"],
						"tăng_ca.xlsx": ["read", "write"]
					}
				}
			}
		}
	}
	cross_access = {
		"role_id": {
			"hr": {
				"tech/security_policies.pdf": ["read"],
				"finance/ngân_sách_các_phòng_ban.xlsx": ["read"],
				"finance/lương.xlsx": ["read"] 
			},
			"tech": {
				"finance/ngân_sách_các_phòng_ban.xlsx": ["read"],
				"finance/lương.xlsx": ["read"],
				"hr/sổ_tay_nhân_viên.pdf": ["read"],
				"hr/chính_sách_công_ty.pdf": ["read"],
				"hr/quy_trình.pdf": ["read"]
			},      
			"finance": {
				"hr/sổ_tay_nhân_viên.pdf": ["read"],
				"hr/chính_sách_công_ty.pdf": ["read"],
				"hr/quy_trình.pdf": ["read"],
				"tech/security_policies.pdf": ["read"]
			}
		}
	}
	return department_file, cross_access

class CheckPermission:
	def __init__(self):
		self.logger = logger

	def req_permission(self, user_id: str, required_permissions: Set[str]) -> bool:
		try:
			from session import get_user
			user_info = get_user()
			user_id = user_info['user_id']
			
			command = "SELECT vai_tro from tt_nv WHERE user_id=%s"
			mycursor.execute(command, (user_id,))
			result = mycursor.fetchone()

			if not result:
				self.logger.warning(f"Không tìm thấy role của người dùng: {user_id}")
				return False
			
			user_role_str = result['vai_tro']
			if user_role_str == 'admin':
				self.logger.info(f"Người dùng {user_id} là quản trị viên, được cấp toàn quyền")
				return True
			try:
				user_role = Role(user_role_str)
			except ValueError:
				self.logger.error(f"Vai trò không đúng với người dùng: {user_id}")
				return False
			
			role_permissions = user_role.get_permissions()
			if not required_permissions.issubset(role_permissions):
				missing_permissions = required_permissions - role_permissions
				self.logger.warning(f"Cấp quyền người dùng {user_id} thất bại. Thiếu quyền: {missing_permissions}")
				return False
			
			self.logger.info(f"Người dùng {user_id} đã được cấp quyền {required_permissions} thành công")
			return True
		
		except Exception as e:
			self.logger.error(f"Có lỗi trong việc kiểm tra quyền người dùng {user_id}: {e}")
			return False

def require_permission(*req_permissions):
	def decorator(func: Callable):
		@wraps(func)
		def wrapper(self, user_id: str, *args, **kwargs):
			if not hasattr(self, 'permission_manager'):
				raise AttributeError("Object missing permission_manager attribute")
			
			permission_set = set(req_permissions)
			
			if not self.permission_manager.req_permission(user_id, permission_set):
				raise PermissionError(f"Người dùng {user_id} không có quyền: {permission_set}")
			
			return func(self, user_id, *args, **kwargs)
		return wrapper
	return decorator

def check_department_access(user_id: str, required_department: str) -> bool:
	try:
		query = "SELECT phong_ban FROM tt_nv WHERE user_id = %s"
		mycursor.execute(query, (user_id,))
		result = mycursor.fetchone()
		
		if not result or result['phong_ban'] != required_department:
			logger.warning(f"Người dùng {user_id} không thuộc phòng ban {required_department}")
			return False
		
		logger.info(f"Người dùng {user_id} thuộc phòng ban {required_department}")
		return True
		
	except Exception as e:
		logger.error(f"Lỗi khi kiểm tra phòng ban của người dùng {user_id}: {e}")
		return False

def check_file_permission(dept_data: Dict[str, Any], cross_access_data: Dict[str, Any], 
						  job_type: str, file_path: str, mode: str) -> Optional[str]:
	if job_type in dept_data:
		job_files = dept_data[job_type]
		if file_path in job_files:
			permissions = job_files[file_path]
			if mode == "r" and "read" in permissions:
				return f"Mở file {file_path} ở chế độ đọc thành công"
			elif mode == "w" and "write" in permissions:
				return f"Mở file {file_path} ở chế độ ghi thành công"
				
	file_key = f"{job_type}/{file_path}"
	if file_key in cross_access_data:
		permissions = cross_access_data[file_key]
		if mode == "r" and "read" in permissions:
			return f"Mở file {file_path} từ cross-access ở chế độ đọc thành công"
		elif mode == "w" and "write" in permissions:
			return f"Mở file {file_path} từ cross-access ở chế độ ghi thành công"
			
	return None

class FileAccessManager:
	def __init__(self):
		self.permission_manager = CheckPermission()
		self.department_file, self.cross_access = data_name()

	def _department_file_access(self, user_id: str, department: str, job_type: str, file_path: str, mode: str = "r"):
		try:
			command = "SELECT vai_tro from tt_nv WHERE user_id=%s"
			mycursor.execute(command, (user_id,))
			result = mycursor.fetchone()
			if result and result['vai_tro'] == 'admin':
				logger.info(f"User {user_id} is admin, granting access to {file_path}")
				return f"Admin user {user_id} granted access to {file_path}"

			if not check_department_access(user_id, department):
				raise PermissionError(f"Người dùng {user_id} không thuộc phòng ban {department}")
			
			dept_data = self.department_file["role_id"][department]["job_id"]
			cross_access_data = self.cross_access["role_id"][department]
			
			result = check_file_permission(dept_data, cross_access_data, job_type, file_path, mode)
			if result:
				logger.info(f"User {user_id}: {result}")
				return result
			else:
				raise PermissionError(f"Người dùng {user_id} không có quyền {mode} với file {file_path}")
			
		except Exception as e:
			logger.warning(f"Có lỗi trong việc truy cập file: {e}")
			raise
	def hr_access_files(self, user_id: str, job_type: str, file_path: str, mode: str = "r"):
		required_permission = set(["hr"])
		if not self.permission_manager.req_permission(user_id, required_permission):
			raise PermissionError(f"Người dùng {user_id} không có quyền hr")
		return self._department_file_access(user_id, "hr", job_type, file_path, mode)
	def tech_access_files(self, user_id: str, job_type: str, file_path: str, mode: str = "r"):
		required_permission = set(["tech"])
		if not self.permission_manager.req_permission(user_id, required_permission):
			raise PermissionError(f"Người dùng {user_id} không có quyền tech")
		return self._department_file_access(user_id, "tech", job_type, file_path, mode)
	def finance_access_files(self, user_id: str, job_type: str, file_path: str, mode: str = "r"):
		required_permission = set(["finance"])
		if not self.permission_manager.req_permission(user_id, required_permission):
			raise PermissionError(f"Người dùng {user_id} không có quyền finance")
		return self._department_file_access(user_id, "finance", job_type, file_path, mode)
	def access_file(self, user_id: str, department: str, file_path: str,job_type:str, mode: str = "r"):
		supported_departments = {
			"hr": self.hr_access_files,
			"tech": self.tech_access_files,
			"finance": self.finance_access_files
		}
		
		try:
			if department not in supported_departments:
				raise ValueError(f"Phòng ban {department} không được hỗ trợ")
				
			return supported_departments[department](user_id, job_type, file_path, mode)
				
		except Exception as e:
			logger.error(f"Có lỗi trong việc truy cập file: {e}")
			raise