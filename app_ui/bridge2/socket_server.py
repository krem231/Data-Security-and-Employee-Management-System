import socket
import os
import logging
import threading
import signal
import sys
from queue import Queue
from tkinter import Tk
from tkinter import filedialog
import time
import requests
sys.path.insert(0,"A://Desktop/app/")
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

file_size = 200000
msg_queue = Queue()
logger = logging.getLogger(__name__)
clients=[]
file_perm=data_name()
clients_lock=threading.Lock()
chat_room={}
HTTP_SERVER_URL="http://127.0.0.1:9999/upload"
def upload_file_to_http(file_path):
	try:
		logger.info(f"Đang tải file lên HTTP server: {file_path}")
		with open(file_path, 'rb') as f:
			files = {'file': (os.path.basename(file_path), f)}
			response = requests.post(HTTP_SERVER_URL, files=files, timeout=10)
			
		if response.status_code == 200 or response.status_code == 303:
			logger.info(f"File {file_path} đã được tải lên HTTP server thành công!")
			return True
		else:
			logger.error(f"Lỗi khi tải file lên HTTP server: {response.status_code}")
			return False
	except Exception as e:
		logger.error(f"Lỗi khi gửi file: {str(e)}")
		return False
def handle_file(client_socket, file_name):
	try:
		if not os.path.exists('received_files'):
			os.makedirs('received_files')

		file_name = file_name.replace(" :file", "")
		file_path = os.path.join('received_files', file_name)
		logger.info(f"Đang nhận file: {file_path}")

		with open(file_path, 'wb') as f:
			while True:
				chunk = client_socket.recv(4096)
				if b"__END__" in chunk:
					end_index = chunk.find(b"__END__")
					f.write(chunk[:end_index]) 
					logger.info("Kết thúc nhận file.")
					break
				f.write(chunk)
		logger.info(f"File đã lưu tại {file_path}")
		if upload_file_to_http(file_path):
			response = f"File {file_name} đã tải lên HTTP server thành công!"
			os.remove(file_path)
		else:
			response = f"File {file_name} tải lên HTTP server thất bại!"

		client_socket.send(response.encode('utf-8'))

	except Exception as e:
		logger.error(f"Lỗi xử lý file: {str(e)}")
		client_socket.send(f"Lỗi: {str(e)}".encode('utf-8'))

	finally:
		client_socket.close()
		logger.info(f"Đã đóng kết nối với client sau khi xử lý file.")
def transform(data,rotate):
	resault=bytearray(data)
	for i in len(resault):
		resault[i]=resault[i]^rotate
	return resault

def broadcast(msg,sender_client): 
	with clients_lock:
		disconnected_clients = []
		for client in clients:
			if client['socket'] != sender_client['socket']:
				try:
					client['socket'].send(msg.encode('utf-8'))
				except:
					disconnected_clients.append(client)
		for client in disconnected_clients:
			delete_client(client)

def delete_client(client):
	with clients_lock:
		if client in clients:
			clients.remove(client)


def listen(server):
	print("Server đang chờ kết nối...")
	while True:
		client_socket, addr = server.accept()
		client_socket.settimeout(300)
		print(f"Có kết nối mới từ {addr}")
		client_socket.send("Kết nối thành công!".encode('utf-8'))
		
		initial_message = client_socket.recv(1024).decode('utf-8')
		try:
			if initial_message.endswith(" :file"):
				print(f"file từ {addr}: {initial_message}")
				thread = threading.Thread(target=handle_file, args=(client_socket, initial_message))
				thread.daemon = True
				thread.start()
			else:
				client_name = initial_message
				client = {
					'name': client_name,
					'socket': client_socket,
					'address': addr
				}
				with clients_lock:
					clients.append(client)
				
				msg = f"User {client_name} has joined the chat!"
				print(msg)
				broadcast(msg, client)
				
				thread = threading.Thread(target=handle_new_client, args=(client,))
				thread.daemon = True
				thread.start()
		except (ConnectionResetError, BrokenPipeError, OSError):
			print("Mất kết nối tới server. Vui lòng thử lại sau.")

def handle_new_client(client):
	client_name = client['name']
	client_socket = client['socket']
	
	while True:
		msg_recv = client_socket.recv(1024).decode()
		if not msg_recv or msg_recv.strip() == client_name + "/exit":
			noti = f"User {client_name} has left the chat!"
			broadcast(noti, client)
			delete_client(client)
			client_socket.close()
		if msg_recv.startswith("check_user:"):
			username=msg_recv.split(":", 1)[1]
			if check_user_exists(username):
				client_socket.send("user online".encode('utf-8'))
			else:
				client_socket.send("user not found".encode('utf-8'))
		elif msg_recv.startswith("private:"): 
			msg_part=msg_recv.split(':',2)
			if len(msg_part)<3:
				header=msg_part[0]
				sender=msg_part[1]
				msg_content=msg_part[2]
				succes=private_mess(header,sender,msg_content)
				if succes:
					respone=f"đã gửi tin nhắn thành công!"
					client.send(bytes(response,'utf-8'))
				else:
					respone=f"không thể gửi tin nhắn!"
					client.send(bytes(response,'utf-8'))
			if message.endswith(" :file"):
				print("File upload detected") 
				file_name = message.replace(" :file", "")
				msg_queue.put(file_name)
				print(f"Receiving file: {file_name}")  
				file_path = os.path.join('received_files', file_name)
				handle_file(client, file_path)
		else:
			broadcast(msg_recv, client)

def check_user(username):
	with clients_lock:
		for client in clients:
			if client['name']==username:
				client.send(bytes('user online','utf-8'))

			else:
				client.send(bytes("user not exist!",'utf-8'))

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print("socket create!")
host=socket.gethostname()
port=9999
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((host, port)) 
server.listen(5)
print("waiting for host!")
print("Nhấn Ctrl+C để thoát server")
try:
	listen(server)
except KeyboardInterrupt:
	server.close()