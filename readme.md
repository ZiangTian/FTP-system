# A graphical FTP client

The FTP client has been implemented with the following features:

- Login authentication 
- Uploading
- Downloading
- Interrupted transfers resumption

The client and functional functions are implemented in [`ftpclient.py`](https://github.com/ZiangTian/FTP-system/blob/main/ftpclient.py), called by [`gui.py`](https://github.com/ZiangTian/FTP-system/blob/main/gui.py). `Relics` contains the implementation without a graphical interface, and `downloads` is the directory where files downloaded by the client are stored.
