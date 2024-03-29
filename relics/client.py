import socket
import re

from utils import ftp_connect, create_data_socket, send_command, receive_file, list_file, parse_pasv_response, change_directory, upload


if __name__ == "__main__":
    host = '10.128.22.12'  
    port = 21

    # 获得控制socket
    control_socket = ftp_connect(host, port)

    # 我自己配置的主机上的ftp服务器
    send_command(control_socket, 'USER FtpUsr\r\n')
    send_command(control_socket, 'PASS 654321\r\n')

    # list_file(control_socket)
    # print("listed1  !")
    # # 获得数据socket需要的主机端口号和地址
    pasv_response = send_command(control_socket, 'PASV\r\n')
    data_address = parse_pasv_response(pasv_response)
    
    # # if data_address:


    # # 创建数据socket
    # # data_socket = create_data_socket(data_address)
    # # send_command(control_socket, f'LIST\r\n')

    # receive_file(control_socket, 'example.txt')
    # print("received1 !")
    # # 移动到books目录下
    change_directory(control_socket, 'books')
    # print("changed1  !")


    # # 获得books目录下的文件列表
    list_file(control_socket, data_address)
    print("listed2  !")

    # # 下载文件riscv-privileged-v1.10.pdf
    receive_file(control_socket, data_address, '10Friends__Lovers_and_The_Big_Terrible_Thing.torrent')


    # 上传文件file_listing.txt
    upload(control_socket, data_address, 'file_listing.txt')

    # 关闭数据socket
    # data_socket.close()
    # else:
        # print("Error parsing PASV response")

    # 关闭控制socket
    control_socket.close()
