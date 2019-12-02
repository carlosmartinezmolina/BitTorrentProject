import asyncio
import random
import os
import struct

#/home/carlos/Documents/PythonBook.pdf

class A:

    def __init__(self):
        self.clientes = 0
        self.copysize = 2**16

    async def parsingList(self,ipList):
        resultList = []
        ipList = ipList[1:-1]
        ipList = ipList.split(',')
        temp = None
        for i in range(len(ipList)):
            if i % 2 == 0:
                temp = ipList[i].split("'")
            else:
                resultList.append((temp[1],int(ipList[i][:-1])))
        return resultList

    async def tcp_echo_client(self, loop):
        # print("escriba el nombre del archivo a descargar")
        # m = input()#"Google I_O 2013 Keynote.mp4"
        # if len(m) == 0:
        #     print("no se van a descargar archivos")
        #     return
        # c = self.copysize


        print('type ip: ')
        ipTracker = '10.42.0.92'#input()
        print('type port: ')
        portTracker = 8888#int(input()) 

        r, w = await asyncio.open_connection(ipTracker, portTracker,
        loop = loop)
        
        a = await handshake(w,r)
        while True:
            ipList = await request(w,r)
            
            if len(ipList) > 0:
                break
        
        print('ok')
        w.close()


        if ipList[0] != 'exit':
            ipList = await self.parsingList(ipList)
            
            for ip, port in ipList:
                try:
                    reader, writer = await asyncio.open_connection(ip, port,
                    loop = loop)
                        
                    writer.write(m.encode())
                    await writer.drain()

                    data = await reader.read(4)
                    message = struct.unpack('I',data)
                    number_packs = message[0]
                    addr = writer.get_extra_info('peername')
                    print("Received %r from %r" % (number_packs, addr))

                    print("reading files")
                    archivo = []
                    for i in range(number_packs):
                        pack = await reader.read(c) #<<-------
                        archivo.append(pack)
                        print("pack %r ok" %i)
                        await asyncio.sleep(0.01)
                except:
                    pass

                # print('Close the socket')
                writer.close()

            #tengo el paquete completo!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            print('addrees to save the file')
            path = input()
            f = open(path,'ab+')
            for i in range(len(archivo)):
                f.write(archivo[i])
            f.close()
            print("file correctly downloaded")

    async def handle_echo(self, reader, writer):
        self.clientes +=1
        c = self.copysize#65536  #2^16
        data = await reader.read(c)
        message = data.decode()
        print(message)
        addr = writer.get_extra_info('peername')
        print("Received %r from %r" % (message, addr))
        size = 0
        path = message
        size += os.path.getsize(path)
        print('size = %r' % size)
        archivo = open(path,'rb')
        content = []
        sizefile = int(os.stat(path).st_size/c) + 1
        print(os.stat(path).st_size/c)
        if os.stat(path).st_size % c == 0:
            sizefile -=1

        print("")
        print("loading files")
        for _ in range(sizefile):
            content.append(archivo.read(c))
        archivo.close()
        print("files loaded")
        writer.write(struct.pack('I',len(content)))
        await writer.drain()

        print("sending package")
        for i in range(len(content)):
            print('aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa')
            writer.write(content[i])
            await writer.drain()
            #await asyncio.sleep(self.clientes/100)
            #print('pack %r sended' %i)
        
        print("Close the client socket")
        writer.close()
        self.clientes -= 1

#print("escribir ip")
#ip = '192.168.43.183'#input()
#print("escribir puerto")
#port = 8000#input()
async def handshake(w,r):
    w.write(b'hello')
    answer = await r.read(4)
    print(answer.decode())
    return None

async def request(w,r):
    print('type list to get the list of torrents')
    print('type download to ask for a file')
    print('type upload to share a file')
    print('type exit to end')
    entry = input()
    if entry == 'exit':
        w.write(b'exit')
        answer = await r.read(4)
        return ['exit']
    if entry == 'list':
        w.write(b'list')
        answer = await r.read(4)
        print(answer.decode())
        my_list = await r.read(1024)
        my_list = my_list.decode()
        print(my_list)
    if entry == 'download':
        w.write(b'download')
        answer = await r.read(4)
        print(answer.decode())
        print('type a filename: ')
        filename = input()
        w.write(filename.encode())
        ip_list = await r.read(1024)
        print(ip_list.decode())
        return ip_list.decode()
    if entry == 'upload':
        w.write(b'upload')
        answer = await r.read(4)
        # print(answer.decode())
        print('type a filename: ')
        filename = input()
        w.write(filename.encode())
    return []



print('type peerip: ')
ip = '10.42.0.92'#input()
print('type peerport: ')
port = 8080#int(input())

a = A()
loop = asyncio.get_event_loop()
coro = asyncio.start_server(a.handle_echo, ip, port, loop = loop)
loop.run_until_complete(asyncio.gather(a.tcp_echo_client(loop),coro))
loop.run_forever()