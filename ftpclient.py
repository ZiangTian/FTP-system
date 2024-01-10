import tkinter as tk
from tkinter import scrolledtext
from tkinter import messagebox
from tkinter import filedialog
import socket
import os
import re
import time

# 创建数据socket，用于传输数据
def create_data_socket(data_address):
    """
    创建数据socket并连接到指定地址

    输入data_address, 元组类型, (IP地址, 端口号)
    返回数据socket
    """
    data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    data_socket.connect(data_address)
    return data_socket

# 发送命令的接口
def send_command(control_socket, command):
    """
    输入控制socket和命令
    发送命令并返回服务器响应串
    """
    time.sleep(0.1)
    control_socket.sendall(command.encode('utf-8'))
    time.sleep(0.5)
    response = control_socket.recv(4096)
    time.sleep(0.1)
    return response

# 解析PASV响应，提取主机和端口信息
def parse_pasv_response(response):
    """
    建立PASV FTP数据传输模式，输入FTP服务器返回的PASV响应，
    对PASV使用正则表达式搜索，提取PASV响应中的主机和端口信息，用于建立数据连接
    """
    response_str = response.decode('utf-8')
    match = re.search(r'(\d+),(\d+),(\d+),(\d+),(\d+),(\d+)', response_str)
    if match:
        host = '.'.join(match.group(1, 2, 3, 4))
        port = int(match.group(5)) * 256 + int(match.group(6))
        return host, port
    return None

