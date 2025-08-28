import socket
import os
import time
import threading
import sys
import datetime
from tkinter import Tk, filedialog

admin = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
folder = "key"
admin_name = ['hr', 'tech', 'finance', 'employed']
user_name = ""
file_name = ""

def data_name():
    department_file = {
        "role_id": {
            "hr": {
                "job_id": {
                    "personnel": {
                        "danh_sách_nhân_viên.xlsx": ["read", "write"],
                        "bảng_lương.xlsx": ["read", "write"],
                        "danh_sách_chấm_công.xlsx": ["read", "write"],
                        "nghỉ_phép.xlsx": ["read", "write"]
                    },
                    "recruitment": {
                        "đăng_thông_tin_tuyển_dụng.docx": ["read", "write"],
                        "cv_ứng_viên/": ["read"],
                        "lịch_phỏng_vấn.xlsx": ["read", "write"]
                    },
                    "performance": {
                        "bảng_đánh_giá.xlsx": ["read", "write"],
                        "đánh_giá_cả_năm.docx": ["read", "write"]
                    },
                    "policies": {
                        "sổ_tay_nhân_viên.pdf": ["read"],
                        "chính_sách_công_ty.pdf": ["read", "write"],
                        "quy_trình.pdf": ["read", "write"]
                    }
                }
            },
            "tech": {
                "job_id": {
                    "projects": {
                        "project_documentation/": ["read", "write"],
                        "source_code/": ["read", "write"],
                        "technical_specs.docx": ["read", "write"],
                        "deployment_logs.txt": ["read", "write"]
                    },
                    "infrastructure": {
                        "network_configs.yaml": ["read", "write"],
                        "server_logs/": ["read", "write"],
                        "security_policies.pdf": ["read"],
                        "backup_schedules.xlsx": ["read", "write"]
                    },
                    "support": {
                        "incident_reports.xlsx": ["read", "write"],
                        "troubleshooting_guides.pdf": ["read"],
                        "maintenance_logs.xlsx": ["read", "write"]
                    }
                }
            },
            "finance": {
                "job_id": {
                    "budgets": {
                        "ngân_sách_cả_năm.xlsx": ["read", "write"],
                        "báo_cáo_ngân_sách.xlsx": ["read", "write"],
                        "ngân_sách_các_phòng_ban.xlsx": ["read", "write"]
                    },
                    "transactions": {
                        "giao_dịch/": ["read", "write"],
                        "hóa_đơn/": ["read"],
                        "lịch_sử_giao_dịch.xlsx": ["read"]
                    },
                    "reports": {
                        "báo_cáo_tài_chính.xlsx": ["read", "write"],
                        "thuế.pdf": ["read", "write"],
                        "kiểm_toán.pdf": ["read", "write"]
                    },
                    "payroll": {
                        "lương.xlsx": ["read", "write"],
                        "tính_thuế.xlsx": ["read", "write"],
                        "tăng_ca.xlsx": ["read", "write"]
                    }
                }
            }
        }
    }
    cross_access = {
        "role_id": {
            "hr": {
                "tech/security_policies.pdf": ["read"],
                "finance/ngân_sách_các_phòng_ban.xlsx": ["read"],
                "finance/lương.xlsx": ["read"] 
            },
            "tech": {
                "finance/ngân_sách_các_phòng_ban.xlsx": ["read"],
                "finance/lương.xlsx": ["read"],
                "hr/sổ_tay_nhân_viên.pdf": ["read"],
                "hr/chính_sách_công_ty.pdf": ["read"],
                "hr/quy_trình.pdf": ["read"]
            },      
            "finance": {
                "hr/sổ_tay_nhân_viên.pdf": ["read"],
                "hr/chính_sách_công_ty.pdf": ["read"],
                "hr/quy_trình.pdf": ["read"],
                "tech/security_policies.pdf": ["read"]
            }
        }
    }
    file_permissions = set()
    for role in department_file["role_id"]:
        for category in department_file["role_id"][role]["job_id"]:
            for file in department_file["role_id"][role]["job_id"][category]:
                file_permissions.add(file)
    
    return department_file, file_permissions
_, file_perm = data_name()

def openfile():
    root = Tk()
    root.withdraw()
    file = filedialog.askopenfile(title="select file", filetypes=[
        ('pdf file', '*.pdf*'),
        ('python file', '*.py'),
        ('word file', ('*.docx', '*.doc')),
        ('excel file', ('*.csv', '*.xls')),
        ('jpg file', '*.jpg'),
        ('all file', '*.*')
    ])
    if file:
        print("file da chon: ", file.name)
        file_path = file.name
        file.close()
        return file_path
    return None

def send_data(client):
    try:
        while True:
            file_path = openfile()
            if not file_path:
                print("Không có file nào được chọn")
                break
                
            data_user_name = os.path.basename(file_path)
            if data_user_name in file_perm:
                if os.path.getsize(file_path) < data_size:
                    file_send = f"{data_user_name}:file"

                    client.send(file_send.encode('utf-8'))
                    with open(file_path, "rb") as f:
                        data = f.read()
                        client.send(data)

                    response = client.recv(2048).decode('utf-8')
                    print("Server:", response)
                    break
                else:
                    print("Kích thước dữ liệu không được quá 20mb!")
            else:
                print("dữ liệu không hợp lệ")

    except Exception as e:
        print(f"Có lỗi trong việc gửi dữ liệu: {str(e)}")

def receive_data(client):
    try:
        while True:
            data_recv = client.recv(data_size)
            if not data_recv:
                break
            print("dữ liệu đã nhận được: ", data_recv.decode('utf-8'))
    except Exception as e:
        current_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"có lỗi trong việc nhận dữ liệu! time: {current_date}", file=sys.stderr)

def send_recv_mess(client, user_name):
    try:
        def receive_messages():
            while True:
                try:
                    message = client.recv(2048).decode('utf-8')
                    if not message:
                        print("\nMất kết nối tới server")
                        break
                    print(message)
                except:
                    print("\nMất kết nối tới server")
                    break
        
        receive_thread = threading.Thread(target=receive_messages)
        receive_thread.daemon = True
        receive_thread.start()
        print("Nhập 'exit' để thoát hoặc nhấn Ctrl+C")
        while True:
            try:
                message = input()
                if message.lower() == 'exit':
                    client.send(f"{user_name}/exit".encode('utf-8'))
                    break
                if message.lower() == 'sendkey':
                    msg=f"/send_key"
                    client.send(bytes(msg, 'utf-8'))
                if message.lower().startswith("/send_data"):
                    send_data(client)
                if message:
                    msg_send = f"{user_name}: {message}"
                    client.send(msg_send.encode('utf-8'))
            except KeyboardInterrupt:
                print("\nĐang thoát...")
                client.send(f"{user_name}/exit".encode('utf-8'))
                break
                
    except Exception as e:
        print(f"Lỗi gửi/nhận tin nhắn: {str(e)}")

def main():
    host = socket.gethostname()
    port = 9999
    data_size = 20000
    admin.connect((host, port))
    server_res = admin.recv(1024)
    print("response:", server_res.decode('utf-8'))
    global user_name
    user_name = input("Nhập tên phòng ban mà bạn quản lý tại đây: ")
    if user_name in admin_name:
        full_name = user_name + " manager"
        admin.send(full_name.encode('utf-8'))
        send_recv_mess(admin, full_name)
    else:
        print("Phòng ban không hợp lệ!")

try:
    main()
except Exception as e:
    print(f"Không thể kết nối tới server: {str(e)}")