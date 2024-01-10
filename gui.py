import tkinter as tk
from ftpclient import FTPClientGUI

if __name__ == "__main__":
    root = tk.Tk() # Create the root window
    app = FTPClientGUI(root) # 创建图形化应用
    root.mainloop()