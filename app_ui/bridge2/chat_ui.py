import tkinter as tk
from tkinter import scrolledtext, Entry, Button, Frame, Label, PhotoImage
import threading
import os
from datetime import datetime
from PIL import Image, ImageTk 
BG_COLOR = "#FFFFCC"
HEADER_COLOR = "#3498db"
SEND_BTN_COLOR = "#CCFF99"
MESSAGE_BG = "#e8f4fc"
USER_MESSAGE_BG = "#d5f5e3"
ADMIN_HEADER_COLOR = "#e74c3c"
SIDEBAR_BG = "#ffffff"
SELECTED_USER_BG = "#e0e0e0"
class ScrollableFrame(tk.Frame):
	def __init__(self, container, *args, **kwargs):
		super().__init__(container, *args, **kwargs)
		canvas = tk.Canvas(self, bg=BG_COLOR, highlightthickness=0)
		scrollbar = tk.Scrollbar(self, orient="vertical", command=canvas.yview)
		self.scrollable_frame = tk.Frame(canvas, bg=BG_COLOR)

		self.scrollable_frame.bind(
			"<Configure>",
			lambda e: canvas.configure(
				scrollregion=canvas.bbox("all")
			)
		)
		canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
		canvas.configure(yscrollcommand=scrollbar.set)

		canvas.pack(side="left", fill="both", expand=True)
		scrollbar.pack(side="right", fill="y")
class UserFrame(tk.Frame):
	def __init__(self, parent, username, message_preview="", time="2:09 PM", *args, **kwargs):
		super().__init__(parent, *args, **kwargs)
		self.configure(bg=SIDEBAR_BG, padx=5, pady=10, borderwidth=0)
		self.pack(fill=tk.X, pady=1)
		self.profile_frame = Frame(self, bg=SIDEBAR_BG, width=40, height=40)
		self.profile_frame.pack(side=tk.LEFT, padx=(5, 10))
		self.profile_pic = self.create_profile_placeholder(username)
		self.profile_label = Label(self.profile_frame, image=self.profile_pic, bg=SIDEBAR_BG)
		self.profile_label.image = self.profile_pic 
		self.profile_label.pack(fill=tk.BOTH)
		self.info_frame = Frame(self, bg=SIDEBAR_BG)
		self.info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
		self.username_label = Label(
			self.info_frame, 
			text=username, 
			font=("Arial", 10, "bold"), 
			bg=SIDEBAR_BG, 
			anchor=tk.W
		)
		self.username_label.pack(fill=tk.X)
		self.preview_label = Label(
			self.info_frame, 
			text=message_preview, 
			font=("Arial", 9), 
			bg=SIDEBAR_BG, 
			fg="#666666",
			anchor=tk.W
		)
		self.preview_label.pack(fill=tk.X)
		self.time_label = Label(
			self, 
			text=time, 
			font=("Arial", 8), 
			bg=SIDEBAR_BG, 
			fg="#888888"
		)
		self.time_label.pack(side=tk.RIGHT, padx=5)
	
	def create_profile_placeholder(self, username):
		colors = ["#1abc9c", "#2ecc71", "#3498db", "#9b59b6", "#34495e", "#f1c40f", "#e67e22", "#e74c3c"]
		color = colors[sum(ord(c) for c in username) % len(colors)]
		
		img = Image.new('RGB', (40, 40), color=color)
		try:
			from PIL import ImageDraw
			draw = ImageDraw.Draw(img)
			initial = username[0].upper() if username else "U"
			w, h = draw.textsize(initial)
			draw.text((20-w/2, 20-h/2), initial, fill="white")
		except:
			pass
		
		return ImageTk.PhotoImage(img)
		
