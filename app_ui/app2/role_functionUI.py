import tkinter as tk
from tkinter import messagebox, simpledialog, Listbox
import mysql.connector
import subprocess
import threading
from role_function import check_token

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="11111",
    database="nhan_vien"
)
mycursor = mydb.cursor()

def check_user(user_id):
    mycursor.execute("SELECT * FROM tt_nv WHERE user_id = %s", (user_id,))
    return mycursor.fetchone()

def update_listbox():
    listbox.delete(0, tk.END)
    mycursor.execute("SELECT user_id, ho_ten, phong_ban ,vai_tro FROM tt_nv")
    for row in mycursor.fetchall():
        listbox.insert(tk.END, f"ID: {row[0]} | Họ tên: {row[1]} |Phòng ban: {row[2]}| Vai trò: {row[3]}")

def assign_role():
    user_id = simpledialog.askstring("Thêm vai trò", "Nhập ID người dùng:")
    if not check_user(user_id):
        messagebox.showerror("Lỗi", "Không tìm thấy ID người dùng")
        return
    role = simpledialog.askstring("Thêm vai trò", "Nhập vai trò (manage, support, finance, employee, admin):")
    if role in ["manage", "support", "finance", "employee", "admin"]:
        mycursor.execute("UPDATE tt_nv SET vai_tro = %s WHERE user_id = %s", (role, user_id))
        mydb.commit()
        messagebox.showinfo("Thành công", f"Đã gán vai trò {role} cho người dùng {user_id}")
        update_listbox()
    else:
        messagebox.showerror("Lỗi", "Vai trò không hợp lệ!")

def delete_user():
    user_id = simpledialog.askstring("Xóa người dùng", "Nhập ID người dùng cần xóa:")
    if check_user(user_id):
        mycursor.execute("DELETE FROM tt_nv WHERE user_id = %s", (user_id,))
        mydb.commit()
        messagebox.showinfo("Thành công", f"Đã xóa người dùng có ID {user_id}")
        update_listbox()
    else:
        messagebox.showerror("Lỗi", "Không tìm thấy ID người dùng")

def delete_role():
    user_id = simpledialog.askstring("Xóa vai trò", "Nhập ID người dùng cần xóa vai trò:")
    if check_user(user_id):
        mycursor.execute("UPDATE tt_nv SET vai_tro = NULL WHERE user_id = %s", (user_id,))
        mydb.commit()
        messagebox.showinfo("Thành công", f"Đã xóa vai trò của người dùng {user_id}")
        update_listbox()
    else:
        messagebox.showerror("Lỗi", "Không tìm thấy ID người dùng")

def check_role():
    role = simpledialog.askstring("Kiểm tra vai trò", "Nhập vai trò cần kiểm tra:")
    mycursor.execute("SELECT * FROM tt_nv WHERE vai_tro = %s", (role,))
    results = mycursor.fetchall()
    if results:
        messagebox.showinfo("Kết quả", f"Có {len(results)} người dùng có vai trò '{role}'")
    else:
        messagebox.showerror("Lỗi", f"Không tìm thấy người dùng nào có vai trò '{role}'")

def check_user_info():
    user_id = simpledialog.askstring("Kiểm tra người dùng", "Nhập ID người dùng:")
    result = check_user(user_id)
    if result:
        messagebox.showinfo("Thông tin", f"Người dùng {user_id} tồn tại trong hệ thống.")
    else:
        messagebox.showerror("Lỗi", "Không tìm thấy ID người dùng")

def run_socket_server():
    def start_server():
        try:
            subprocess.run(["python", "server.py"], check=True)
            root.after(0, lambda: messagebox.showinfo("Thành công", "Socket server đã chạy thành công!"))
        except subprocess.CalledProcessError as e:
            root.after(0, lambda e=e: messagebox.showerror("Lỗi", f"Không thể chạy socket server: {e}"))
    
    threading.Thread(target=start_server, daemon=True).start()

def run_http_server():
    def start_server():
        try:
            subprocess.run(["python", "run_http.py"], check=True)
            root.after(0, lambda: messagebox.showinfo("Thành công", "HTTP server đã chạy thành công!"))
        except subprocess.CalledProcessError as e:
            error_message = f"Không thể chạy HTTP server: {e}"
            root.after(0, lambda: messagebox.showerror("Lỗi", error_message))

    threading.Thread(target=start_server, daemon=True).start()

def verify_token():
    user_id = simpledialog.askstring("Xác thực Token", "Nhập ID người dùng:")
    token = simpledialog.askstring("Xác thực Token", "Nhập Token:")
    if user_id and token:
        result = check_token(user_id, token)
        if result:
            messagebox.showinfo("Thành công", "Token hợp lệ!")
        else:
            messagebox.showerror("Lỗi", "Token không hợp lệ hoặc có lỗi khi xác thực.")
    else:
        messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ ID và Token.")

def open_multi_factor_ui():
    try:
        subprocess.run(["python", "A:Desktop/app_ui/app2/multi_factorUI.py"], check=True)
    except subprocess.CalledProcessError as e:
        error_message = f"Không thể chạy HTTP server: {e}"
        root.after(0, lambda: messagebox.showerror("Lỗi", error_message))

root = tk.Tk()
root.title("Quản lý Người dùng & Vai trò")
root.geometry("600x500")
root.configure(bg="#D9A7A0")

sidebar = tk.Frame(root, bg="#D9A7A0", width=250, height=500)
sidebar.pack(side="left", fill="y")
sidebar.pack_propagate(False)

def create_button(parent, text, command, bg_color, hover_color="#777777"):
    btn = tk.Button(parent, text=text, command=command, font=("Courier", 12, "bold"),
                    bg=bg_color, fg="black", bd=2, relief="ridge",
                    highlightthickness=0, padx=10, pady=5, cursor="hand2")
    btn.pack(expand=True, fill="both", padx=10, pady=5)

    def on_enter(e):
        btn.config(bg=hover_color)

    def on_leave(e):
        btn.config(bg=bg_color)

    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)
    return btn

buttons = [
    ("➕ Thêm vai trò", assign_role, "#3F51B5"),
    ("❌ Xóa người dùng", delete_user, "#D32F2F"),
    ("🚫 Xóa vai trò", delete_role, "#F57C00"),
    ("🔍 Kiểm tra vai trò", check_role, "#4CAF50"),
    ("👤 Kiểm tra thông tin", check_user_info, "#9C27B0"),
    ("⚡ Chạy Socket Server", run_socket_server, "#FF9800"),
    ("⚡ Chạy Http Sever", run_http_server, "#757575"),
    ("🔑 Xác thực Token", verify_token, "#009688"),
    ("🔐 Mutil-Factor UI", open_multi_factor_ui, "#FF5722")
]

for text, command, color in buttons:
    create_button(sidebar, text, command, color)

main_frame = tk.Frame(root, bg="white", width=350, height=500)
main_frame.pack(side="right", expand=True, fill="both")

listbox_frame = tk.Frame(main_frame, bg="lightgray")
listbox_frame.pack(pady=10, padx=20, fill="both", expand=True)

listbox = Listbox(listbox_frame, bg="white", font=("Arial", 10))
listbox.pack(padx=10, pady=10, fill="both", expand=True)

update_listbox()
root.mainloop()