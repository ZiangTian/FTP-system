import socket
import re

def create_data_socket(data_address):
    data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    data_socket.connect(data_address)
    return data_socket

def receive_file(control_socket, data_socket, filename):
    send_command(control_socket, f"RETR {filename}\r\n")
    
    with open(filename, 'wb') as file:
        while True:
            data = data_socket.recv(4096)
            if not data:
                break
            file.write(data)

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

def ftp_connect(host, port):
    control_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    control_socket.connect((host, port))
    response = control_socket.recv(4096)
    print(response.decode('utf-8'))
    return control_socket

def send_command(control_socket, command):
    control_socket.sendall(command.encode('utf-8'))
    response = control_socket.recv(4096)
    print(response.decode('utf-8'))
    return response

def main():
    host = '10.128.20.24'  # Replace with your FTP server IP address or hostname
    port = 21

    control_socket = ftp_connect(host, port)

    # Replace 'USERNAME' and 'PASSWORD' with your FTP server credentials
    send_command(control_socket, 'USER Benjamin\r\n')
    send_command(control_socket, 'PASS 6124360230tzaing\r\n')
    send_command(control_socket, 'PASV\r\n')

    pasv_response = send_command(control_socket, 'PASV\r\n')
    # data_address = parse_pasv_response(pasv_response.decode('utf-8'))
    data_address = parse_pasv_response(pasv_response)
    
    if data_address:
        print(f"Data connection address: {data_address}")
        data_socket = create_data_socket(data_address)

        # Example: Download a file named 'example.txt'
        receive_file(control_socket, data_socket, 'example.txt')

        data_socket.close()
    else:
        print("Error parsing PASV response")
    
    # Example: Change to the directory 'example_directory'
    # send_command(control_socket, 'CWD example_directory\r\n')

    # Example: List files in the current directory
    send_command(control_socket, 'LIST\r\n')

    # Example: Download a file named 'example.txt'
    send_command(control_socket, 'RETR example.txt\r\n')

    control_socket.close()

if __name__ == "__main__":
    main()


