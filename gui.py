import tkinter as tk
from tkinter import scrolledtext
from tkinter import messagebox
from tkinter import filedialog
import socket
import os
import re
import time
# from utils import create_data_socket, receive_file, list_file, parse_pasv_response, change_directory


class FTPClientGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("FTP Client")
        # self.local_file_path = tk.StringVar()
        # self.remote_file_path = tk.StringVar()
        # self.create_data_socket = create_data_socket
        # self.receive_file = receive_file
        # self.list_file = list_file
        # self.parse_pasv_response = parse_pasv_response
        # self.change_directory = change_directory
        self.create_widgets()

    def ftp_connect(self, host, port):
        control_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        control_socket.connect((host, port))
        response = control_socket.recv(4096)
        self.text_area.insert(tk.END, f"{response.decode('utf-8')}\n")
        return control_socket
    
    def create_widgets(self):
        self.text_area = scrolledtext.ScrolledText(self.master, wrap=tk.WORD, width=50, height=20)
        self.text_area.pack(padx=10, pady=10)

        self.connect_button = tk.Button(self.master, text="Connect", command=self.connect_ftp)
        self.connect_button.pack(pady=5)

        self.list_button = tk.Button(self.master, text="List Files", command=self.list_files)
        self.list_button.pack(pady=5)

        self.upload_button = tk.Button(self.master, text="Upload File", command=self.upload_file)
        self.upload_button.pack(pady=5)

        self.download_button = tk.Button(self.master, text="Download File", command=self.download_file)
        self.download_button.pack(pady=5)

        self.quit_button = tk.Button(self.master, text="Quit", command=self.master.destroy)
        self.quit_button.pack(pady=5)

    def connect_ftp(self):
        host = '10.128.22.12' 
        port = 21

        self.control_socket = self.ftp_connect(host, port)
        
        send_command(self.control_socket, 'USER FtpUsr\r\n')
        send_command(self.control_socket, 'PASS 654321\r\n')

        self.text_area.insert(tk.END, "Connected to FTP server.\n")

    def list_files(self):
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

            file_encoding = 'utf-8'  # Replace with the correct encoding
            decoded_data = received_data.decode(file_encoding)

            self.text_area.insert(tk.END, f"File Listing:\n{decoded_data}\n")

            data_socket.close()
        else:
            self.text_area.insert(tk.END, "Error parsing PASV response\n")
    
    def upload_file(self):
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

    def download_file(self):
            remote_filename = self.remote_file_path.get()
            if remote_filename:
                local_filename = filedialog.asksaveasfilename(title="Select Save Location")
                if local_filename:
                    # Get the data address for the data connection
                    pasv_response = send_command(self.control_socket, 'PASV\r\n')
                    data_address = parse_pasv_response(pasv_response)

                    if data_address:
                        # Create a data socket and connect to the specified address
                        data_socket = create_data_socket(data_address)

                        # Download the remote file from the server
                        self.download_file_operation(data_socket, local_filename, remote_filename)

                        # Close the data socket
                        data_socket.close()
                    else:
                        self.text_area.insert(tk.END, "Error parsing PASV response\n")
                else:
                    self.text_area.insert(tk.END, "Please select a local save location.\n")
            else:
                self.text_area.insert(tk.END, "Please enter a remote filename.\n")

    def download_file_operation(self, data_socket, local_filename, remote_filename):
            # Send the RETR command to the server
            send_command(self.control_socket, f"RETR {remote_filename}\r\n")

            # Open the local file for writing
            with open(local_filename, 'wb') as local_file:
                while True:
                    data = data_socket.recv(4096)
                    if not data:
                        break
                    local_file.write(data)

            # Close the data socket to signal the end of file download
            data_socket.close()

            # Wait for the server response after download
            response = self.control_socket.recv(4096)
            self.text_area.insert(tk.END, response.decode('utf-8') + "\n")


def create_data_socket(data_address):
    data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    data_socket.connect(data_address)
    return data_socket

def send_command(control_socket, command):
    control_socket.sendall(command.encode('utf-8'))
    if command ==  :time.sleep(0.5)
    response = control_socket.recv(4096)
    return response

def parse_pasv_response(response):
    response_str = response.decode('utf-8')
    match = re.search(r'(\d+),(\d+),(\d+),(\d+),(\d+),(\d+)', response_str)
    if match:
        host = '.'.join(match.group(1, 2, 3, 4))
        port = int(match.group(5)) * 256 + int(match.group(6))
        return host, port
    return None

if __name__ == "__main__":
    root = tk.Tk()
    app = FTPClientGUI(root)
    root.mainloop()
