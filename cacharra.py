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