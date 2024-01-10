import socket
import re

# create a control socket
def ftp_connect(host, port):
    """
    输入ftp服务器的ip和端口号
    创建ftp连接，返回控制socket
    """
    control_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    control_socket.connect((host, port))
    response = control_socket.recv(4096)
    print(response.decode('utf-8'))
    return control_socket

# PASV wrapped
def parse_pasv_response(response):
    """
    建立PASV FTP数据传输模式，输入FTP服务器返回的PASV响应，
    对PASV使用正则表达式搜索，提取PASV响应中的主机和端口信息，用于建立数据连接
    """
    # Convert bytes to string for regex matching
    response_str = response.decode('utf-8')
    
    match = re.search(r'(\d+),(\d+),(\d+),(\d+),(\d+),(\d+)', response_str)
    if match:
        host = '.'.join(match.group(1, 2, 3, 4))
        port = int(match.group(5)) * 256 + int(match.group(6))
        return host, port
    return None

# create a data socket
def create_data_socket(data_address):
    """
    输入数据连接的地址tuple(IP, 端口号)，创建数据socket
    """
    data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    data_socket.connect(data_address)
    return data_socket

# control socket can be directly created using ftp_connect

# RETR wrapped
def receive_file(control_socket, data_address, filename):
    """
    从服务器下载文件，输入控制socket，数据socket，要下载的文件名，下载到当前目录下
    """
    # pasv_response = send_command(control_socket, 'PASV\r\n')
    # data_address = parse_pasv_response(pasv_response)
    
    if data_address:
        print(f"Data connection address for receive: {data_address}")
        data_socket = create_data_socket(data_address)
        send_command(control_socket, f"RETR {filename}\r\n")
        with open(filename, 'wb') as file:
            while True:
                data = data_socket.recv(4096)
                if not data:
                    break
                file.write(data)
        data_socket.close()
        return data
    
    else:
        print("Failed to receive, Error parsing PASV response")

# resumable file transfer
def re_receive_file(control_socket, data_socket, filename, offset=0):
    """
    支持断点重传的文件下载，输入控制socket，数据socket，要下载的文件名，下载到当前目录下，偏移量.

    使用方法: 假如已经下载了文件，中途中断，那么在客户端的代码可以使用以下代码实现断点重传:
    filename = "partially_downloaded_file.txt"
    offset = os.path.getsize(filename)
    re_receive_file(control_socket, data_socket, filename, offset)

    这样便可以继续接收文件，而不是从头开始下载
    """
    if offset>0:
        send_command(control_socket, f"REST {offset}\r\n")
    
    # start receiving
    send_command(control_socket, f"RETR {filename}\r\n")

    mode = 'ab' if offset>0 else 'wb' # append if offset>0 else write
    with open(filename, mode) as file:
        while True:
            data = data_socket.recv(4096)
            if not data:
                break
            file.write(data)
    return data


# LIST wrapped
def list_file(control_socket, data_address):
    """
    打印出在服务器当前目录下的文件和目录
    
    输入控制socket，数据socket
    """
    # pasv_response = send_command(control_socket, 'PASV\r\n')
    # data_address = parse_pasv_response(pasv_response)
    
    if data_address:
        print(f"Data connection address for list: {data_address}")
        data_socket = create_data_socket(data_address)
        send_command(control_socket, f'LIST\r\n')

        received_data = b''
        # data = data_socket.recv(4096)
        while True:
            data = data_socket.recv(4096)
            if not data:
                break
            received_data += data
            print(received_data)
        data_socket.close()
        return received_data
    else:
        print("Failed to list. Error parsing PASV response")


    # with open(filename, 'wb') as file:
    #     while True:
    #         data = data_socket.recv(4096)
    #         if not data:
    #             break
    #         file.write(data)

# send commands
def send_command(control_socket, command):
    """
    输入控制socket，和要发送的命令，发送命令到服务器，返回服务器的响应
    """
    control_socket.sendall(command.encode('utf-8'))
    response = control_socket.recv(4096)
    print(command, " says ",response.decode('utf-8'))
    return response

# CWD wrapped
def change_directory(control_socket, directory):
    """
    改变在服务器上的当前目录
    
    输入控制socket，和要改变的目录名
    """
    send_command(control_socket, f'CWD {directory}\r\n')

# QUIT wrapped
def quit(control_socket):
    """
    退出FTP连接
    
    输入控制socket
    """
    send_command(control_socket, f'QUIT\r\n')
    control_socket.close()

# Upload wrapped
def upload(control_socket, data_address, filename):
    """
    上传文件到FTP服务器
    
    输入控制socket，数据address，要上传的文件名
    """
    pasv_response = send_command(control_socket, 'PASV\r\n')
    data_address = parse_pasv_response(pasv_response)

    if data_address:
        print(f"Data connection address for upload: {data_address}")
        data_socket = create_data_socket(data_address)
        send_command(control_socket, f'STOR {filename}\r\n')
        with open(filename, 'rb') as loc_file:
            data = loc_file.read(4096)
            while data:
                data_socket.sendall(data)
                data = loc_file.read(4096)

        data_socket.close()
        response = control_socket.recv(4096)
        print(response.decode('utf-8'))
    else:
        print("Failed to upload. Error parsing PASV response")
