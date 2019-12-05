import chord, socket, struct, hashlib, sys, threading, time, dill, random

server_node = None
tracker_list = []
is_conected = []

def create_node(ip,port):
    global server_node
    h = str(port)
    h = hashlib.sha256(h.encode())
    n = int.from_bytes(h.digest(),byteorder = sys.byteorder) % 2**chord.k
    if not server_node.is_there(n) == n:
        new_node = chord.Node(n)
        new_node.join(server_node)
        if not tracker_list.__contains__((ip,port)):
            thr = threading.Thread(target = update_remote_trackers,args = (ip,port,))
            thr.start()

def handshake(sc):
    pack = sc.recv(1024)
    #print(pack.decode())
    if pack.decode() == 'hello':
        sc.send(b'done')

def upload_remote_trackers(ip,port,upload_info):
    for i in tracker_list:
        s = socket.socket(type=socket.SOCK_STREAM)
        try:
            s.connect(i)
            s.send(b'hello')
            answer = s.recv(4)
            pack = str(port)
            s.send(pack.encode())
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
    for i in tracker_list:
        s = socket.socket(type=socket.SOCK_STREAM)
        try:
            s.connect(i)
            s.send(b'hello')
            answer = s.recv(4)
            pack = str(port)
            s.send(pack.encode())
            answer = s.recv(4)
            s.send(b'update')
            answer = s.recv(4)
            pack = str((ip,port))
            s.send(pack.encode())
            answer = s.recv(4)
            s.close()
        except:
            s.close()

def request(sc,adr):
    global server_node
    create_node(adr[0],adr[1])
    while True:
        try:
            pack = sc.recv(1024)
            if len(pack) == 0:
                    break
        except:
            break
        if pack.decode() == 'exit':
            sc.send(b'done')
            break
        if pack.decode() == 'list':
            sc.send(b'done')
            torrent_list = []
            torrent_list = server_node.get_info(server_node.id,torrent_list)
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
            server_node.put_key(n,adr,pack.decode())
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
            ip_list = server_node.put_key(n,adr,pack.decode())
            thr = threading.Thread(target = upload_remote_trackers,args = (adr[0],adr[1],pack.decode(),))
            thr.start()
        if pack.decode() == 'update':
            sc.send(b'done')
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
            create_node(address[0],address[1])
            break
        if pack.decode() == 'remote_upload':
            sc.send(b'done')
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
            h = hashlib.sha256(pack)
            n = int.from_bytes(h.digest(),byteorder = sys.byteorder) % 2**chord.k
            ip_list = server_node.put_key(n,address,pack.decode())
            break

def auxiliar(sc,adr):
    handshake(sc)
    pack = sc.recv(1024)
    #print('server ' + pack.decode())
    pack = int(pack.decode())
    sc.send(b'done')
    boolean = True
    while boolean:
        boolean = request(sc,(adr[0],pack))
    #print('close')
    sc.close()

def call_broadcast_client(ip,port):
    global server_node
    global tracker_list
    ip_tracker = broadcast_client(ip,port)
    tracker_list.append(ip_tracker)
    print('encontre con el broadcast al ' + str(ip_tracker))
    s = socket.socket(type=socket.SOCK_STREAM)
    try:
        s.connect(ip_tracker)
        s.send(b'hello')
        answer = s.recv(4)
        pack = str(port)
        s.send(pack.encode())
        answer = s.recv(4)
        s.send(b'exit')
        answer = s.recv(4)
        #print('yes')
        s.close()
        create_node(ip,port)
    except:
        s.close()

def begin_server():
    global server_node
    s = socket.socket(type=socket.SOCK_STREAM)
    #print('type ip: ')
    ip = '191.121.116.27'#input()
    #print('type port: ')
    port = random.randint(8000,65000)#int(input())
    x = str(port)
    x = hashlib.sha256(x.encode())
    x = int.from_bytes(x.digest(),byteorder = sys.byteorder) % 2**chord.k
    print(x%10000)
    s.bind((ip,port))
    s.listen(10)

    print('type of node')
    type_node = input()
    if type_node == 'initial':
        h = str(port)
        h = hashlib.sha256(h.encode())
        n = int.from_bytes(h.digest(),byteorder = sys.byteorder) % 2**chord.k
        server_node = chord.Node(n)
        server_node.join(server_node)
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
                #print(data.decode())
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
    #print(lista[0])
    return lista[0]

def broadcast_server_auxiliar(ip,port,my_ip,my_port):
    global server_node
    global is_conected
    s = socket.socket(type=socket.SOCK_STREAM)
    try:
        s.connect((ip,int(port) + 1000))
        answer = s.recv(7)
        print(answer.decode())
        print('conection from ' + str(int(port) + 1000))
        if answer.decode() == 'tracker':
            print('un tracker se esta uniendo')
            instance = dill.dumps(server_node)
            s.send(instance)
            answer = s.recv(4)
            #print('llego el pakete ' + answer.decode())
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
    sc.send(b'tracker')
    instance = b''
    while True:
        packet = sc.recv(1024)
        if not packet:
            break
        instance += packet
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


