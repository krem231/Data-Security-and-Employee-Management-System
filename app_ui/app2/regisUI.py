import tkinter as tk
from tkinter import messagebox
from regis import register
import re

def handle_register(entry_name, entry_password, entry_phone, entry_email, entry_department, entry_role, root):
    ho_ten = entry_name.get().strip()
    password = entry_password.get().strip()
    phone = entry_phone.get().strip()
    email = entry_email.get().strip()
    phong_ban = entry_department.get().strip()
    vai_tro = entry_role.get().strip()

    if not ho_ten or not password or not phone or not email or not phong_ban or not vai_tro:
        messagebox.showwarning("Cảnh báo", "Vui lòng nhập đầy đủ thông tin!")
        return
    success, message = register(ho_ten, password, phone, email, phong_ban, vai_tro)

    if success:
        messagebox.showinfo("Thành công", message)
    else:
        messagebox.showerror("Lỗi", message)

def switch_to_login(root, on_login_attempt):
    root.destroy() 
    from loginUI import create_login_ui 
def switch_to_login(root, on_login_attempt):
    root.destroy() 
    from loginUI import create_login_ui  
    create_login_ui(lambda u, p: on_login_attempt(u, p))  
def create_register_ui():
    root = tk.Tk()
    root.title("Đăng ký tài khoản")
    root.geometry("1400x900")
    root.configure(bg="#D9A7A0")


    frame = tk.Frame(root, bg="white", width=600, height=750, bd=10, relief="ridge")
    frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
    frame.configure(highlightbackground="#CCCCCC", highlightthickness=2)


    tk.Label(frame, text="REGISTER", font=("Courier", 36, "bold"), fg="#333", bg="white").pack(pady=20)


    fields = [
        ("Họ và Tên", "entry_name"),
        ("Mật khẩu", "entry_password"),
        ("Số điện thoại", "entry_phone"),
        ("Email", "entry_email"),
        ("Phòng ban", "entry_department"),
    ]

    entries = {}
    for label, var_name in fields:
        tk.Label(frame, text=label, font=("Courier", 16), bg="white", fg="#666").pack()
        entry = tk.Entry(frame, width=30, bd=2, relief="solid", font=("Courier", 14))
        if var_name == "entry_password":
            entry.config(show="*")  # Ẩn mật khẩu
        entry.pack(pady=10)
        entries[var_name] = entry


    btn_register = tk.Button(
        frame, text="REGISTER", font=("Courier", 18, "bold"),
        bg="#FF6B6B", fg="white", width=20, height=2, relief="flat",
        command=lambda: handle_register(
            entries["entry_name"], entries["entry_password"],
            entries["entry_phone"], entries["entry_email"],
            entries["entry_department"], entries["entry_role"], root
        )
    )
    btn_register.pack(pady=30)

    btn_switch_login = tk.Button(
    frame, text="Quay lại đăng nhập",
    font=("Courier", 10, "bold"),
    bg="white", fg="red", relief="flat",
    command=lambda: switch_to_login(root, lambda u, p: print(f"Đăng nhập với {u}, {p}"))  
    )   
    btn_switch_login.pack()

    root.mainloop()