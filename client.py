import socket
import re

from utils import ftp_connect, create_data_socket, send_command, receive_file, list_file, parse_pasv_response, change_directory


if __name__ == "__main__":
    host = '10.128.22.12'  
    port = 21

    control_socket = ftp_connect(host, port)

    # Replace 'USERNAME' and 'PASSWORD' with your FTP server credentials
    send_command(control_socket, 'USER FtpUsr\r\n')
    send_command(control_socket, 'PASS 654321\r\n')

    pasv_response = send_command(control_socket, 'PASV\r\n')
    # data_address = parse_pasv_response(pasv_response.decode('utf-8'))
    data_address = parse_pasv_response(pasv_response)
    
    if data_address:
        print(f"Data connection address: {data_address}")
        data_socket = create_data_socket(data_address)
        change_directory(control_socket, 'books')
        
        # file_listing_filename = 'file_listing.txt'
    
        # with open(file_listing_filename, 'wb') as file:
        #     while True:
        #         data = data_socket.recv(4096)
        #         if not data:
        #             break
        #         file.write(data)
        print(list_file(control_socket, data_socket))

        receive_file(control_socket, data_socket, 'riscv-privileged-v1.10.pdf')
        data = data_socket.recv(4096)
        print(data)

        data_socket.close()
    else:
        print("Error parsing PASV response")
    
    # Example: Change to the directory 'example_directory'
    # send_command(control_socket, 'CWD example_directory\r\n')

    # # Example: List files in the current directory
    # send_command(control_socket, 'LIST\r\n')

    # # Example: Download a file named 'example.txt'
    # send_command(control_socket, 'RETR riscv-privileged-v1.10.pdf\r\n')

    control_socket.close()
