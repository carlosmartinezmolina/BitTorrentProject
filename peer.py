import asyncio, os, struct, socket, broad, random, dill


class A:

    def __init__(self, ip, port):
        self.clientes = 0
        self.copysize = 1024
        self.port = port
        self.ip = ip
        self.downloadFileName = None
        self.uploadName = None
        self.download_info = None
        self.downloadsize = 0
        self.temp = 0
        self.resto = 0

    async def parsingList(self, ipList):
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

        c = self.copysize
        archivo = []
        ipList = None

        ip_temp = random.randint(8000,65000)
        print('buscando tracker')
        ipTracker, portTracker = broad.broadcast_client(self.ip, ip_temp)
        print(portTracker)
        try:
            r, w = await asyncio.open_connection(ipTracker, portTracker,
            loop = loop)
            
            a = await self.handshake(w, r)

            while True: 
                ipList = await self.request(w, r)
                if ipList is None or len(ipList) > 0:
                    break
            w.close()
        except:
            pass
        m = self.downloadFileName
        
        if ipList is not None and ipList[0] != 'exit':
            path = './files/' + self.downloadFileName
            f = open(path,'ab+')
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
                    self.temp = number_packs

                    
                    current = str(self.downloadsize)
                    writer.write(current.encode())
                    number_packs -= self.downloadsize                    

                    print("reading files")
                    print(' cantidad a descargar  %r'%number_packs)
                    for i in range(number_packs):
                        pack = await reader.read(c) #<<-------
                        if len(pack) != c and i < number_packs - 1:
                            break
                        #archivo.append(pack)
                        f.write(pack)
                        self.downloadsize += 1
                        print("pack %r ok" %self.downloadsize)
                        await asyncio.sleep(0.01)
                    writer.close()
                except:
                    pass
                if self.downloadsize != 0 and self.downloadsize == self.download_info['info']['length']:
                    break
                await asyncio.sleep(3)
            f.close()
            if self.downloadsize == self.download_info['info']['length']:
                print("file correctly downloaded")
            else:
                print('download failed')
        await asyncio.sleep(1)

    async def handle_echo(self, reader, writer):

        self.clientes +=1
        c = self.copysize

        try:
            data = await reader.read(c)
            message = data.decode()
            addr = writer.get_extra_info('peername')
            print("Received %r from %r" % (message, addr))
            size = 0
            path = './files/' + message
            size += os.path.getsize(path)
            print('size = %r' % size)
            archivo = open(path,'rb')
            content = []
            sizefile = int(os.stat(path).st_size/c) + 1
            print(os.stat(path).st_size/c)
            if os.stat(path).st_size % c == 0:
                sizefile -=1

            if sizefile > 0:
                writer.write(struct.pack('I',sizefile))

                temp = await reader.read(4)
                current = int(temp.decode())

                for _ in range(current):
                    x = archivo.read(c)
                
                sizefile -= current
                
                print("loading files")
                for _ in range(sizefile):
                    content.append(archivo.read(c))
                archivo.close()

                print("sending package")
                for i in range(len(content)):
                    writer.write(content[i])
                    await asyncio.sleep(self.clientes/100)                
                    
        except:
            pass
        
        print("Close the client socket")
        try:
            writer.close()
        except:
            pass

        self.clientes -= 1

    async def handshake(self, w, r):
        w.write(b'cliente')
        answer = await r.read(4)
        w.write(b'-1')
        answer = await r.read(4)
        port = str(self.port)
        w.write(port.encode())
        answer = await r.read(4)
        w.write(b'updato_trackers')
        answer = await r.read(4)
        return None

    async def request(self, w, r):
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
            my_list = await r.read(1024)
            my_list = my_list.decode()
            print(my_list)
        if entry == 'download':
            w.write(b'download')
            answer = await r.read(4)
            print('type a filename: ')
            filename = input()
            self.downloadFileName = filename
            w.write(filename.encode())            
            ip_list = await r.read(1024)
            w.write(b'done')
            torrent = await r.read(1024)
            w.write(b'done')
            my_dict = dill.loads(torrent)
            self.download_info = my_dict
            a = ip_list.decode()
            b = await self.parsingList(a)
            return b
        if entry == 'upload':
            w.write(b'upload')
            answer = await r.read(4)
            print('type a filename: ')
            filename = input()
            self.uploadName = filename
            addr = w.get_extra_info('peername')
            info = await self.metaInfo(addr)
            instance = dill.dumps(info)
            w.write(instance)            
        return []

    async def metaInfo(self, adr):
        c = self.copysize
        d = {}
        data = {}        
        d['piece_length'] = 1024
        size = 0
        path = './files/' + self.uploadName
        size += os.path.getsize(path)
        sizefile = int(os.stat(path).st_size/c) + 1
        if os.stat(path).st_size % c == 0:
            sizefile -=1
        d['name'] = self.uploadName
        d['length'] = sizefile
        data['info'] =  d
        data['adr'] = adr
        return data
print('Escribe el ip de tu maquina')
ip = input()
port = int(input())#random.randint(8000,65000)
print(port)

a = A(ip, port)
loop = asyncio.get_event_loop()
coro = asyncio.start_server(a.handle_echo, ip, port, loop = loop)
loop.run_until_complete(asyncio.gather(a.tcp_echo_client(loop), coro))
loop.run_forever()