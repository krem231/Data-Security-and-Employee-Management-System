import tkinter as tk
from tkinter import messagebox
from session import set_user
from functionUI import open_function_ui

def create_login_ui(on_login_attempt):

    
    def handle_login():
        username = entry_username.get()
        password = entry_password.get()

        if not username or not password:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập tên đăng nhập và mật khẩu!")
            return

        user_data = on_login_attempt(username, password, root) 
        
        if user_data:  
            user_id, role, department = user_data
            set_user(user_id, username, role, department)
            messagebox.showinfo("Thành công", "Đăng nhập thành công!")
            switch_to_function_ui()  

    def switch_to_register():
        root.destroy() 
        from regisUI import create_register_ui  
        create_register_ui()  

    def switch_to_function_ui():
        root.destroy()  
        open_function_ui()  

    root = tk.Tk()
    root.title("Login")
    root.geometry("1400x900")  
    root.configure(bg="#D9A7A0")   


    frame = tk.Frame(root, bg="white", width=550, height=700, bd=10, relief="ridge")
    frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
    frame.configure(highlightbackground="#CCCCCC", highlightthickness=2)  

   
    label_title = tk.Label(frame, text="LOGIN", font=("Courier", 36, "bold"), fg="#333", bg="white")
    label_title.pack(pady=30)


    label_username = tk.Label(frame, text="Username", font=("Courier", 16), bg="white", fg="#666")
    label_username.pack()
    entry_username = tk.Entry(frame, width=30, bd=2, relief="solid", font=("Courier", 14))
    entry_username.pack(pady=15)


    label_password = tk.Label(frame, text="Password", font=("Courier", 16), bg="white", fg="#666")
    label_password.pack()
    entry_password = tk.Entry(frame, width=30, bd=2, relief="solid", show="*", font=("Courier", 14))
    entry_password.pack(pady=15)


    remember_var = tk.IntVar()
    checkbox_remember = tk.Checkbutton(frame, text="Remember me", variable=remember_var, bg="white", fg="#666", font=("Courier", 12))
    checkbox_remember.pack(pady=15)


    btn_login = tk.Button(frame, text="LOGIN", font=("Courier", 18, "bold"), bg="#FF6B6B", fg="white",
                          width=20, height=2, relief="flat", command=handle_login)
    btn_login.pack(pady=40)

    btn_register = tk.Button(frame, text="Chưa có tài khoản? Đăng ký ngay!",
                         font=("Courier", 10, "bold"), bg="white", fg="blue", relief="flat",
                         command=lambda: switch_to_register())
    btn_register.pack()
    root.mainloop()
