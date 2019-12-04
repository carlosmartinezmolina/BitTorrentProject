import chord, socket, struct, hashlib, sys, threading

server_node = chord.Node(1)
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
        torrent_list = server_node.get_info(1,torrent_list)
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


def begin_server():
    s = socket.socket(type=socket.SOCK_STREAM)
    #print('type ip: ')
    ip = 'localhost'#input()
    print('type port: ')
    port = int(input())
    s.bind((ip,port))
    # s.bind(('localhost',8080))
    s.listen(10)

    

    while True:
        print('waiting for peers')
        sc , adr = s.accept()

        print(adr[0] + ' ' + str(adr[1]))
        th = threading.Thread(target = auxiliar,args =(sc,adr,))
        th.start()
        
        

    
    s.close()

begin_server()