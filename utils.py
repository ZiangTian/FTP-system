import socket
import re

# create a control socket
def ftp_connect(host, port):
    control_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    control_socket.connect((host, port))
    response = control_socket.recv(4096)
    print(response.decode('utf-8'))
    return control_socket

# create a data socket
def create_data_socket(data_address):
    data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    data_socket.connect(data_address)
    return data_socket

# control socket can be directly created using ftp_connect

# RETR wrapped
def receive_file(control_socket, data_socket, filename):
    send_command(control_socket, f"RETR {filename}\r\n")
    
    with open(filename, 'wb') as file:
        while True:
            data = data_socket.recv(4096)
            if not data:
                break
            file.write(data)

# LIST wrapped
def list_file(control_socket, data_socket):
    send_command(control_socket, f'LIST\r\n')
    data = data_socket.recv(4096)
    # with open(filename, 'wb') as file:
    #     while True:
    #         data = data_socket.recv(4096)
    #         if not data:
    #             break
    #         file.write(data)
    return data

# PASV wrapped
def parse_pasv_response(response):
    # Convert bytes to string for regex matching
    response_str = response.decode('utf-8')
    
    match = re.search(r'(\d+),(\d+),(\d+),(\d+),(\d+),(\d+)', response_str)
    if match:
        host = '.'.join(match.group(1, 2, 3, 4))
        port = int(match.group(5)) * 256 + int(match.group(6))
        return host, port
    return None


# def parse_pasv_response(response):
#     match = re.search(r'(\d+),(\d+),(\d+),(\d+),(\d+),(\d+)', response.decode('utf-8'))
#     if match:
#         host = '.'.join(match.group(1, 2, 3, 4))
#         port = int(match.group(5)) * 256 + int(match.group(6))
#         return host, port
#     return None

# send commands
def send_command(control_socket, command):
    control_socket.sendall(command.encode('utf-8'))
    response = control_socket.recv(4096)
    print(response.decode('utf-8'))
    return response

# CWD wrapped
def change_directory(control_socket, directory):
    send_command(control_socket, f'CWD {directory}\r\n')
