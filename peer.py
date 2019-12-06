import asyncio, os, struct, socket, broad, random, dill


class A:

    def __init__(self, ip, port):
        self.clientes = 0
        self.copysize = 1024
        self.port = port
        self.ip = ip
        self.downloadFileName = None
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

        ip_temp = random.randint(8000,65000)#input()
        ipTracker, portTracker = broad.broadcast_client(self.ip, ip_temp)
        print('-------------------------------------------------------')
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
            print('se perdio la conexion con el tracker')

        m = self.downloadFileName
        
        if ipList is not None and ipList[0] != 'exit':


            for ip, port in ipList:
                try:
                    reader, writer = await asyncio.open_connection(ip, port,
                    loop = loop)

                    writer.write(m.encode())
                    await writer.drain()                    
                    #/home/eziel/Documents/PythonBook.pdf
                    print('+++++++++++++++++++++++++++++++++++++++++++++++++++')
                    data = await reader.read(4)
                    print('+++++++++++++++++++++++++++++++++++++++++++++++++++')

                    message = struct.unpack('I',data)

                    number_packs = message[0]
                    addr = writer.get_extra_info('peername')
                    print("Received %r from %r" % (number_packs, addr))
                    self.temp = number_packs

                    #lo q ya se copio
                    current = str(self.downloadsize)
                    writer.write(current.encode())
                    number_packs -= self.downloadsize                    

                    print("reading files")
                    print('cantidad a descargar%r'%number_packs)
                    for i in range(number_packs):
                        pack = await reader.read(c) #<<-------
                        if len(pack) != c and i < number_packs - 1:
                            break
                        archivo.append(pack)
                        self.downloadsize += 1
                        #print("pack %r ok" %i)
                        await asyncio.sleep(0.01)
                    writer.close()
                except:
                    pass
                if self.downloadsize != 0 and self.downloadsize == self.temp:
                    break
                await asyncio.sleep(3)

            print('tamanno del archivo %r'%len(archivo))
            
            if len(archivo) == self.temp and self.temp > 0:
                #tengo el paquete completo!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                print("saving file")
                #print('addrees to save the file')
                #/home/eziel/Downloads
                #/home/eziel/Documents/PythonBook.pdf
                s=self.downloadFileName.split('/')
                t = s[len(s)-1]
                path = '/home/eziel/Downloads/' + t
                f = open(path,'ab+')
                for i in range(len(archivo)):
                    f.write(archivo[i])
                    #print(len(archivo[i]))
                f.close()
                print("file correctly downloaded")
            else:
                print('download failed')

    async def handle_echo(self, reader, writer):

        self.clientes +=1
        c = self.copysize#65536  #2^16

        try:
            data = await reader.read(c)
            message = data.decode()
            print('=====================================================')
            print(message)
            addr = writer.get_extra_info('peername')
            print("Received %r from %r" % (message, addr))
            size = 0
            path = message
            print(path)
            size += os.path.getsize(path)
            print('size = %r' % size)
            archivo = open(path,'rb')
            content = []
            sizefile = int(os.stat(path).st_size/c) + 1
            print(os.stat(path).st_size/c)
            if os.stat(path).st_size % c == 0:
                sizefile -=1

            print('tamanno del archivo')            
            print(sizefile)
            if sizefile > 0:
                writer.write(struct.pack('I',sizefile))

                temp = await reader.read(4)
                current = int(temp.decode())

                #lo q ya se envio
                for _ in range(current):
                    x = archivo.read(c)
                
                sizefile -= current
                
                print("loading files")
                for _ in range(sizefile):
                    content.append(archivo.read(c))
                archivo.close()

                print("sending package")
                print('cantidad a enviar%r'%len(content))
                for i in range(len(content)):
                    writer.write(content[i])
                    #print(len(content[i]))
                    await asyncio.sleep(0.01)                
                    #print('pack %r sended' %i)
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
        print(answer.decode())
        port = str(self.port)
        w.write(port.encode())
        print('puerto enviado al tracker %r' %self.port)        
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
            self.downloadFileName = filename
            w.write(filename.encode())
            ip_list = await r.read(1024)
            a=ip_list.decode()
            print(ip_list.decode())
            b = await self.parsingList(a)
            return b
        if entry == 'upload':
            w.write(b'upload')
            answer = await r.read(4)
            print('type a filename: ')
            filename = input()
            serializado = dill.dumps(filename)
            w.write(serializado)
        return []

print('escribe el ip de tu maquina')
ip = input()
port = random.randint(8000,65000)

a = A(ip, port)
loop = asyncio.get_event_loop()
coro = asyncio.start_server(a.handle_echo, ip, port, loop = loop)
loop.run_until_complete(asyncio.gather(a.tcp_echo_client(loop), coro))
loop.run_forever()