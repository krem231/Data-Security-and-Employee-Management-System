import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog,Listbox
import os
import sys
import subprocess
import mysql.connector
from function import encrypt, decrypt, encrypt_folder, decrypt_folder
from session import get_user
import socket
import threading
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, 'bridge2'))

BASE_DIR = r"A:Desktop\app_ui\bridge2"
if BASE_DIR not in sys.path:
	sys.path.insert(0, BASE_DIR)

mydb = mysql.connector.connect(
	host="localhost",
	username="root",
	password="11111",
	database="nhan_vien"
)
mycursor = mydb.cursor()

def select_file():
	try:
		file_path = filedialog.askopenfilename()
		if not file_path:
			return

		progress_window = tk.Toplevel()
		progress_window.title("Đang tải lên...")
		progress_window.geometry("600x100")
		progress_window.configure(bg="#1a1a2e")
		file_name_label = tk.Label(progress_window, text=f"file đã chọn: {file_path}",
								   fg="white", bg="#1a1a2e", font=("Arial", 10))
		file_name_label.pack(pady=(10, 5))
		progress_frame = tk.Frame(progress_window, bg="#1a1a2e")
		progress_frame.pack(fill="x", padx=20)

		progress_var = tk.IntVar()
		progress_bar = tk.Canvas(progress_frame, width=500, height=25, bg="#1a1a2e",
								 highlightthickness=1, highlightbackground="white")
		progress_bar.pack(side="left")

		percent_label = tk.Label(progress_frame, text="0%", fg="white", bg="#1a1a2e")
		percent_label.pack(side="left", padx=5)

		response_label = tk.Label(progress_window, text="", fg="white", bg="#1a1a2e")
		response_label.pack(pady=5)

		def update_progress(value):
			progress_var.set(value)
			progress_bar.delete("progress")
			width = 5 * value
			progress_bar.create_rectangle(0, 0, width, 25, fill="#4e9eff", tags="progress")
			percent_label.config(text=f"{value}%")
			progress_window.update_idletasks()

		def send_file():
			try:
				client =socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				host=socket.gethostname()
				port=9999
				client.connect((host, port))

				file_size=os.path.getsize(file_path)
				chunk_size=4096
				sent=0

				client.send(f"{os.path.basename(file_path)} :file".encode('utf-8'))
				response = client.recv(1024).decode('utf-8')
				response_label.config(text=f"Server: {response}")

				with open(file_path, 'rb') as f:
					while True:
						chunk = f.read(chunk_size)
						if not chunk:
							client.send(b"__END__")
							break
						client.send(chunk)
						sent += len(chunk)
						progress = int((sent / file_size) * 100)
						update_progress(progress)
				update_progress(100)
				try:
					final_response = client.recv(1024).decode('utf-8')
					response_label.config(text=f"Server: {final_response}")
				except:
					pass

				client.close()
				progress_window.after(1000, progress_window.destroy)

			except Exception as e:
				messagebox.showerror("Lỗi", f"Lỗi gửi file: {str(e)}")
				progress_window.destroy()
		threading.Thread(target=send_file).start()

	except Exception as e:
		messagebox.showerror("Lỗi", f"Lỗi gửi file: {str(e)}")

def open_role_management(root):
	script_path = os.path.abspath("role_functionUI.py")
	subprocess.Popen(["python", script_path], shell=True)

def select_file_encrypt():
	file_path = filedialog.askopenfilename()
	if file_path:
		encrypt(file_path)
		messagebox.showinfo("Thành công", "Mã hóa file thành công!")

def select_folder_encrypt():
	folder_path = filedialog.askdirectory()
	if folder_path:
		encrypt_folder(folder_path)
		messagebox.showinfo("Thành công", "Mã hóa thư mục thành công!")

def select_file_decrypt():
	file_path = filedialog.askopenfilename()
	if file_path:
		key = simpledialog.askstring("Nhập key", "Vui lòng nhập key để giải mã: ")
		if key:
			decrypt_file(file_path, key)

def select_folder_decrypt():
	folder_path = filedialog.askdirectory()
	if folder_path:
		key = simpledialog.askstring("Nhập key", "Vui lòng nhập key để giải mã: ")
		if key:
			decrypt_folder_ui(folder_path, key)

def encrypt_action():
	choice = simpledialog.askstring("Chọn loại mã hóa", "Nhập 'file' để mã hóa file hoặc 'folder' để mã hóa thư mục:")
	if choice == "file":
		select_file_encrypt()
	elif choice == "folder":
		select_folder_encrypt()
	else:
		messagebox.showerror("Lỗi", "Lựa chọn không hợp lệ!")

