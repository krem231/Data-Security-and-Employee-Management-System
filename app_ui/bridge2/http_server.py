from http.server import HTTPServer, BaseHTTPRequestHandler 
import time
from datetime import datetime, timedelta
import sys
import os
import logging
from urllib.parse import parse_qs
import cgi
from werkzeug.utils import secure_filename
import shutil 
import threading
host = "192.168.0.30" 
port = 9999
upload_path = 'upload'
original_filenames = {}
current_date = time.strftime("%Y-%m-%d %H-%M-%S")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
if not os.path.exists(upload_path):
	os.makedirs(upload_path)
User = {
	"user1": {"role": "hr"},
	"user2": {"role": "tech"},
	"user3": {"role": "account"},
	"user4": {"role": "employed"}
}

def take_backup(src_file_name, dst_file_name=None, src_dir='', dst_dir=''): 
	try: 
		today = datetime.today()   
		date_format = today.strftime("%d_%b_%Y_") 
		
		try: 
			if src_file_name and dst_file_name and src_dir and dst_dir: 
				full_src_path = os.path.join(src_dir, src_file_name)
				full_dst_path = os.path.join(dst_dir, dst_file_name)
			elif dst_file_name is None or not dst_file_name: 
				dst_file_name = src_file_name 
				full_src_path = os.path.join(src_dir, src_file_name)
				full_dst_path = os.path.join(dst_dir, date_format + dst_file_name)
			elif dst_file_name.isspace(): 
				dst_file_name = src_file_name 
				full_src_path = os.path.join(src_dir, src_file_name)
				full_dst_path = os.path.join(dst_dir, date_format + dst_file_name)
			else: 
				full_src_path = os.path.join(src_dir, src_file_name)
				full_dst_path = os.path.join(dst_dir, date_format + dst_file_name)
				
			shutil.copy2(full_src_path, full_dst_path) 
			print("Backup Successful!") 
			return True
		except FileNotFoundError: 
			print("File does not exist! Please provide the complete path") 
			return False
	except PermissionError:   
		try:
			dst_dir_path = os.path.join(dst_dir, date_format + dst_file_name)
			shutil.copytree(src_file_name, dst_dir_path)
			return True
		except Exception as e:
			print(f"Permission error during backup: {str(e)}")
			return False
	except Exception as e:
		print(f"Error during backup: {str(e)}")
		return False

def permission(user_id, req_role):
	if user_id not in User:
		logger.warning("User not valid!")
		return False
	return User[user_id]["role"] == req_role

def get_file_list():
	upload_files = []
	for file_name in os.listdir(upload_path):
		file_path = os.path.join(upload_path, file_name)
		file_stat = os.stat(file_path)
		upload_files.append({
			"name": file_name,
			"path": file_path,
			"size": file_stat.st_size,
			"status": file_stat,
			"create": time.ctime(file_stat.st_ctime)  
		})
	return upload_files

def back_up_data(upload_files):
	set_time = timedelta(days=5)
	current_time = datetime.now()
	new_time = current_time + set_time
	result = []
	if new_time:
		for file in upload_files:
			take_backup(file)
	result = get_file_list()
	return result
def auto_backup():
	files = get_file_list()
	for file in files:
		back_up_data(file)
		threading.Timer(432000, auto_backup).start()
def generate_file_table(files):
	rows = ""
	for file in files:
		rows += f"""<tr>
			<td>{file['name']}</td>
			<td>{file['size']} bytes</td>
			<td>{file['create']}</td>
			<td><a href="/download?file={file['name']}">Download</a></td>
		</tr>"""
	return rows

class NeutralHTTP(BaseHTTPRequestHandler):
	def do_GET(self):
		if self.path == '/':
			self.send_response(200)
			self.send_header("content-type", "text/html")
			self.end_headers()
			
			files = get_file_list() 
			file_rows = generate_file_table(files)
			
			html = f'''
			<html>
			<body>
				<h1>File Upload</h1>
				<div class="upload-form">
					<form action="/upload" method="post" enctype="multipart/form-data">
						<input type="file" name="file" required>
						<input type="submit" value="Upload" class="submit-btn">
					</form>
				</div>
				<h2>Uploaded Files</h2>
				<table>
					<thead>
						<tr>
							<th>Filename</th>
							<th>Size</th>
							<th>Upload Date</th>
							<th>Action</th>
						</tr>
					</thead>
					<tbody>
						{file_rows}
					</tbody>
				</table>
			</body>
			</html>
			'''
			self.wfile.write(bytes(html, "utf-8"))
		
		elif self.path.startswith('/download'):
			try:
				if '?' in self.path:
					path_parts = self.path.split('?', 1)
					params = parse_qs(path_parts[1])
					file_name = params.get('file', [''])[0]
					
					if not file_name:
						self.send_error(400, "Missing file parameter")
						return
					file_path = os.path.join(upload_path, file_name)
					if os.path.exists(file_path) and os.path.isfile(file_path):
						original_name = original_filenames.get(file_name, file_name)
						self.send_response(200)
						self.send_header('Content-Type', 'application/octet-stream')
						self.send_header('Content-Disposition', f'attachment; filename="{original_name}"')
						self.end_headers()
						
						with open(file_path, 'rb') as f:
							self.wfile.write(f.read())
					else:
						self.send_error(404, "File not found")
				else:
					self.send_error(400, "Invalid request format")
			except Exception as e:
				logger.error(f"Download error: {str(e)}")
				self.send_error(500, str(e))
		else:
			self.send_error(404, "Path not found")
	
	def do_POST(self):
		if self.path == "/upload":
			try:
				content_length = int(self.headers['Content-Length'])
				if content_length > 20000000:
					self.send_response(413)
					self.send_header("Content-type", "text/html")
					self.end_headers()
					self.wfile.write(bytes("<html><body><h1>Error 413: File too large</h1></body></html>", "utf-8"))
					read_bytes = 0
					while read_bytes < content_length:
						read_bytes += len(self.rfile.read(min(65536, content_length - read_bytes)))
					return
				
				form = cgi.FieldStorage(
					fp=self.rfile,
					headers=self.headers,
					environ={'REQUEST_METHOD': 'POST',
							'CONTENT_TYPE': self.headers['Content-Type']}
				)
				
				if 'file' in form:
					file_item = form['file']
					if file_item.filename:
						filename = secure_filename(file_item.filename)
						file_path = os.path.join(upload_path, filename)
						with open(file_path, 'wb') as f:
							f.write(file_item.file.read())
						logger.info(f"File {filename} uploaded successfully")
						self.send_response(200)
						self.end_headers()
						self.wfile.write(b"File uploaded successfully")
					else:
						self.send_response(400)
						self.end_headers()
						self.wfile.write(b"Error: No file selected")
				else:
					logger.warning("File field missing in form")
					self.send_response(400)
					self.send_header("Content-type", "text/html")
					self.end_headers()
					self.wfile.write(bytes("<html><body><h1>Error: File field missing</h1></body></html>", "utf-8"))
			
			except Exception as e:
				logger.error(f"Upload error: {str(e)}")
				self.send_error(500, str(e))
		else:
			self.send_error(404, "Path not found")
server = HTTPServer((host, port), NeutralHTTP)
try:
	server.serve_forever()
except KeyboardInterrupt:
	server.server_close()
	print("Server has been stopped")