import tkinter as tk
from tkinter import messagebox
import mysql.connector
import smtplib
from email.message import EmailMessage

def send_token(user_id):
    try:
        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            password="12345",
            database="nhan_vien"
        )
        mycursor = mydb.cursor()
        command = "SELECT email, token FROM tt_nv WHERE user_id=%s"
        mycursor.execute(command, (user_id,))
        result = mycursor.fetchone()
        
        if result:
            to_email, token = result
            sender_email = "" #doi gmail
            app_password = "" #app password
            msg = EmailMessage()
            msg['Subject'] = 'Xác thực người dùng'
            msg['From'] = sender_email
            msg['To'] = to_email
            msg.set_content(f"Token của bạn: {token}")
            msg.add_alternative(f"""
            <html>
            <body>
                <h2>Xin chào</h2>
                <p>Dưới đây là token xác thực của bạn: {token}</p>
                <p>Vui lòng không chia sẻ token này với người khác.</p>
            </body>
            </html>
            """, subtype='html')
            
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(sender_email, app_password)
                server.send_message(msg)
                messagebox.showinfo("Thành công", f"Đã gửi token đến {to_email}")
        else:
            messagebox.showwarning("Lỗi", "Không tìm thấy người dùng")
    
    except Exception as e:
        messagebox.showerror("Lỗi", f"Lỗi khi gửi email: {str(e)}")

def create_ui():
    root = tk.Tk()
    root.title("Gửi Token qua Email")
    root.geometry("350x200")
    
    tk.Label(root, text="Nhập ID người dùng:").pack(pady=5)
    user_id_entry = tk.Entry(root)
    user_id_entry.pack(pady=5)
    
    send_button = tk.Button(root, text="Gửi Token", command=lambda: send_token(user_id_entry.get()))
    send_button.pack(pady=10)
    
    root.mainloop()

if __name__ == "__main__":
    create_ui()
    