# 图形化界面实现，整合了FTP服务端功能
class FTPClientGUI:
    def __init__(self, master):
        self.master = master # Tkinter的根窗口
        self.master.title("FTP Client")
        self.create_widgets() # 创建图形化界面的组件
    
    # 登录FTP服务器的函数
    def login_ftp(self):
        """

        登录FTP服务器，prompt用户输入FTP服务器的IP地址和端口号，用户名和密码
        """

        host = tk.simpledialog.askstring("Input", "Enter host:") # '10.128.22.12' 
        port = tk.simpledialog.askinteger("Input", "Enter port:") # 21
        username = tk.simpledialog.askstring("Input", "Enter username:") # FtpUsr
        password = tk.simpledialog.askstring("Input", "Enter password:")  # 654321

        ## uncomment for quick debugging
        # host = '10.128.22.12' 
        # port = 21
        # username = 'FtpUsr'
        # password = '654321'

        self.control_socket = self.ftp_connect(host, port)

        if self.control_socket:
            send_command(self.control_socket, 'USER {}\r\n'.format(username))
            response = send_command(self.control_socket, 'PASS {}\r\n'.format(password))
            if response.decode('utf-8').startswith('530'):
                self.text_area.insert(tk.END, "Login failed. Please check your credentials.\n")
                # self.control_socket.close()
            else:
                self.text_area.insert(tk.END, "Login successful. Connected to FTP server.\n")
                self.upload_button["state"] = tk.NORMAL
                self.download_button["state"] = tk.NORMAL
        else:
            self.text_area.insert(tk.END, "Login failed. Please check your credentials.\n")

    # 用于连接FTP服务器的函数
    def ftp_connect(self, host, port):
        """

        输入ftp服务器的ip和端口号
        创建ftp连接，返回控制socket
        """
        try:
            control_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            control_socket.connect((host, port))
            response = control_socket.recv(4096)
            self.text_area.insert(tk.END, f"{response.decode('utf-8')}\n")
            return control_socket
        except Exception as e:
            self.text_area.insert(tk.END, f"Error connecting to FTP server: {e}\n")
            return None
    
    # 创建图形化界面的组件
    def create_widgets(self):
        self.text_area = scrolledtext.ScrolledText(self.master, wrap=tk.WORD, width=80, height=40)
        self.text_area.pack(padx=10, pady=10)

        self.login_button = tk.Button(self.master, text="Login", command=self.login_ftp)
        self.login_button.pack(pady=5)

        self.list_button = tk.Button(self.master, text="List Files", command=self.list_files)
        self.list_button.pack(pady=5)

        self.upload_button = tk.Button(self.master, text="Upload File", command=self.upload_file_re)
        self.upload_button.pack(pady=5)

        # self.download_button = tk.Button(self.master, text="Download File", command=self.download_file)
        # self.download_button.pack(pady=5)

        self.download_button = tk.Button(self.master, text="Download File", command=self.download_file_re)
        self.download_button.pack(pady=5)

        self.quit_button = tk.Button(self.master, text="Quit", command=self.master.destroy)
        self.quit_button.pack(pady=5)


        self.text_area.insert(tk.END, "Welcome to FTP server. This is the group work for WHU computer network lab.\n")

    # 列出FTP服务器上的文件
    def list_files(self):
        """

        打印出在服务器当前目录下的文件和目录
        自行创建数据连接，发送LIST命令，接收服务器返回的数据
        """
        pasv_response = send_command(self.control_socket, 'PASV\r\n')
        data_address = parse_pasv_response(pasv_response)

        if data_address:
            data_socket = create_data_socket(data_address)
            send_command(self.control_socket, 'LIST\r\n')

            received_data = b''
            while True:
                data = data_socket.recv(4096)
                if not data:
                    break
                received_data += data

            file_encoding = 'utf-8' 
            decoded_data = received_data.decode(file_encoding)

            self.text_area.insert(tk.END, f"File Listing:\n{decoded_data}\n")

            data_socket.close()
        else:
            self.text_area.insert(tk.END, "Error parsing PASV response\n")
    
    # 上传文件
    def upload_file(self):
        """
        上传文件到FTP服务器(不带断点重传)

        自行创建数据连接，发送STOR命令
        """
        try: 
            if self.control_socket:
                local_filename = filedialog.askopenfilename(title="Select Local File")
                if local_filename:
                    # Extract the filename from the full path
                    file_name = os.path.basename(local_filename)

                    # Get the data address for the data connection
                    time.sleep(0.2)
                    pasv_response = send_command(self.control_socket, 'PASV\r\n')
                    data_address = parse_pasv_response(pasv_response)
                    print(pasv_response)
                    print(data_address)

                    if data_address:
                        # Create a data socket and connect to the specified address
                        data_socket = create_data_socket(data_address)

                        # Send the STOR command with the remote filename
                        send_command(self.control_socket, f"STOR {file_name}\r\n")

                        # Open the local file for reading
                        with open(local_filename, 'rb') as local_file:
                            # Send the file data to the server
                            data = local_file.read(4096)
                            while data:
                                data_socket.sendall(data)
                                data = local_file.read(4096)

                        # Close the data socket to signal the end of file upload
                        data_socket.close()

                        # Wait for the server response after upload
                        response = self.control_socket.recv(4096)
                        self.text_area.insert(tk.END, response.decode('utf-8') + "\n")

                    else:
                        self.text_area.insert(tk.END, "Error parsing PASV response\n")
                else:
                    self.text_area.insert(tk.END, "Please select a local file.\n")
            else:
                self.text_area.insert(tk.END, "Not connected to FTP server. Please connect first.\n")
        except Exception as e:
            self.text_area.insert(tk.END, f"Error uploading file: {e}\n")

    # 断点重传 上传文件
    def upload_file_re(self):
        """
        上传文件到FTP服务器(带断点重传)

        自行创建数据连接
        检测服务器是否有待传输文件，有则发送REST指令
        发送STOR命令进行传输
        """
        try:
            if self.control_socket:
                local_filename = filedialog.askopenfilename(title="Select Local File")
                if local_filename:
                    # Extract the filename from the full path
                    file_name = os.path.basename(local_filename)

                    # Get the data address for the data connection
                    time.sleep(0.2)
                    pasv_response = send_command(self.control_socket,'PASV\r\n')
                    data_address = parse_pasv_response(pasv_response)

                    if data_address:
                        # Create a data socket and connect to the specified address
                        data_socket = create_data_socket(data_address)

                        # Check if the remote file exists and get its size
                        remote_file_size = 0
                        response = send_command(self.control_socket, f"SIZE {file_name}\r\n")
                        if response.startswith(b"213"):
                            remote_file_size = int(response.split()[1])
                            # Send REST command to resume upload
                            send_command(self.control_socket, f"REST {remote_file_size}\r\n")

                        # Send the STOR command with the remote filename
                        send_command(self.control_socket, f"STOR {file_name}\r\n")

                        # Open the local file for reading
                        with open(local_filename, 'rb') as local_file:
                            # Send the file data to the server
                            data = local_file.read(4096)
                            while data:
                                data_socket.sendall(data)
                                data = local_file.read(4096)
                        
                        self.text_area.insert(tk.END, f"Uploaded {local_filename} with resume support.\n")
                        self.text_area.insert(tk.END, f"Total bytes uploaded this time: {os.path.getsize(local_filename)-remote_file_size}\n")

                        # Close the data socket to signal the end of file upload
                        data_socket.close()
                        

                        # Wait for the server response after upload
                        response = self.control_socket.recv(4096)
                        self.text_area.insert(tk.END, response.decode('utf-8') + "\n")

                    else:
                        self.text_area.insert(tk.END, "Error parsing PASV response\n")
                else:
                    self.text_area.insert(tk.END, "Please select a local file.\n")
            else:
                self.text_area.insert(tk.END, "Not connected to FTP server. Please connect first.\n")
        except Exception as e:
            self.text_area.insert(tk.END, f"Error uploading file: {e}\n")

    # 下载文件
    def download_file(self):
        """
        从服务器下载文件，
        prompt用户输入待下载的文件名
        下载到子目录downloads下
        """
        try:
            if self.control_socket:
                remote_filename = tk.simpledialog.askstring("Input", "Enter remote filename:")
                if remote_filename:
                    # Get the data address for the data connection
                    time.sleep(0.5)
                    pasv_response = send_command(self.control_socket, 'PASV\r\n')
                    data_address = parse_pasv_response(pasv_response)

                    if data_address:
                        # Create a data socket and connect to the specified address
                        data_socket = create_data_socket(data_address)

                        # Send the RETR command with the remote filename
                        send_command(self.control_socket, f"RETR {remote_filename}\r\n")

                        # Open the local file for writing
                        local_folder = os.path.join(os.getcwd(), 'downloads')
                        os.makedirs(local_folder, exist_ok=True)
                        local_filename = os.path.join(local_folder, remote_filename)

                        with open(local_filename, 'wb') as local_file:
                            while True:
                                data = data_socket.recv(4096)
                                if not data:
                                    break
                                local_file.write(data)
                        
                        # Wait for the server response after download
                        # response = self.control_socket.recv(4096)
                        self.text_area.insert(tk.END, "Downloaded")
                        self.text_area.insert(tk.END, " {} bytes in total this time".format(os.path.getsize(local_filename)))       
                        

                    else:
                        self.text_area.insert(tk.END, "Error parsing PASV response\n")
                else:
                    self.text_area.insert(tk.END, "Please enter a remote filename.\n")
            else:
                self.text_area.insert(tk.END, "Not connected to FTP server. Please connect first.\n")
        except Exception as e:
            self.text_area.insert(tk.END, f"Error downloading file: {e}\n")
    
    # 断点重传 下载文件
    def download_file_re(self):
        """
        从服务器下载文件，
        prompt用户输入待下载的文件名
        
        检测本地是否有该文件，有则进入断点重传
        下载到子目录downloads下
        """
        try:
            if self.control_socket:
                remote_filename = tk.simpledialog.askstring("Input", "Enter remote filename:")
                if remote_filename:
                    local_folder = os.path.join(os.getcwd(), 'downloads')
                    os.makedirs(local_folder, exist_ok=True)
                    local_filename = os.path.join(local_folder, remote_filename)

                    # Get the data address for the data connection
                    time.sleep(0.5)
                    pasv_response = send_command(self.control_socket, 'PASV\r\n')
                    data_address = parse_pasv_response(pasv_response)

                    if data_address:
                        # Create a data socket and connect to the specified address
                        data_socket = create_data_socket(data_address)

                        # Check if the local file exists and get its size
                        local_file_size = 0
                        if os.path.exists(local_filename):
                            local_file_size = os.path.getsize(local_filename)
                            # Send REST command to resume download
                            send_command(self.control_socket, f"REST {local_file_size}\r\n")

                        # Send the RETR command with the remote filename
                        send_command(self.control_socket, f"RETR {remote_filename}\r\n")

                        # Open the local file for writing in append mode
                        with open(local_filename, 'ab') as local_file:
                            while True:
                                data = data_socket.recv(4096)
                                if not data:
                                    break
                                local_file.write(data)

                        # Wait for the server response after download
                        self.text_area.insert(tk.END, f"Downloaded {remote_filename} with resume support.\n")
                        self.text_area.insert(tk.END, f"Total bytes downloaded this time: {os.path.getsize(local_filename)-local_file_size}\n")

                    else:
                        self.text_area.insert(tk.END, "Error parsing PASV response\n")
                else:
                    self.text_area.insert(tk.END, "Please enter a remote filename.\n")
            else:
                self.text_area.insert(tk.END, "Not connected to FTP server. Please connect first.\n")
        except Exception as e:
            self.text_area.insert(tk.END, f"Error downloading file: {e}\n")

