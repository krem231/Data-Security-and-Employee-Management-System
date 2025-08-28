import sys
import os
import threading
import signal
import time
import logging
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, 'bridge2'))
from http.server import HTTPServer
from http_server import NeutralHTTP, host as http_host, port as http_port

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("combined_server.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

running = True
server_threads = []

def run_http_server():
    try:
        http_server = HTTPServer((http_host, http_port), NeutralHTTP)
        logger.info(f"HTTP Server đang chạy tại http://{http_host}:{http_port}")
        
        while running:
            http_server.handle_request()
            time.sleep(0.1)  
            
        http_server.server_close()
        logger.info("HTTP Server đã dừng")
    except Exception as e:
        logger.error(f"Lỗi HTTP Server: {str(e)}")

def combined_signal_handler(sig, frame):
    global running
    logger.info("\nĐang đóng tất cả các server...")
    running = False

    for thread in server_threads:
        if thread.is_alive():
            thread.join(timeout=5)
    
    logger.info("Tất cả các server đã dừng.")
    sys.exit(0)

def main():
    signal.signal(signal.SIGINT, combined_signal_handler)

    print("=== Server quản lý đã khởi động ===")
    print("Đang khởi động các server con...")
    
    http_thread = threading.Thread(target=run_http_server, daemon=True)
    http_thread.start()
    server_threads.append(http_thread)
    
    
    print("Tất cả các server đã được khởi động thành công!")
    print("Nhấn Ctrl+C để thoát tất cả các server")
    try:
        while running:
            time.sleep(1)
    except KeyboardInterrupt:
        combined_signal_handler(signal.SIGINT, None)


if __name__ == "__main__":
    main()