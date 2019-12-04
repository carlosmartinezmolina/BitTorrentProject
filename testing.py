import chord, socket, struct, hashlib, sys, threading, time

server_node = chord.Node(2)
server_node.join(server_node)

def create_node(ip,port):
    h = str(port)
    h = hashlib.sha256(h.encode())
    n = int.from_bytes(h.digest(),byteorder = sys.byteorder) % 2**chord.k
    print(n)
    print(server_node.is_there(n))
    if not server_node.is_there(n) == n:
        new_node = chord.Node(n)
        new_node.join(server_node)

def handshake(sc):
    pack = sc.recv(1024)
    print(pack.decode())
    if pack.decode() == 'hello':
        sc.send(b'done')

def request(sc,adr):
    create_node(adr[0],adr[1])
    try:
        pack = sc.recv(1024)
        if len(pack) == 0:
                return False
    except:
        return False
    if pack.decode() == 'exit':
        sc.send(b'done')
        return False
    if pack.decode() == 'list':
        sc.send(b'done')
        torrent_list = []
        torrent_list = server_node.get_info(2,torrent_list)
        sc.send(str(torrent_list).encode())
    if pack.decode() == 'download':
        sc.send(b'done')
        try:
            pack = sc.recv(1024)
            if len(pack) == 0:
                return False
        except:
            return False
        h = hashlib.sha256(pack)
        n = int.from_bytes(h.digest(),byteorder = sys.byteorder) % 2**chord.k
        ip_list = server_node.get_key(n)
        sc.send(str(ip_list).encode())
    if pack.decode() == 'upload':
        sc.send(b'done')
        try:
            pack = sc.recv(1024)
            if len(pack) == 0:
                return False
        except:
            return False
        h = hashlib.sha256(pack)
        n = int.from_bytes(h.digest(),byteorder = sys.byteorder) % 2**chord.k
        ip_list = server_node.put_key(n,adr,pack.decode())
    return True

def auxiliar(sc,adr):
    handshake(sc)
    pack = sc.recv(1024)
    pack = int(pack.decode())
    sc.send(b'done')
    boolean = True
    while boolean:
        boolean = request(sc,(adr[0],pack))
    sc.close()

def call_broadcast_client(ip,port):
    ip_tracker = broadcast_client(ip,port)
    print('encontre con el broadcast al ' + str(ip_tracker))


def begin_server():
    s = socket.socket(type=socket.SOCK_STREAM)
    #print('type ip: ')
    ip = 'localhost'#input()
    print('type port: ')
    port = int(input())
    s.bind((ip,port))
    # s.bind(('localhost',8080))
    s.listen(10)

    thr = threading.Thread(target = broadcast_server,args = ('191.121.116.10',port,))
    thr.start()

    thr = threading.Thread(target = call_broadcast_client,args = ('191.121.116.10',port,))
    thr.start()

    while True:
        print('waiting for peers')
        sc , adr = s.accept()

        print(adr[0] + ' ' + str(adr[1]))
        th = threading.Thread(target = auxiliar,args =(sc,adr,))
        th.start()
        
        

    
    s.close()

def broadcast_server(ip,port):
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    server.setsockopt(socket.SOL_SOCKET,socket.SO_BROADCAST, 1)

    server.bind(('',37020))
    is_conecting = []
    while True:
        data, addr = server.recvfrom(1024)
        if int(data.decode()) > 0 and int(data.decode()) != port:# and ip != addr[0]:
            if not is_conecting.__contains__(int(data.decode())):
                is_conecting.append(int(data.decode()))
                print('conection from ' + data.decode())
                th = threading.Thread(target = broadcast_server_auxiliar,args =(addr[0],data.decode(),ip,port,))
                th.start()

def broadcast_client(ip,port):
    client = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)

    client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    client.setsockopt(socket.SOL_SOCKET,socket.SO_BROADCAST, 1)
    message = str(port)
    lista = []
    th = threading.Thread(target = broadcast_client_auxiliar,args = (ip,port + 1000,lista,))
    th.start()
    while True:
        client.sendto(message.encode(),('255.255.255.255',37020))
        time.sleep(2)
        if len(lista) > 0:
            break
    print(lista[0])
    return lista[0]

def broadcast_server_auxiliar(ip,port,my_ip,my_port):
    s = socket.socket(type=socket.SOCK_STREAM)
    try:
        s.connect((ip,int(port) + 1000))
        answer = s.recv(4)
        pack = str((my_ip,my_port))
        s.send(pack.encode())
        answer = s.recv(4)
        s.close()
    except:
        s.close()

def broadcast_client_auxiliar(ip,port,lista):
    s = socket.socket(type=socket.SOCK_STREAM)
    s.bind((ip,port))
    s.listen(1)
    sc , adr = s.accept()
    sc.send(b'done')
    pack = sc.recv(1024)
    sc.send(b'done')
    pack = pack.decode()
    pack = pack[1:-1]
    pack = pack.split(',')
    l = pack[0].split("'")
    pack = (l[1],int(pack[1]))
    lista.append(pack)
    s.close()

begin_server()


