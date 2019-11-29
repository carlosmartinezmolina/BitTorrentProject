import socket, os, struct
#/home/carlos/Documents/tahm.avi
#/home/carlos/Documents/PythonBook.pdf
def handshake(s):
    s.send(b'hello')
    answer = s.recv(4)
    print(answer.decode())

def request(s):
    print('type new for join the network')
    print('type download to ask for a file')
    print('type upload to share a file')
    entry = input()
    if entry == 'new':
        s.send(b'new')
        answer = s.recv(4)
        print(answer.decode())
    if entry == 'download':
        s.send(b'download')
        answer = s.recv(4)
        print(answer.decode())
        print('type a filename: ')
        filename = input()
        s.send(filename.encode())
        ip_list = s.recv(1024)
        print(ip_list.decode())
    if entry == 'upload':
        s.send(b'upload')
        answer = s.recv(4)
        print(answer.decode())
        print('type a filename: ')
        filename = input()
        s.send(filename.encode())

def begin_client():
    s = socket.socket(type=socket.SOCK_STREAM)
    print('type ip: ')
    ip = input()
    print('type port: ')
    port = int(input())
    s.connect((ip,port))

    handshake(s)
    
    request(s)
        

    s.close()

begin_client()
