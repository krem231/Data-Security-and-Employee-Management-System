import os
import base64
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad
from Crypto.Util.Padding import unpad
import platform
from tkinter import Tk
from tkinter import filedialog

#mở file
def openfile():
    Tk().withdraw()
    file=filedialog.askopenfile(title="select file",filetypes=[
        ('pdf file','*.pdf*'),
        ('python file','*.py'),
        ('word file',('*.docx', '*.doc')),
        ('excel file',('*.csv','*.xls')),
        ('jpg file','*.jpg'),
        ('all file', '*.*')
        ]
    )
    file_extension = os.path.splitext(file.name)[1].lower()
    while 1:        
        print("file da chon: ", file.name)
        file.close()
        break


    return file.name 

#mở folder
def open_direc():
    root=Tk()
    root.withdraw()
    path=filedialog.askdirectory()
    return path
#tạo key filde
def key_gen(file):
    key = os.urandom(16)
    hex_key=key.hex().upper()
    formatted_key="-".join(hex_key[i:i+8] for i in range(0,len(hex_key),8))
    folder = "key"
    if not os.path.exists(folder):
        os.mkdir(folder)
        
    file_name = os.path.splitext(os.path.basename(file))[0]
    
    user_folder = os.path.join(folder,f"{file_name}_key.txt")
    try:
        with open(user_folder, "w", encoding='utf-8') as ko:
            ko.write(f"key: {formatted_key}\n")
            print(f"dia chi luu key: {user_folder}")
    except Exception as e:
        print(f"loi tao key")
    
    return key
#tạo key folder
def key_folder(folder):
    i=0
    key=os.urandom(16)
    hex_key=key.hex().upper()
    format_key="-".join(hex_key[i:i+8] for i in range(0,len(hex_key),8))
    key_folder="key"
    check=os.path.exists(key_folder)
    folder_name = os.path.basename(folder)
    key_file = os.path.join(key_folder, f"{folder_name}_key.txt")
    if not check:
        os.mkdir(key_folder)
    else:
        with open(key_file,"w") as op:
            op.write(f"folder key {i+1}: {format_key}")
    return key

#tiến hành mã hóa file
def encrypt(file):
    key=key_gen(file)
    with open(file,"rb") as re:
        file_data=re.read()
    cipher=AES.new(key,AES.MODE_CBC)
    try:
        iv=cipher.iv
        ct=cipher.encrypt(pad(file_data,AES.block_size))
        with open(file,"w") as te:
            te.write(base64.b64encode(ct+iv).decode('utf-8'))
            print("ma hoa thanh cong!")
    except Exception as e:
        print("loi ma hoa")

#tiến hành giải mã file
def decrypt(key,filed):
    try:
        file_path = filed
        with open(file_path,"rb") as re:
            read_file= base64.b64decode(re.read())
        def proces_key(str_key):
            clean_key=str_key.replace("-","")
            return bytes.fromhex(clean_key)
        m=proces_key(key)
        iv=read_file[-16:]
        ct=read_file[:-16]
        cipher=AES.new(m,AES.MODE_CBC,iv)
           
        ct_de=unpad(cipher.decrypt(ct),AES.block_size)  
        with open(file_path,"wb") as re2:
            re2.write(ct_de)
            print(" giai ma hoa thanh cong")
            return True
    except ValueError as ve:
        print(f"Lỗi định dạng key: {str(ve)}")
        return False
    except Exception as e:
        print(f"Lỗi giải mã: {str(e)}")
        return False
#mã hóa folder
def encrypt_folder(folder):
    key=key_folder(folder)
    for root,dirs,files in os.walk(folder):
        for file in files:
            file_path = os.path.join(root, file)
            with open(file_path ,"rb") as r:
                data=r.read()
            
            cipher=AES.new(key,AES.MODE_CBC)
            try: 
                iv=cipher.iv 
                ct=cipher.encrypt(pad(data,AES.block_size))
                with open(file_path,"wb") as en:
                    en.write(base64.b64encode(ct+iv))
                    
                print("ma hoa thanh cong")
            except Exception as e:
                print("loi ma hoa folder")
# giải mã hóa folder
def decrypt_folder(key,folder):
    for root,dirs,files in os.walk(folder):
        for file in files:
            file_path = os.path.join(root, file)
            with open(file_path,"rb") as re:
                read_file= base64.b64decode(re.read())
            def proces_key(str_key):
                clean_key=str_key.replace("-","")
                return bytes.fromhex(clean_key)
            m=proces_key(key)
            iv=read_file[-16:]
            ct=read_file[:-16]
            cipher=AES.new(m,AES.MODE_CBC,iv)
            ct_de=unpad(cipher.decrypt(ct),AES.block_size)
            with open(file_path,"wb") as re2:
                    re2.write(ct_de)
            print("giai ma hoa thanh cong")
