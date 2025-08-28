from encrypt import *
import logging
import socket
import platform
import mysql.connector
import sys
from session import get_user
from role_base import Role
from session import get_user
import time
import threading
import maskpass
logging.basicConfig(filename='logging.txt', level=logging.INFO, 
					format='%(asctime)s - [%(levelname)s] %(message)s')
mydb = mysql.connector.connect(
	host="localhost",
	username="root",
	password="11111",
	database="nhan_vien"
)
mycursor = mydb.cursor()
def get_system_info():
	return {
		"IP": socket.gethostbyname(socket.gethostname()),
		"Device": socket.gethostname(),
		"OS": platform.system() + " " + platform.release()
	}

def get_token(user_id):
	command="SELECT token from tt_nv where user_id=%s"
	mycursor.execute(command,(user_id,))
	result=mycursor.fetchone()
	if result:
		return result[0]
	return None

def log_action(action):
	info = get_system_info()
	logging.info(f"{action} - IP: {info['IP']}, Device: {info['Device']}, OS: {info['OS']}")

def kiem_tra_thong_tin(user_id):
	check_com = "SELECT * FROM tt_nv WHERE user_id = %s"
	mycursor.execute(check_com, (user_id,))
	result = mycursor.fetchone()
	from main import rot_token
	rotate=rot_token(user_id)
	if result:
		column_names = [desc[0] for desc in mycursor.description]
		user_dict = dict(zip(column_names, result))

		print("\nThông tin cá nhân của bạn:")
		for key, value in user_dict.items():
			if key != 'password' and key!='token':
				print(f"{key.capitalize()}: {value}")

def choose():
	user_info = get_user()
	current_user_id = user_info['user_id']
	user_role = user_info['role']
	from role_base import Role
	from data_permission import FileAccessManager
	query = "SELECT user_id, ho_ten, vai_tro, phong_ban FROM tt_nv"
	mycursor.execute(query)
	users_data = {}
	for user in mycursor.fetchall():
		users_data[user[0]] = {
			'name': user[1],
			'role': user[2],
			'department': user[3]
		}
	access_control = FileAccessManager()
	while 1:
		print("chon chuc nang de dung", "\n", "1: de ma hoa", "\n", "2: de giai ma", "\n","3: de xem thong tin ca nhan","\n","4: de kiem tra token","\n", "5: de nhan tin","\n","6: de thoat khoi chuong trinh")
		agrgument = int(input("Nhap lua chon cua ban (1-6): "))
		log_action(f"Nguoi dung chon: {agrgument}")
		match agrgument:
			case 1:
				print(" chon 1 de ma hoa file", "\n", "chon 2 de ma hoa folder", "\n" ,"chon 4 de thoat khoi ma hoa")
				choose = int(input("nhap lua chon cua ban(1/2/3): "))
				log_action(f"Nguoi dung chon ma hoa: {choose}")
				match choose:
					case 1:
						user_department = user_info['department']
						file = openfile()
						try:
							access_control.access_file(current_user_id, user_department, file, "admin", "w")
							log_action(f"Nguoi dung ma hoa file: {file}")
							encrypt(file)
						except PermissionError as e:
							print(f"Bạn không có quyền mở file này: {e}")
						except ValueError as e:
							print(f"Lỗi truy cập phòng ban: {e}")
						except Exception as e:
							print(f"Lỗi không xác định: {e}")
					case 2:
						direc = open_direc()
						log_action(f"Nguoi dung ma hoa folder: {direc}")
						encrypt_folder(direc)
					case 4:
						continue
					case _:
						print("vui long nhap lua chon hop le")
			case 2:
				print(" chon 1 de giai ma file", "\n", "chon 2 de giai ma folder", "\n", "chon 3 de thoat khoi giai ma")
				choose = int(input("nhap lua chon cua ban(1/2/3): "))
				log_action(f"Nguoi dung chon giai ma: {choose}")
				match choose:
					case 1:
						filed = filedialog.askopenfile()
						log_action(f"Nguoi dung chon file de giai ma: {filed.name}")
						max_attempt = 3
						login_attempts = 0

						while login_attempts < max_attempt:
							key_attempts = 0
							print(f"nhap key lan {login_attempts + 1}")
							while key_attempts < max_attempt:
								print("nhap key de giai ma: ")
								key = input()
								try:
									if decrypt(key, filed):
										log_action("Giai ma thanh cong")
										return True
								except Exception as e:
									key_attempts += 1
									remain = max_attempt - key_attempts
									log_action(f"Nhap sai key ({key_attempts}/{max_attempt})")
									if remain > 0:
										print(f"key nhap sai, ban con {remain} lan nhap")
									else:
										print("da het lan thu!")
										break
							login_attempts += 1
							remain_log = max_attempt - login_attempts
							if remain_log > 0:
								print(f"ban con co the nhap lai key {remain_log} lan")
							else:
								print("ban khong con co the nhap key!")
								log_action("Da vuot qua so lan nhap key!")
								break

					case 2:
						folder = open_direc()
						log_action(f"Nguoi dung chon folder de giai ma: {folder}")
						max_attempt = 3
						login_attempts = 0

						while login_attempts < max_attempt:
							key_attempts = 0
							print(f"nhap key lan {login_attempts + 1}")
							while key_attempts < max_attempt:
								print("nhap key de giai ma: ")
								key = input()
								try:
									decrypt_folder(key, folder)
									log_action("Giai ma folder thanh cong")
									return_to_menu = True
									break
								except Exception as e:
									key_attempts += 1
									remain = max_attempt - key_attempts
									log_action(f"Nhap sai key ({key_attempts}/{max_attempt})")
									if remain > 0:
										print(f"key nhap sai, ban con {remain} lan nhap")
									else:
										print("da het lan thu!")

							if 'return_to_menu' in locals() and return_to_menu:
								break
							login_attempts += 1
							remain_log = max_attempt - login_attempts
							if remain_log > 0:
								print(f"ban con co the nhap lai key {remain_log} lan")
							else:
								print("ban khong con co the nhap key!")
								log_action("Da vuot qua so lan nhap key!")
								break
					case _:
						print("vui long nhap lua chon hop le")
			case 3: 
				user_info=get_user()
				user_id=user_info['user_id']
				command="SELECT * from tt_nv where user_id=%s"
				mycursor.execute(command,(user_id,))
				result=mycursor.fetchone()
				if result:
					kiem_tra_thong_tin(current_user_id)
				else:
					print("không tìm thấy thông tin người dùng")
			case 4:
				user_info=get_user()
				password = maskpass.askpass(prompt="password: ", mask="#")
				user_id=user_info['user_id']
				command="SELECT password from tt_nv where user_id=%s"
				mycursor.execute(command,(user_id,))
				result=mycursor.fetchone()
				db_pass=result[0]
				if password==db_pass:
					token=get_token(user_id)
					print("token của người dùng: ",token)
				else:
					print("mật khẩu người dùng không hợp lệ")
			case 5:
				BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

				sys.path.insert(0, os.path.join(BASE_DIR, 'bridge'))
				info=get_user()
				display_name = info[1]
					
				log_action(f"Người dùng {display_name} bắt đầu chat")
				from client import man_func
				man_func(user_name=display_name)
			case 6:
				log_action("Nguoi dung thoat chuong trinh")
				break
			case _:
				print("lua chon khong hop le")