def decrypt_action():
	choice = simpledialog.askstring("Chọn loại giải mã", "Nhập 'file' để giải mã file hoặc 'folder' để giải mã thư mục:")
	if choice == "file":
		select_file_decrypt()
	elif choice == "folder":
		select_folder_decrypt()
	else:
		messagebox.showerror("Lỗi", "Lựa chọn không hợp lệ!")

def decrypt_file(file_path, key):
	if os.path.exists(file_path) and key:
		try:
			success = decrypt(key, file_path)
			if success:
				messagebox.showinfo("Thành công", "Giải mã file thành công!")
				file_listbox.insert(tk.END, file_path)
			else:
				messagebox.showerror("Lỗi", "Giải mã thất bại! Kiểm tra lại key.")
		except Exception as e:
			messagebox.showerror("Lỗi", f"Giải mã thất bại: {str(e)}")
	else:
		messagebox.showerror("Lỗi", "Vui lòng chọn file và nhập key!")

def decrypt_folder_ui(folder_path, key):
	if os.path.exists(folder_path) and key:
		decrypt_folder(key, folder_path)
		messagebox.showinfo("Thành công", "Giải mã thư mục thành công!")
		for root_dir, _, files in os.walk(folder_path):
			for file in files:
				file_listbox.insert(tk.END, os.path.join(root_dir, file))
	else:
		messagebox.showerror("Lỗi", "Vui lòng chọn thư mục và nhập key!")
def view_user_info():
	user_info = get_user()
	if not user_info:
		messagebox.showerror("Lỗi", "Bạn chưa đăng nhập!")
		return
	
	user_id = user_info.get('user_id')
	username = user_info.get('username')
	role = user_info.get('role')
	department = user_info.get('department')

	info_message = f"ID: {user_id}\nTên: {username}\nVai trò: {role}\nPhòng ban: {department}"
	messagebox.showinfo("Thông tin cá nhân", info_message)
def check_permission_and_execute(action):
	user_info = get_user()
	user_role = user_info.get('role')
	if user_role in ['admin', 'manager']:
		action()
	else:
		messagebox.showerror("Lỗi", "Bạn không có quyền thực hiện hành động này!")
def open_function_ui():
	global file_listbox 
	root = tk.Tk()
	root.title("Hệ Thống Mã Hóa & Giải Mã")
	root.geometry("800x600")
	root.configure(bg="#D9A7A0")

	sidebar = tk.Frame(root, bg="#D9A7A0", width=250, height=600)
	sidebar.pack(side="left", fill="y")
	sidebar.pack_propagate(False)  # 
	def create_button(parent, text, command, bg_color, hover_color="#777777"):
		btn = tk.Button(parent, text=text, command=command, font=("Courier", 14, "bold"),
						bg=bg_color, fg="white", bd=2, relief="ridge",
						highlightthickness=0, padx=15, pady=10, cursor="hand2")
		
		btn.pack(expand=True, fill="both", padx=10, pady=5)
		def on_enter(e):
			btn.config(bg=hover_color)

		def on_leave(e):
			btn.config(bg=bg_color)

		btn.bind("<Enter>", on_enter)
		btn.bind("<Leave>", on_leave)

		return btn
	user_info = get_user()
	user_role = user_info.get('role') if user_info else None

	

	buttons = [
		("📂 Upload File", select_file, "#3F51B5"),  
		("🔒 Mã Hoá", encrypt_action, "#4CAF50"),    
		("🔓 Giải Mã", decrypt_action, "#2196F3"),   
		("👤 User", view_user_info, "#9C27B0")      
	]

	if user_role == "admin":
		buttons.append(("Quản lý User", lambda: open_role_management(root), "#D32F2F"))


	for text, command, color in buttons:
		create_button(sidebar, text, command, color)

	main_frame = tk.Frame(root, bg="#D9A7A0", width=600, height=600)
	main_frame.pack(side="right", expand=True, fill="both")

	notification_label = tk.Label(main_frame, text="", bg="lightgray", font=("Arial", 12))
	notification_label.pack(pady=10, padx=20, fill="x")

	file_list_frame = tk.Frame(main_frame, bg="lightgray", width=500, height=700)
	file_list_frame.pack(pady=10, padx=20, fill="both", expand=True)

	file_listbox = Listbox(file_list_frame, bg="lightgray", font=("Arial", 10))
	file_listbox.pack(padx=10, pady=10, fill="both", expand=True)

	root.mainloop()