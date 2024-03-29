import hashlib, sys, random, time, math, threading

k = 160


def periodically(number):
    def decorator(function):
        def wrapper(*args,**kwargs):
            def _wrapper():
                while True:
                    time.sleep(number)
                    function(*args,**kwargs)
            th = threading.Thread(target = _wrapper)
            th.start()
        return wrapper
    return decorator  

class Node:
    def __init__(self,id):
        self.id = id
        self.storage = {}
        self.info = {}
        self.trackers = []
        self.m = int(math.log2(k))
        self.finger_table = [None] * self.m
        self.start = [None] * self.m
        for i in range(self.m):
            self.start[i] = (self.id + (2**i)) % (2**k)
        for i in range(self.m):
            self.finger_table[i] = self
        self.predeccessor = self
        self.stabilize()
        self.fix_finger()

    def is_there(self,id,list=[]):
        if list.__contains__(self.successor().id):
            return False
        if self.successor().id == id:
            return True
        else:
            list.append(self.id)
            return self.successor().is_there(id,list) 

    def get_key(self,key):
        node = self.closest_preceding_node(key).successor()
        if key in self.storage:
            return self.storage[key], self.info[key]
        return None

    def get_info(self,id,my_list):
        if self.successor().id == id:
            for i in self.successor().info.values():
                if not my_list.__contains__(i['info']['name']):
                    my_list.append(i['info']['name'])
            return my_list
        else:
            for i in self.info.values():
                if not my_list.__contains__(i['info']['name']):
                    my_list.append(i['info']['name'])
            self.successor().get_info(id,my_list)
            return my_list

    def get_trackers(self,id,my_list):
        if self.successor().id == id:
            for i in self.successor().trackers:
                if not my_list.__contains__(i):
                    my_list.append(i)
            return my_list
        else:
            for i in self.trackers:
                if not my_list.__contains__(i):
                    my_list.append(i)
            self.successor().get_trackers(id,my_list)
            return my_list

    
    def replicar(self,node,key,value,pack):
        if key not in self.info:
            self.info[key] = pack
        if key not in node.storage:
            node.storage[key] = [value]
        else:
            if not node.storage[key].__contains__(value):
                node.storage[key].append(value)

    def replica(self,key,value,pack):
        replicados = []
        replicados.append(self.id)
        if not replicados.__contains__(self.successor().id):
            self.replicar(self.successor(),key,value,pack)
        if self.m > 1 and not replicados.__contains__(self.finger_table[1].id):
            self.replicar(self.finger_table[1],key,value,pack)


    def put_tracker(self,ip_port):
        if not self.trackers.__contains__(ip_port):
            self.trackers.append(ip_port)
        return
        
    def put_key(self,key,value,pack):
        if key not in self.info:
            self.info[key] = pack
        if key not in self.storage:
            self.storage[key] = [value]
        else:
            if not self.storage[key].__contains__(value):
                self.storage[key].append(value)
        
        self.replica(key,value,pack)
        
        



    def decr(self,value, size):
        if size <= value:
            return value - size
        return (2**k) - (size - value)

    def successor(self):
        return self.finger_table[0]

    def between(self,id,node_id,node_successor):
        if node_id == node_successor:
            return True
        elif node_id > node_successor:
            shift = 2**k - node_id
            node_id = 0
            node_successor = (node_successor + shift) % 2**k
            id = (id + shift) % 2**k
        return node_id < id < node_successor
    def Ebetween(self,id,node_id,node_successor):
        if id == node_id:
            return True
        return self.between(id,node_id,node_successor)
    def betweenE(self,id,node_id,node_successor):
        if id == node_successor:
            return True
        return self.between(id,node_id,node_successor) 

    def find_predecessor(self,id):
        if id == self.id:
            return self.predeccessor
        x = self
        # print(str(id) + '   ' + str(x.id) + '   ' + str(x.successor().id))
        # print(self.betweenE(id,x.id,x.successor().id))
        while not self.betweenE(id,x.id,x.successor().id):
            x = x.closest_preceding_node(id)
        return x

    def find_successor(self,id):
        # print('successor ' + str(id))
        if self.betweenE(id,self.predeccessor.id,self.id):
            return self
        x = self.find_predecessor(id)
        # print('termino find successor')
        return x.successor()

    def closest_preceding_node(self,id):
        for i in range(self.m - 1,-1,-1):
            finger_node = self.finger_table[i]
            if self.between(finger_node.id,self.id,id):
                return finger_node
        return self
    
    def init_finger_table(self,node):
        # print('finger table ' + str(node.id))
        self.finger_table[0] = node.find_successor(self.start[0])
        # print('middle ' + str(self.successor().id))
        self.predeccessor = self.successor().predeccessor
        self.successor().predeccessor = self
        self.predeccessor.finger_table[0] = self
        # print('avanced ' + str(self.predeccessor.id))
        for i in range(self.m - 1):
            if self.Ebetween(self.start[i+1],self.id,self.finger_table[i].id):
                self.finger_table[i + 1] = self.finger_table[i]
                # print('entro al if')
            else:
                # print('no entro al if')
                self.finger_table[i + 1] = node.find_successor(self.start[i+1])
        

    def update_finger_table(self,s,i):
        if self.id != s.id and self.Ebetween(s.id,self.id,self.finger_table[i].id):
            self.finger_table[i] = s
            p = self.predeccessor
            p.update_finger_table(s,i)

    def update_others(self):
        for i in range(self.m):
            prev = self.decr(self.id,2**i)
            p = self.find_predecessor(prev)
            if prev == p.successor().id:
                p = p.successor()
            p.update_finger_table(self,i)

    def join(self,node):
        if node.id != self.id:
            # print('entro')
            self.init_finger_table(node)
            # print('finger')
            self.update_others()
            # print('----+++++')
            # print(str(self.id%10000) + ': ')
            # print(self.finger_table[0].id%10000)
            # print(self.finger_table[1].id%10000)
            # print(self.finger_table[2].id%10000)
            # print(self.finger_table[3].id%10000)
            # print('Predecesor: ' + str(self.predeccessor.id))
            # print('Sucesor: ' + str(self.successor().id))
            # print('-----')
            # print(str(self.predeccessor.id) + ': ')
            # print('Predecesor: ' + str(self.predeccessor.predeccessor.id))
            # print('Sucesor: ' + str(self.predeccessor.successor().id))
            # print('+++++')
            # print(str(self.successor().id) + ': ')
            # print('Predecesor: ' + str(self.successor().predeccessor.id))
            # print('Sucesor: ' + str(self.successor().successor().id))
        

    @periodically(2)
    def stabilize(self):
        x = self.successor().predeccessor
        if self.between(x.id,self.id,self.successor().id):
            self.finger_table[0] = x
        self.successor().notify(self)

    def notify(self,node):
        if self.predeccessor is None or self.between(node.id,self.predeccessor.id,self.id):
            self.predeccessor = node

    @periodically(2)
    def fix_finger(self):
        next = random.randint(0,self.m - 1)
        self.finger_table[next] = self.find_successor(self.start[next])


    




