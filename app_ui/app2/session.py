# session.py
current_user = None  # Ban đầu chưa có ai đăng nhập

def set_user(user_id, username, role, department):
    """Lưu thông tin người dùng vào session"""
    global current_user
    current_user = {
        "user_id": user_id,
        "username": username,
        "role": role,
        "department": department
    }

def get_user():
    """Lấy thông tin người dùng, trả về None nếu chưa đăng nhập"""
    return current_user  # Nếu chưa đăng nhập, trả về None

def clear_user():
    """Xóa thông tin người dùng khi đăng xuất"""
    global current_user
    current_user = None
