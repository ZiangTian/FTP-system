import socket
import os
from tkinter import Tk, filedialog

class FTPClient:
    def __init__(self, server_host, server_port):
        self.server_host = server_host
        self.server_port = server_port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connected = False

    def connect(self):
        try:
            self.client_socket.connect((self.server_host, self.server_port))
            self.connected = True
            print("Connected to FTP server")
        except Exception as e:
            print(f"Error connecting to FTP server: {e}")

    def disconnect(self):
        self.client_socket.close()
        self.connected = False
        print("Disconnected from FTP server")
    def upload_file(self, local_path, remote_path):
        if not self.connected:
            print("Not connected to FTP server. Please connect first.")
            return

        try:
            with open(local_path, 'rb') as file:
                file_data = file.read()
                self.client_socket.sendall(file_data)
            print(f"File {os.path.basename(local_path)} uploaded successfully.")
        except FileNotFoundError:
            print(f"Error: File not found - {local_path}")
        except Exception as e:
            print(f"Error uploading file: {e}")


def select_file():
    root = Tk()
    root.filename = filedialog.askopenfilename(initialdir="/", title="Select file",
                                               filetypes=(("All files", "*.*"),))
    root.destroy()
    return root.filename

if __name__ == "__main__":
    ftp_client = FTPClient('127.0.0.1', 21)
    ftp_client.connect()

    local_file_path = select_file()
    if local_file_path:
        remote_file_path = input("Enter the remote file path on the server: ")
        ftp_client.upload_file(local_file_path, remote_file_path)

    ftp_client.disconnect()

