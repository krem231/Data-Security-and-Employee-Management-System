import socket
import os 
import threading
from tkinter import *
from tkinter import filedialog
import datetime
import sys
from chat_ui import *
import json
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
	return department_file
date = datetime.now()
data_size = 20000
chunk_size=4096
file_perm=data_name()
def openfile():
	root = Tk()
	root.withdraw()
	file = filedialog.askopenfile(title="select file", filetypes=[
		('pdf file', '*.pdf*'),
		('python file', '*.py'),
		('word file', ('*.docx', '*.doc')),
		('excel file', ('*.csv', '*.xls')),
		('jpg file', '*.jpg'),
		('archive file',('*.zip','*.rar'))
	])
	
	while 1:
		print("file da chon: ", file.name)
		file.close()
		break
		return file.name
	return None
def send_data(client):
	try:
		file_path = openfile()
		if file_path and os.path.getsize(file_path) < data_size:
			file_send = f"{os.path.basename(file_path)} :file"
			client.send(file_send.encode('utf-8'))

			with open(file_path, "rb") as f:
				progress = tqdm.tqdm(total=os.path.getsize(file_path), unit="B", unit_scale=True)
				while chunk := f.read(chunk_size):
					client.send(chunk)
					progress.update(len(chunk))
				progress.close()
				# client.shutdown(socket.SHUT_WR) 
			client.send(b"__END__")
			response = client.recv(2048).decode('utf-8')
			print("Server:", response)
		else:
			print("Kích thước file quá lớn hoặc file không hợp lệ!")
	except Exception as e:
		print(f"Lỗi khi gửi file: {str(e)}")

def receive_data(client):
	try:
		while True:
			data_recv = client.recv(data_size)
			if not data_recv:
				break
			print("dữ liệu đã nhận được: ", data_recv.decode('utf-8'))
	except Exception as e:
		print(f"có lỗi trong việc nhận dữ liệu! time: {date}", file=sys.stderr)
	

def man_func(user_name):
	try:
		client=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		host =socket.gethostname() 
		port =9999

		try:
			client.connect((host, port))
			server_res = client.recv(1024)
			print("response:", server_res.decode('utf-8'))
			from chat_ui import run_chat_ui_client
			client.send(bytes(user_name, 'utf-8')) 
			run_chat_ui_client(client, user_name)  
		except Exception as e:
			print(f"Không thể kết nối tới server: {str(e)}")
	except Exception as e:
		print(f"Lỗi khi khởi chạy giao diện chat: {str(e)}")
		print("Chuyển sang chế độ dòng lệnh...")

		def receive_messages():
			while True:
				try:
					message = client.recv(2048).decode('utf-8')
					if not message:
						print("\nMất kết nối tới server")
						break
					print(message)
				except:
					print("\nMất kết nối tới server")
					break

		receive_thread = threading.Thread(target=receive_messages)
		receive_thread.daemon = True
		receive_thread.start()

		print("Nhập 'exit' để thoát hoặc nhấn Ctrl+C")
		while True:
			try:
				message = input()
				if message.lower() == 'exit':
					client.send(f"{user_name}/exit".encode('utf-8'))
					break
				if message.lower().startswith("/send_data"):
					send_data(client)
				if message:
					msg_send = f"{user_name}: {message}"
					client.send(msg_send.encode('utf-8'))
			except KeyboardInterrupt:
				print("\nĐang thoát...")
				client.send(f"{user_name}/exit".encode('utf-8'))
				break
			