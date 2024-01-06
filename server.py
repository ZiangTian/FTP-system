import socket
import threading
import os
from tkinter import Tk, Label, Button, filedialog

class FTPServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)

    def start(self):
        print(f"FTP Server listening on {self.host}:{self.port}")
        while True:
            client_socket, client_address = self.server_socket.accept()
            threading.Thread(target=self.handle_client, args=(client_socket,)).start()

    def handle_client(self, client_socket):
        # Implement FTP protocol handling here
        pass

def select_file():
    root = Tk()
    root.filename = filedialog.askopenfilename(initialdir="/", title="Select file",
                                               filetypes=(("Text files", "*.txt"), ("all files", "*.*")))
    root.destroy()
    return root.filename

if __name__ == "__main__":
    ftp_server = FTPServer('127.0.0.1', 21)
    threading.Thread(target=ftp_server.start).start()
