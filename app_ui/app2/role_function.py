import logging
import os
import re
import uuid
from tkinter import *
import tkinter as tk
import mysql.connector
from data_permission import * 
from role_base import Role
import sys
import socket
import platform
import time
import json
import hmac
import hashlib
import base64
mydb = mysql.connector.connect(
	host="localhost",
	user="root",
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

def log_action(action):
	info = get_system_info()
	logging.info(f"{action} - IP: {info['IP']}, Device: {info['Device']}, OS: {info['OS']}")
def check_user(user_id):
	check_com = "SELECT * FROM tt_nv WHERE user_id = %s"
	mycursor.execute(check_com, (user_id,))
	result = mycursor.fetchone()
	return result
class RoleManager:
	def __init__(self):
		self.users = {}
		self.logger = logging.getLogger(__name__)
	def assign_role(self, user_id):
		try:
			while True: 
				role_val = ["manage", "support", "finance", "employee", "admin"] 
				role = input("Nhập tên vai trò cần thêm: ")
				if role in role_val:
					command = "UPDATE tt_nv SET vai_tro = %s WHERE user_id = %s"  
					mycursor.execute(command, (role, user_id))
					mydb.commit()
					print(f"Đã gán vai trò {role} cho người dùng có ID {user_id}")
					return True
				else:
					print("Vai trò không hợp lệ!")
		except Exception as e:
			self.logger.error(f"Lỗi khi gán vai trò: {e}")
			return False
	def delete_role(self, user_id):
		try:
			command = "UPDATE tt_nv set vai_tro=Null where user_id=%s"
			mycursor.execute(command,(user_id,))
			mydb.commit()
			result=mycursor.fetchone()
			print(f"đã xóa vai trò cho id {user_id} thành công ")
			return result
		except Exception as e:
			print(f"lỗi không xóa được vai trò người dùng! {e}")
	

def them_nguoi_dung():
	role_manager = RoleManager()
	user_id = input("Nhập ID người dùng cần gán: ")
	if not check_user(user_id):
		print("Không tìm thấy ID người dùng")
	else:
		if role_manager.assign_role(user_id):
			print("Thêm vai trò thành công!")

def xoa_nguoi_dung():
	user_id = input("Nhập ID người dùng cần xóa: ").strip()
	if check_user(user_id):
		command = "DELETE FROM tt_nv WHERE user_id = %s"
		mycursor.execute(command, (user_id,))
		mydb.commit()
		print(f"Đã xóa người dùng có ID {user_id}")
	else:
		print("Không tìm thấy ID người dùng")
def kiem_tra_vai_tro():
	role = input("Nhập vai trò cần kiểm tra: ")
	try:
		command = "SELECT * FROM tt_nv WHERE vai_tro = %s" 
		mycursor.execute(command, (role,))
		results = mycursor.fetchall()
		if results:
			print(f"\nDanh sách người dùng có vai trò '{role}':")
			column_names = [desc[0] for desc in mycursor.description]
			for result in results:
				user_dict = dict(zip(column_names, result))
				print("\nThông tin người dùng:")
				for key, value in user_dict.items():
					if key != 'password': 
						if key == 'token' and value is not None:
							try:
								if isinstance(value, bytes):
									hex_key = value.hex().upper()
									formatted_key = "-".join(hex_key[i:i+8] for i in range(0, len(hex_key), 8))
									print(f"{key.capitalize()}: {formatted_key}")
								else:
									print(f"{key.capitalize()}: {value}")
							except AttributeError:
								print(f"{key.capitalize()}: {value} (không thể định dạng)")
						else:
							print(f"{key.capitalize()}: {value}")
		else:
			print(f"Không tìm thấy người dùng nào có vai trò '{role}'")
	except Exception as e:
		print(f"Lỗi khi tìm kiếm vai trò: {e}")
def kiem_tra_nguoi_dung():
	user_id = input("Nhập ID người dùng cần kiểm tra: ")
	result = check_user(user_id)
	if result:
		column_names = [desc[0] for desc in mycursor.description]
		user_dict = dict(zip(column_names, result))
		print("\nThông tin người dùng:")
		for key, value in user_dict.items():
			if key != 'password': 
				if key == 'token' and value is not None:
					try:
						if isinstance(value, bytes):
							hex_key = value.hex().upper()
							formatted_key = "-".join(hex_key[i:i+8] for i in range(0, len(hex_key), 8))
							print(f"{key.capitalize()}: {formatted_key}")
						else:
							print(f"{key.capitalize()}: {value}")
					except AttributeError:
						print(f"{key.capitalize()}: {value} (không thể định dạng)")
				else:
					print(f"{key.capitalize()}: {value}")
	else:
		print("Không tìm thấy ID người dùng")

def base64url_decode(data):
    padding = '=' * (4 - len(data) % 4)
    return base64.urlsafe_b64decode((data + padding).encode('utf-8'))
def base64_encode(data: bytes)->str:
	return base64.urlsafe_b64encode(data).rstrip(b'=').decode()
def check_token(user_id,token):
	command="SELECT token from tt_nv WHERE user_id=%s"
	mycursor.execute(command,(user_id,))
	result=mycursor.fetchone()
	if result:
		try:
			with open("secrets_key.txt","rb") as e:
				key=e.read()
			header_b64, payload_b64, signature_b64 = token.split('.')
			signature_check = hmac.new(
				key,
				f"{header_b64}.{payload_b64}".encode(),
				hashlib.sha256
			).digest()
			if base64_encode(signature_check) != signature_b64:
				print("Invalid signature")
				return None
			payload_json = base64url_decode(payload_b64)
			payload = json.loads(payload_json)

			print("Token hợp lệ")
			return payload

		except Exception as e:
			print("lỗi xác thực: ", e)
			return None
def chinh():
	current_user_id = None
	while True:
		print("\n--- Quản Lý Người Dùng và Vai Trò ---")
		print("1. Thêm người dùng")
		print("2. thêm vai trò người dùng")
		print("3. Xóa người dùng/vai trò")
		print("4. Kiểm tra thông tin người dùng")
		print("5. Kiểm tra vai trò")
		print("6. nhắn tin")
		print("7. xác thực token")
		print("8. Thoát")
		
		choice = input("Chọn chức năng (1-8): ").strip()
		
		if choice == '1':
			them_nguoi_dung()
		elif choice=='2':
			user_id=input("nhập id của người cần thêm vai trò: ")
			role_manager = RoleManager()
			role_manager.assign_role(user_id)
		elif choice == '3':
			print("bạn muốn xóa người dùng hay vai trò của người dùng? \n chọn 1 để xóa người dùng \n chọn 2 để xóa vai trò ")
			choose=input("chọn chức năng bạn muốn dùng: ")
			match choose:
				case '1':
					xoa_nguoi_dung()
				case '2':
					user_id=input("nhập id của người cần xóa vai trò: ")
					role_manager = RoleManager()
					role_manager.delete_role(user_id)
				case _:
					print("lựa chọn không hợp lệ!")
		elif choice == '4':
			kiem_tra_nguoi_dung()
		elif choice == '5':
			kiem_tra_vai_tro()
		elif choice=='6':
				BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

				sys.path.insert(0, os.path.join(BASE_DIR, 'bridge'))
				query = "SELECT ho_ten FROM tt_nv WHERE user_id = %s"
				mycursor.execute(query, (current_user_id,))
				result = mycursor.fetchone()
				display_name = result[0] if result else "Người dùng"				
				log_action(f"Người dùng {display_name} bắt đầu chat")
				from socket_admin import main
				main()
		elif choice=='7':
			user_id=input("nhập id người dùng: ")
			token=input("nhập token cần xác thực tại đây: ")
			check_token(user_id,token)		
		elif choice == '8':
			print("Thoát chương trình.")
			break
		else:
			print("Lựa chọn không hợp lệ. Vui lòng thử lại.")
