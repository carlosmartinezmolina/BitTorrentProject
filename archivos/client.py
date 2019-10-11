import socket, os, struct
from method import sending_file, making_file
#/home/carlos/Documents/tahm.avi
#/home/carlos/Documents/PythonBook.pdf


def begin_client():
    s = socket.socket(type=socket.SOCK_STREAM)
    s.connect(('10.42.0.126',8080))

    while True:
        path , mensaje = making_file()
        s.send(path.encode('utf-8'))
        answer = s.recv(4)
        
        sending_file(s,mensaje)

    s.close()

begin_client()
