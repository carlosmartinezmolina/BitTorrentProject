import chord, socket, struct, hashlib, sys, threading

server_node = chord.Node(1)
server_node.join(server_node)

def create_node(ip,port):
    h = ip + ':' + str(port)
    h = hashlib.sha256(h.encode())
    n = int.from_bytes(h.digest(),byteorder = sys.byteorder) % 2**chord.k
    new_node = chord.Node(n)
    # print(n)
    new_node.join(server_node)
    # print('end')

def handshake(sc):
    pack = sc.recv(1024)
    if pack.decode() == 'hello':
        sc.send(b'done')

def request(sc,adr):
    pack = sc.recv(1024)
    if pack.decode() == 'new':
        sc.send(b'done')
        create_node(adr[0],adr[1])
    if pack.decode() == 'download':
        sc.send(b'done')
        pack = sc.recv(1024)
        h = hashlib.sha256(pack)
        n = int.from_bytes(h.digest(),byteorder = sys.byteorder) % 2**chord.k
        ip_list = server_node.get_key(n)
        sc.send(str(ip_list).encode())
    if pack.decode() == 'upload':
        sc.send(b'done')
        pack = sc.recv(1024)
        h = hashlib.sha256(pack)
        n = int.from_bytes(h.digest(),byteorder = sys.byteorder) % 2**chord.k
        ip_list = server_node.put_key(n,adr)

def auxiliar(sc,adr):
    handshake(sc)
    request(sc,adr)
    sc.close()


def begin_server():
    s = socket.socket(type=socket.SOCK_STREAM)
    print('type ip: ')
    ip = input()
    print('type port: ')
    port = int(input())
    s.bind((ip,port))
    # s.bind(('localhost',8080))
    s.listen(10)

    

    while True:
        # print('no')
        sc , adr = s.accept()
        # print('yes')
        th = threading.Thread(target = auxiliar(sc,adr))
        th.start()
        
        

    
    s.close()

begin_server()