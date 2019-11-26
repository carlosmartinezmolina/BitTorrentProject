import chord, socket, struct

server_node = chord.Node(1)
server_node.join(server_node)

def create_node(number):
    new_node = chord.Node(number)
    new_node.join(server_node)


def begin_server():
    s = socket.socket(type=socket.SOCK_STREAM)

    s.bind(('127.0.0.1',8080))

    s.listen(5)

    

    while True:
        sc , adr = s.accept()
        pack = sc.recv(1024)
        sc.send(b'done')
        number = struct.unpack('I',pack)
        create_node(number[0])
        sc.close()

        
        
        

    
    s.close()

begin_server()