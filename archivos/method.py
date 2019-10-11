import socket, os, struct


def geting_pack(sc):
    pack = sc.recv(4)
    sc.send(b'done')
    number_packs = struct.unpack('I',pack)
    print(number_packs[0])

    archivo = []
    for i in range(number_packs[0]):
        pack = sc.recv(1024)
        archivo.append(pack)
    sc.send(b'done')
    return archivo

def creating_file(path,content):
    archivo = open(path,'ab+')
    for i in range(len(content)):
        archivo.write(content[i])

def making_file():
    path = input()
    archivo = open(path,'rb')
    content = []
    sizefile = int(os.stat(path).st_size/1024) + 1
    for i in range(sizefile):
        content.append(archivo.read(1024))
    return path, content

def sending_file(s,mensaje):
    s.send(struct.pack('I',len(mensaje)))
    answer = s.recv(4)

    for i in range(len(mensaje)):
        s.send(mensaje[i])
    answer = s.recv(4)
    print('yes')