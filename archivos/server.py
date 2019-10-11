import socket, struct
from method import geting_pack, creating_file
    

def begin_server():

    s = socket.socket(type=socket.SOCK_STREAM)

    s.bind(('127.0.0.1',8080))

    s.listen(5)

    sc , adr = s.accept()

    while True:

        path = sc.recv(1024)
        sc.send(b'done')
        print(path)

        archivo = geting_pack(sc)
        
        creating_file('/home/carlos/Documents/Codes/learnigStuff/archivos/test.pdf', archivo)
        print('yes')

        

    sc.close()
    s.close()

begin_server()