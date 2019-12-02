import socket, os, struct, threading
from method import geting_pack, creating_file, sending_file, making_file
#/home/carlos/Documents/tahm.avi
#/home/carlos/Documents/PythonBook.pdf
def handshake(s):
    s.send(b'hello')
    answer = s.recv(4)
    print(answer.decode())

def request(s):
    print('type list to get the list of torrents')
    print('type download to ask for a file')
    print('type upload to share a file')
    print('type exit to end')
    entry = input()
    if entry == 'exit':
        s.send(b'exit')
        answer = s.recv(4)
        return ['exit']
    if entry == 'list':
        s.send(b'list')
        answer = s.recv(4)
        print(answer.decode())
        my_list = s.recv(1024)
        my_list = my_list.decode()
        print(my_list)
    if entry == 'download':
        s.send(b'download')
        answer = s.recv(4)
        print(answer.decode())
        print('type a filename: ')
        filename = input()
        s.send(filename.encode())
        ip_list = s.recv(1024)
        print(ip_list.decode())
        return ip_list
    if entry == 'upload':
        s.send(b'upload')
        answer = s.recv(4)
        print(answer.decode())
        print('type a filename: ')
        filename = input()
        s.send(filename.encode())
    return []

def get_pieces(s,pos,my_file):
    pack = str(pos)
    s.send(pack.encode())
    answer = s.recv(1024)
    answer = int(answer.decode())
    for i in range(answer):
        pack = s.recv(1024)
        my_file.append(pack)
        pos += 1
    s.send(b'done')
    return pos

def client(ip_list,size):
    s = socket.socket(type=socket.SOCK_STREAM)

    my_file = []
    pos = 0
    i = 0
    while i < len(ip_list):
        try:
            if len(my_file) == size:
                break
            s.connect(ip_list[i])
            handshake(s)
            pos = get_pieces(s,pos,my_file)

            i+= 1
        except:
            i += 1
            if i == len(ip_list) - 1:
                i = 0

    

    s.close()

def server():
    s = socket.socket(type=socket.SOCK_STREAM)

    s.bind(('127.0.0.1',8080))

    s.listen(10)

    while True:
        sc , adr = s.accept()
        path = sc.recv(1024)
        sc.send(b'done')
        print(path)
        archivo = geting_pack(sc)
        creating_file('/home/carlos/Documents/Codes/learnigStuff/archivos/test.pdf', archivo)
        print('yes')

        

    sc.close()
    s.close()

def begin_client():
    s = socket.socket(type=socket.SOCK_STREAM)

    print('type ip: ')
    ip = input()
    print('type port: ')
    port = int(input())
    s.connect((ip,port))
    # s.connect(('localhost',8080))
    handshake(s)
    
    while True:
        ip_list = request(s)
        if len(ip_list) > 0 and ip_list[0] == 'exit':
            break
        print('yes')
        #th = threading.Thread(target = client(ip_list))
        #th.start()
    


    s.close()

begin_client()
