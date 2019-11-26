import socket, os, struct
#/home/carlos/Documents/tahm.avi
#/home/carlos/Documents/PythonBook.pdf


def begin_client():
    number  = int(input())
    s = socket.socket(type=socket.SOCK_STREAM)
    s.connect(('127.0.0.1',8080))

    
    s.send(struct.pack('I',number))
    answer = s.recv(4)
    print(answer.decode())
        

    s.close()

begin_client()
