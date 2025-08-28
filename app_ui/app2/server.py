import sys
import os
import threading
import signal
import time
import logging

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, 'bridge2'))

from socket_server import server as socket_server, signal_handler as socket_signal_handler

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


def run_socket_server():
	"""Chạy Socket server trong thread riêng"""
	try:
		logger.info(f"Socket Server đang chạy")
		from socket_server import listen
		listen(socket_server)
	except Exception as e:
		logger.error(f"Lỗi Socket Server: {str(e)}")

def combined_signal_handler(sig, frame):
	global running
	logger.info("\nĐang đóng tất cả các server...")
	running = False
	socket_signal_handler(sig, frame)
	for thread in server_threads:
		if thread.is_alive():
			thread.join(timeout=5)
	
	logger.info("Tất cả các server đã dừng.")
	sys.exit(0)

def main():
	signal.signal(signal.SIGINT, combined_signal_handler)

	print("=== Server quản lý đã khởi động ===")
	print("Đang khởi động các server con...")
	
	socket_thread = threading.Thread(target=run_socket_server, daemon=True)
	socket_thread.start()
	server_threads.append(socket_thread)
	
	print("Tất cả các server đã được khởi động thành công!")
	print("Nhấn Ctrl+C để thoát tất cả các server")
	

	try:
		while running:
			time.sleep(1)
	except KeyboardInterrupt:
		combined_signal_handler(signal.SIGINT, None)

if __name__ == "__main__":
	main()