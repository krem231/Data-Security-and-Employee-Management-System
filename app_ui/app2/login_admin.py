import mysql.connector
import requests
import logging
import maskpass

logging.basicConfig(
    filename="logging.txt",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8"
)

mydb = mysql.connector.connect(
    host="localhost",
    username="root",
    password="11111",
    database="nhan_vien"
)
mycursor = mydb.cursor()

def get_public_ip():
    try:
        response = requests.get("https://api64.ipify.org?format=text")
        return response.text.strip()
    except Exception as e:
        logging.error(f"Lỗi khi lấy IP: {e}")
        return None

def get_user_info(username, password):
    command = """
        SELECT user_id, ho_ten, phone_number, phong_ban, vai_tro, email, last_ip
        FROM tt_nv
        WHERE ho_ten = %s AND password = %s
    """
    mycursor.execute(command, (username, password))
    result = mycursor.fetchone()

    if result:
        user_id, ho_ten, phone, phong_ban, vai_tro, email, last_ip = result
        current_ip = get_public_ip()

        if not current_ip:
            logging.warning(f"Không thể lấy IP cho người dùng {ho_ten}")
            return None
        log_message = f"Người dùng {ho_ten} đăng nhập từ IP: {current_ip}"
        if last_ip and last_ip != current_ip:
            log_message += f" (IP trước đó: {last_ip})"
        logging.info(log_message)
        if last_ip != current_ip:
            update_ip_query = "UPDATE tt_nv SET last_ip = %s WHERE user_id = %s"
            mycursor.execute(update_ip_query, (current_ip, user_id))
            mydb.commit()
            logging.info(f"Cập nhật IP mới cho {ho_ten}: {current_ip}")

        return user_id, ho_ten, phone, phong_ban, vai_tro, email, current_ip
    else:
        logging.warning(f"Đăng nhập thất bại với tài khoản: {username}")
        return None
