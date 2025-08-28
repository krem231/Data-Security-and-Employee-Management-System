from uuid import uuid4
import sys
import logging
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
from email.message import EmailMessage
import mysql.connector

mydb = mysql.connector.connect(
	host="localhost",
	username="root",
	password="12345",
	database="nhan_vien"
)
mycursor = mydb.cursor()
def send_token_to_email():
	try:
		user_id=input("nhập id người cần kt: ")
		command="SELECT email, token from tt_nv where user_id=%s"
		mycursor.execute(command,(user_id,))
		result=mycursor.fetchone()
		if result:
			to_email=result[0]
			token=result[1]
			sender_email =""#nhap mail cua nguoi gui o day
			app_password = '' #nhap mat khau cua nguoi gui o day
			msg = EmailMessage()
			msg['Subject'] = 'Xác thực người dùng'
			msg['From'] = sender_email
			msg['To'] = to_email
			body = f"""
			<html>
			<body>
				<h2>Xin chào</h2>
				<p>Dưới đây là token xác thực của bạn: {token}</p>
				<div style="background-color: #f0f0f0; padding: 10px; margin: 15px 0; border-left: 4px solid #007bff;">
				</div>
				<p>Vui lòng không chia sẻ token này với người khác.</p>
				<hr>
				<p style="font-size: 12px; color: #666;">Đây là email tự động, vui lòng không trả lời email này.</p>
			</body>
			</html>
			"""

			msg.set_content("Vui lòng sử dụng email HTML để xem nội dung.")
			msg.add_alternative(body, subtype='html')

			with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
				server.login(sender_email, app_password)
				server.send_message(msg)
				print(f"Đã gửi token đến email: {to_email}")
				return True
		else:
			print("không tìm thấy người dùng")

	except Exception as e:
		logging.error(f"Lỗi khi gửi email: {str(e)}")
		return False