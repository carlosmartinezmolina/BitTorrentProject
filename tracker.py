import chord, socket, struct, hashlib, sys, threading, time, dill, random

server_node = None
is_conected = []
_ip = None
_port = None
lock = threading.RLock()
ip_tracker = None
_cliente = None
_cliente_ip = None

def create_node(ip,port):
    global server_node
    lock.acquire()
    h = str(port)
    h = hashlib.sha256(h.encode())
    n = int.from_bytes(h.digest(),byteorder = sys.byteorder) % 2**chord.k
    if not server_node.is_there(n):
        print('yes')
        new_node = chord.Node(n)
        new_node.join(server_node)
        if not _cliente:
            server_node.put_tracker((ip,port))
        torrent_list = []
        torrent_list = server_node.get_trackers(server_node.id,torrent_list)
        if (ip,port) == (_ip,_port) or _cliente:
            thr = threading.Thread(target = update_remote_trackers,args = (ip,port,))
            thr.start()
    lock.release()

def handshake(sc):
    global _cliente
    pack = sc.recv(1024)
    print(pack.decode())
    if pack.decode() == 'cliente':
        _cliente = True
    else:
        _cliente = False
    sc.send(b'done')

def upload_remote_trackers(ip,port,upload_info):
    lock.acquire()
    torrent_list = []
    torrent_list = server_node.get_trackers(server_node.id,torrent_list)
    lock.release()
    print(torrent_list)
    for i in torrent_list:
        if i != (ip,port) and i != (_ip,_port):
            s = socket.socket(type=socket.SOCK_STREAM)
            try:
                s.connect(i)
                s.send(b'hello')
                answer = s.recv(4)
                pack = str(port)
                s.send(pack.encode())
                answer = s.recv(4)
                s.send(b'update_trackers')
                answer = s.recv(4)
                s.send(b'remote_upload')
                answer = s.recv(4)
                pack = str((ip,port))
                s.send(pack.encode())
                answer = s.recv(4)
                s.send(upload_info.encode())
                answer = s.recv(4)
                s.close()
            except:
                s.close()

def update_remote_trackers(ip,port):
    lock.acquire()
    torrent_list = []
    torrent_list = server_node.get_trackers(server_node.id,torrent_list)
    lock.release()
    print(torrent_list)
    temp = ip_tracker
    if _cliente:
        temp = (_ip,_port)
    for i in torrent_list:
        if i != (ip,port) and i != temp and i != (_ip,_port):
            print('tracker remoto ' + str(i) + ' ' + str((ip,port)) + ' ' + str(ip_tracker) )
            s = socket.socket(type=socket.SOCK_STREAM)
            try:
                s.connect(i)
                s.send(b'hello')
                answer = s.recv(4)
                pack = str(port)
                s.send(pack.encode())
                answer = s.recv(4)
                s.send(b'updata_trackers')
                answer = s.recv(4)
                s.send(b'exit')
                answer = s.recv(4)
                s.close()
            except:
                s.close()

def request(sc,adr):
    global server_node
    answer = sc.recv(15)
    if answer.decode() != 'update_trackers':
        sc.send(b'done')
        create_node(adr[0],adr[1])
        if not _cliente:
            return
    else:
        sc.send(b'done')
    while True:
        try:
            pack = sc.recv(1024)
            #print(pack.decode())
            if len(pack) == 0:
                break
        except:
            break
        if pack.decode() == 'exit':
            sc.send(b'done')
            break
        if pack.decode() == 'list':
            sc.send(b'done')
            lock.acquire()
            torrent_list = []
            torrent_list = server_node.get_info(server_node.id,torrent_list)
            lock.release()
            sc.send(str(torrent_list).encode())
        if pack.decode() == 'download':
            sc.send(b'done')
            try:
                pack = sc.recv(1024)
                if len(pack) == 0:
                    break
            except:
                break
            h = hashlib.sha256(pack)
            n = int.from_bytes(h.digest(),byteorder = sys.byteorder) % 2**chord.k
            ip_list = server_node.get_key(n)
            sc.send(str(ip_list).encode())
            lock.acquire()
            server_node.put_key(n,adr,pack.decode())
            lock.release()
            thr = threading.Thread(target = upload_remote_trackers,args = (adr[0],adr[1],pack.decode(),))
            thr.start()
        if pack.decode() == 'upload':
            sc.send(b'done')
            try:
                pack = sc.recv(1024)
                if len(pack) == 0:
                    break
            except:
                break
            h = hashlib.sha256(pack)
            n = int.from_bytes(h.digest(),byteorder = sys.byteorder) % 2**chord.k
            lock.acquire()
            ip_list = server_node.put_key(n,adr,pack.decode())
            lock.release()
            thr = threading.Thread(target = upload_remote_trackers,args = (adr[0],adr[1],pack.decode(),))
            thr.start()
        if pack.decode() == 'remote_upload':
            sc.send(b'done')
            print('entrooooo')
            try:
                pack = sc.recv(1024)
                if len(pack) == 0:
                    break
            except:
                break
            pack = pack.decode()
            pack = pack[1:-1]
            pack = pack.split(',')
            l = pack[0].split("'")
            pack = (l[1],int(pack[1]))
            address = pack
            sc.send(b'done')
            try:
                pack = sc.recv(1024)
                if len(pack) == 0:
                    break
            except:
                break
            sc.send(b'done')
            h = hashlib.sha256(pack)
            n = int.from_bytes(h.digest(),byteorder = sys.byteorder) % 2**chord.k
            lock.acquire()
            ip_list = server_node.put_key(n,address,pack.decode())
            lock.release()
            break