class ChatApp:
	def __init__(self, root, socket_conn, username, is_admin=False):
		self.root = root
		self.socket = socket_conn
		self.username = username
		self.is_admin = is_admin
		

		self.root.title("Chat Application")
		self.root.geometry("1000x700")
		self.root.minsize(600, 400)

		self.header_frame = Frame(root, bg="blue", height=100)
		self.header_frame.pack(fill=tk.X)
		
		self.user_label = Label(
			self.header_frame, 
			text=f"{'Admin: ' if is_admin else ''}{username}", 
			font=("Arial", 14, "bold"), 
			bg="blue", 
			fg="white",
			pady=10
		)
		self.user_label.pack(side=tk.LEFT, padx=20)
		
		self.status_label = Label(
			self.header_frame,
			text="Connected",
			font=("Arial", 10),
			bg="green",
			fg="white",
			padx=10,
			pady=2,
			borderwidth=1,
			relief="solid"
		)
		self.status_label.pack(side=tk.RIGHT, padx=20)

		self.messages_frame = Frame(root, bg="white")
		self.messages_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
		

		self.input_frame = Frame(root, bg="white", height=60)
		self.input_frame.pack(fill=tk.X, padx=10, pady=10)

		self.message_entry = Entry(self.input_frame, font=("Helvetica", 14), bd=1, relief=tk.GROOVE)
		self.message_entry.insert(0, "Nhập tin nhắn nè...")
		self.message_entry.config(fg="gray")
		self.message_entry.bind("<FocusIn>", self.on_focus_in)
		self.message_entry.bind("<FocusOut>", self.on_focus_out)
		self.message_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
		self.message_entry.bind("<Return>", self.send_message)  
		
		self.send_button = Button(
			self.input_frame, 
			text="Send", 
			command=self.send_message,
			bg="lightblue",
			fg="black",
			font=("Arial", 10, "bold"),
			width=10,
			bd=2,
			padx=10,
			pady=5
		)
		self.send_button.pack(side=tk.RIGHT, padx=10)
		
		self.receive_thread = threading.Thread(target=self.receive_messages)
		self.receive_thread.daemon = True
		self.receive_thread.start()
		
		self.add_system_message("Welcome to the chat! You are connected to the server.")
		self.message_entry.focus()

	def on_focus_in(self, event):
		if self.message_entry.get() == "Nhập tin nhắn...":
			self.message_entry.delete(0, tk.END)
			self.message_entry.config(fg="black")

	def on_focus_out(self, event):
		if not self.message_entry.get().strip():
			self.message_entry.insert(0, "Nhập tin nhắn...")
			self.message_entry.config(fg="gray")

	def add_message(self, username, message, is_self=False):
		message_frame = Frame(
			self.messages_frame, 
			bg="lightgray" if is_self else "white",
			padx=10, 
			pady=5,
			borderwidth=1,
			relief="flat"
		)
		
		if is_self:
			message_frame.pack(anchor=tk.E, fill=tk.X, padx=10, pady=5)
		else:
			message_frame.pack(anchor=tk.W, fill=tk.X, padx=10, pady=5)
		
		username_label = Label(
			message_frame, 
			text=username, 
			font=("Arial", 10, "bold"),
			bg="lightgray" if is_self else "white",
			fg="#333333"
		)
		username_label.pack(anchor=tk.W)
		
		message_label = Label(
			message_frame, 
			text=message, 
			font=("Arial", 11),
			bg="lightgray" if is_self else "white",
			fg="#333333",
			justify=tk.LEFT,
			wraplength=400
		)
		message_label.pack(anchor=tk.W)
		
		time_label = Label(
			message_frame,
			text=datetime.now().strftime("%H:%M"),
			font=("Arial", 8),
			bg="lightgray" if is_self else "white",
			fg="#888888"
		)
		time_label.pack(anchor=tk.E)
		
	def add_system_message(self, message):
		system_frame = Frame(self.messages_frame, bg="#f0f0f0", padx=10, pady=5)
		system_frame.pack(fill=tk.X, pady=5)
		
		system_label = Label(
			system_frame, 
			text=message, 
			font=("Arial", 9, "italic"),
			bg="#f0f0f0",
			fg="#666666"
		)
		system_label.pack()
	
	def send_message(self, event=None):
		message = self.message_entry.get().strip()
		if message:
			msg_to_send = f"{self.username}: {message}"
			try:
				self.socket.send(msg_to_send.encode('utf-8'))
				self.add_message(self.username, message, is_self=True)
				self.message_entry.delete(0, tk.END)
			except Exception as e:
				self.add_system_message(f"Error sending message: {str(e)}")
				self.update_connection_status(False)
	
	def receive_messages(self):
		while True:
			try:
				message = self.socket.recv(2048).decode('utf-8')
				if not message:
					self.add_system_message("Connection to server lost")
					self.update_connection_status(False)
					break
				if ":" in message:
					name, content = message.split(":", 1)
					name, content = name.strip(), content.strip()
					if name != self.username:
						self.root.after(0, lambda: self.add_message(name, content))
				else:
					self.root.after(0, lambda: self.add_system_message(message))
			except Exception as e:
				self.root.after(0, lambda e=e: self.add_system_message(f"Error receiving message: {str(e)}"))
				self.root.after(0, lambda: self.update_connection_status(False))
				break
	
	def update_connection_status(self, is_connected):
		self.status_label.config(text="Connected" if is_connected else "Disconnected", bg="green" if is_connected else "red")
	
	def on_closing(self):
		try:
			self.socket.send(f"{self.username}/exit".encode('utf-8'))
		except:
			pass
		self.root.destroy()
def run_chat_ui_client(socket_conn, username):
	root = tk.Tk()
	app = ChatApp(root, socket_conn, username)
	root.protocol("WM_DELETE_WINDOW", app.on_closing)
	root.mainloop()

def run_chat_ui_admin(socket_conn, username):
	root = tk.Tk()
	app = ChatApp(root, socket_conn, username, is_admin=True)
	root.protocol("WM_DELETE_WINDOW", app.on_closing)
	root.mainloop()

if __name__ == "__main__":
	import socket
	test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	try:
		test_socket.connect((socket.gethostname(), 9999))
		run_chat_ui_client(test_socket, "Test User")
	except Exception as e:
		print(f"Could not connect to server for testing: {e}")