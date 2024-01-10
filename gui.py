import tkinter as tk
from ftpclient import FTPClientGUI

if __name__ == "__main__":
    root = tk.Tk()
    app = FTPClientGUI(root)
    root.mainloop()