def auxiliar(sc,adr):
    handshake(sc)
    pack = sc.recv(1024)
    pack = int(pack.decode())
    sc.send(b'done')
    request(sc,(adr[0],pack))
    sc.close()

def call_broadcast_client(ip,port):
    global server_node
    global ip_tracker
    ip_tracker = broadcast_client(ip,port)
    lock.acquire()
    server_node.put_tracker((_ip,_port))
    create_node(ip,port)
    print('encontre con el broadcast al ' + str(ip_tracker))
    s = socket.socket(type=socket.SOCK_STREAM)
    try:
        s.connect(ip_tracker)
        s.send(b'hello')
        answer = s.recv(4)
        pack = str(port)
        s.send(pack.encode())
        answer = s.recv(4)
        s.send(b'updato_trackers')
        answer = s.recv(4)
        s.close()
    except:
        s.close()
    lock.release()

def begin_server():
    global server_node
    global _port
    global _ip
    s = socket.socket(type=socket.SOCK_STREAM)
    ip = '192.168.43.148'#input()
    port = random.randint(8000,65000)#int(input())
    _ip = ip
    _port = port
    x = str(port)
    x = hashlib.sha256(x.encode())
    x = int.from_bytes(x.digest(),byteorder = sys.byteorder) % 2**chord.k
    print(x%10000)
    print(port)
    s.bind((ip,port))
    s.listen(10)

    print('type of node')
    type_node = input()
    if type_node == 'initial':
        h = str(port)
        h = hashlib.sha256(h.encode())
        n = int.from_bytes(h.digest(),byteorder = sys.byteorder) % 2**chord.k
        lock.acquire()
        server_node = chord.Node(n)
        server_node.join(server_node)
        server_node.put_tracker((_ip,_port))
        lock.release()
        thr = threading.Thread(target = broadcast_server,args = (ip,port,))
        thr.start()
    else:
        call_broadcast_client(ip,port)
        thr = threading.Thread(target = broadcast_server,args = (ip,port,))
        thr.start()

    while True:
        print('waiting for peers')
        sc , adr = s.accept()

        print(adr[0] + ' ' + str(adr[1]))
        th = threading.Thread(target = auxiliar,args =(sc,adr,))
        th.start()
        
        
    s.close()

def broadcast_server(ip,port):
    global is_conected
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    server.setsockopt(socket.SOL_SOCKET,socket.SO_BROADCAST, 1)

    server.bind(('',37020))
    
    while True:
        data, addr = server.recvfrom(1024)
        if int(data.decode()) > 0 and int(data.decode()) != port:# and ip != addr[0]:
            if not is_conected.__contains__(int(data.decode())):
                is_conected.append(int(data.decode()))
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
    return lista[0]

def broadcast_server_auxiliar(ip,port,my_ip,my_port):
    global server_node
    global is_conected
    s = socket.socket(type=socket.SOCK_STREAM)
    try:
        s.connect((ip,int(port) + 1000))
        answer = s.recv(7)
        print('conection from ' + str(int(port) + 1000))
        s.send(b'done')
        if answer.decode() == 'tracker':
            pakete = s.recv(1024)
            pakete = pakete.decode()
            pakete = pakete[1:-1]
            pakete = pakete.split(',')
            l = pakete[0].split("'")
            p = (l[1],int(pakete[1]))
            lock.acquire()
            server_node.put_tracker(p)
            lock.release()
            instance = dill.dumps(server_node)
            s.send(instance)
            answer = s.recv(4)
        else:
            for i in range(len(is_conected)):
                if is_conected[i] == int(port):
                    is_conected[i] = -1
        pack = str((my_ip,my_port))
        s.send(pack.encode())
        answer = s.recv(4)
        s.close()
    except:
        s.close()

def broadcast_client_auxiliar(ip,port,lista):
    global server_node
    s = socket.socket(type=socket.SOCK_STREAM)
    s.bind((ip,port))
    s.listen(1)
    sc , adr = s.accept()
    sc.settimeout(1)
    sc.send(b'tracker')
    answer = sc.recv(4)
    pack = str((ip,port-1000))
    sc.send(pack.encode())
    instance = b''
    while True:
        try:
            packet = sc.recv(1024)
            instance += packet
        except:
            break
    server_node = dill.loads(instance)
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


