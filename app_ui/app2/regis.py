import mysql.connector
import secrets
import random
import re
import base64
import time
import json
import hmac
import hashlib
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="11111",
    database="nhan_vien",
)
mycursor = mydb.cursor()

def create_id():
    return str(random.randint(1, 99999))

def base64_encode(data: bytes)->str:
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode()

def create_token(user_id,exp_seconds=15):
    with open("secrets_key.txt","rb") as e:
        key=e.read()

    header = {'alg': 'HS256', 'typ': 'JWT'}
    payload = {
        'user_id': user_id,
        'exp': int(time.time()) + exp_seconds
    }
    header_json = json.dumps(header, separators=(',', ':'), sort_keys=True).encode()
    payload_json = json.dumps(payload, separators=(',', ':'), sort_keys=True).encode()

    header_b64 = base64_encode(header_json)
    payload_b64 = base64_encode(payload_json)

    signature = hmac.new(key, f"{header_b64}.{payload_b64}".encode(), hashlib.sha256).digest()
    signature_b64=base64_encode(signature)

    token = f"{header_b64}.{payload_b64}.{signature_b64}"
    return token

def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_phone_number(phone):
    return len(phone) == 11 and phone.startswith('84') and phone.isdigit()

def register(ho_ten, password, phone, email, phong_ban, vai_tro):
    if not validate_phone_number(phone):
        return False, "Số điện thoại không hợp lệ! Phải có 11 số và bắt đầu bằng '84'."
    if not validate_email(email):
        return False, "Email không hợp lệ!"

    user_id = create_id()
    token = create_token()

    command = "INSERT INTO tt_nv (user_id, ho_ten, phone_number, phong_ban, vai_tro, email, password, token) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
    values = (user_id, ho_ten, phone, phong_ban, vai_tro, email, password, token)

    try:
        mycursor.execute(command, values)
        mydb.commit()
        return True, "Đăng ký thành công!"
    except mysql.connector.Error as err:
        mydb.rollback()
        return False, f"Lỗi đăng ký: {err}"
