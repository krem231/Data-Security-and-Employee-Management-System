import os
import sys
from login_admin import get_user_info
from role_function import chinh
from regis import register
import loginUI
import regisUI
from loginUI import create_login_ui
from functionUI import open_function_ui
from session import set_user
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import maskpass
from function import choose
import mysql.connector
import logging
import urllib.request
import socket
import json
import platform
from regis import register

import logging

def on_login_attempt(username, password, root):
    user_info = get_user_info(username, password)
    print("DEBUG - user_info:", user_info)
    
    if user_info:
        if len(user_info) < 6:
            print(" Lỗi: Dữ liệu user_info không hợp lệ!", user_info)
            return
        
        user_id, ho_ten, phone_number, phong_ban, vai_tro, email, *_ = user_info
        set_user(user_id, ho_ten, vai_tro, phong_ban)
        print(" Đăng nhập thành công!")
        root.destroy()
        open_function_ui()
    else:
        print(" Sai tên đăng nhập hoặc mật khẩu!")

def on_register_attempt(user_data):
    """Xử lý đăng ký"""
    logging.info(f"Người dùng mới đăng ký: {user_data}")
    print("\nĐăng ký thành công! Chuyển đến trang đăng nhập...")
    loginUI.create_login_ui(on_login_attempt) 

# from data_permission import Permissions, CheckPermission
from session import set_user
mydb = mysql.connector.connect(
	host="localhost",
	user="root",
	password="11111",
	database="nhan_vien",
)
mycursor = mydb.cursor()
users_cache = {}

def load_users_cache():
    try:
        query = "SELECT user_id, ho_ten, val_tro as role, phong_ban FROM tt_nv"
        mycursor.execute(query)
        users = mycursor.fetchall()
        
        for user in users:
            users_cache[user['user_id']] = {
                'name': user['ho_ten'],
                'role': user['role'],
                'department': user['phong_ban']
            }
        
        logger.info(f"Đã tải thông tin {len(users_cache)} người dùng")
        return users_cache
    except Exception as e:
        logger.error(f"Lỗi khi tải thông tin người dùng: {e}")
        return {}

logging.basicConfig(filename='logging.txt', level=logging.INFO, 
					format='%(asctime)s - [%(levelname)s] %(message)s')
permission_system = None

def init_permission_system():
    global permission_system
    users = load_users_cache()
    permission_system = Permissions(users)
    logger.info("Hệ thống phân quyền đã được khởi tạo")
    return permission_system
def start_permission_service():
    service_thread = threading.Thread(target=run_as_service, daemon=True)
    service_thread.start()
    logger.info("Dịch vụ phân quyền đã được khởi động")
    return service_thread
def get_system_info():
	return{
		"IP": socket.gethostbyname(socket.gethostname()),
		"Device": socket.gethostname(),
		"OS": platform.system() + " " + platform.release(),
	}

def rotate_token(token,rotate):
	result = []
	for char in token:
		rotated_char = ord(char) ^ rotate
		result.append(chr(rotated_char))
	return ''.join(result)
def get_token(user_id):
	command="SELECT token from tt_nv where user_id=%s"
	mycursor.execute(command,(user_id,))
	result=mycursor.fetchone()
	if result:
		return result[0]
	return None
def rot_token(user_id):
	original_token=get_token(user_id)
	rotate=7
	try:
		with open("logging.txt", "r") as log_file:
			lines = log_file.readlines()
			user_logs = [line for line in lines if f"nguoi dung {user_id}" in line]
			
			if len(user_logs) >= 2:
				current_log = user_logs[-1]
				previous_log = user_logs[-2]
			  
				current_ip = current_log.split("IP: ")[1].split(",")[0]
				previous_ip = previous_log.split("IP: ")[1].split(",")[0]
				current_device=current_log.split("Device: ")[1].split(",")[0]
				previous_device=current_log.split("Device: ")[1].split(",")[0]
				if current_ip != previous_ip or current_device !=previous_device:
					rotate = (rotate % 256) + 13
					rotated_token = rotate_token(original_token, rotate)
					save_rotated_token_to_session(user_id, rotated_token)
					
					return rotated_token
	except Exception as e:
		logging.error(f"Lỗi khi xoay token: {str(e)}")
	return original_token
def save_rotated_token_to_session(user_id, rotated_token):

	global rotated_tokens
	if 'rotated_tokens' not in globals():
		global rotated_tokens
		rotated_tokens = {}
	
	rotated_tokens[user_id] = rotated_token

def log_action(action):
	info = get_system_info()
	logging.info(f"{action} - IP: {info['IP']}, Device: {info['Device']}, OS: {info['OS']}",)
def login():
    attempts = 0
    max_attempts = 3

    def on_login_attempt_a(username, password,root):
        nonlocal attempts
        user_info = get_user_info(username, password)

        if user_info:
            logging.info(f"Người dùng {username} đăng nhập thành công")
            print("\nĐăng nhập thành công!")
            root.destroy()
            process_login(username, password)
        else:
            attempts += 1
            remaining = max_attempts - attempts
            if remaining > 0:
                logging.warning(f"Người dùng {username} nhập sai, còn {remaining} lần thử")
                loginUI.messagebox.showwarning("Cảnh báo", f"Thông tin đăng nhập không đúng! Còn {remaining} lần thử.")
            else:
                logging.error(f"Người dùng {username} bị khóa sau {max_attempts} lần thử")
                loginUI.messagebox.showerror("Lỗi", "Bạn đã nhập sai quá nhiều lần. Vui lòng thử lại sau.")
                root.destroy()
    global root
    root = loginUI.create_login_ui(on_login_attempt)
    
def register_user():
    def on_register_attempt(user_data):
        regis_result = register(user_data)
        if regis_result:
            logging.info("Người dùng mới đã đăng ký tài khoản")
            print("\nĐăng ký thành công! Chuyển đến trang đăng nhập...")
            login()
    
    regisUI.create_register_ui(on_register_attempt)
    
def process_login(username, password, root):
    command = "SELECT user_id, ho_ten, vai_tro, phong_ban FROM tt_nv WHERE ho_ten = %s AND password = %s"
    mycursor.execute(command, (username, password,))
    result = mycursor.fetchone()

    if result:
        user_id, user_name, role, department = result
        set_user(user_id, user_name, role, department)
        show_menu(role)

def show_menu(user_role):
    if user_role in ['admin', 'manage']:
        choose()
        chinh()
    else:
        choose()



def main():
    loginUI.create_login_ui(on_login_attempt) 

if __name__ == "__main__":
    main()