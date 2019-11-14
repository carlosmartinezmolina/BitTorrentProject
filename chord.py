import hashlib, sys, random, time

class Identifier:
    def __init__(self,number,ip,port):
        self.identifier = str(number) + ip + str(port)
        self.identifier = hashlib.sha256(self.identifier.encode())

def between(n1,n2,n3):
    if n1 < n3:
        return n1 < n2 and n2 < n3
    else:
        return n1 < n2 or n2 < n3


x = Identifier(5,'192.168.0.1',3128)
#print(x.identifier.digest())

def periodically(number):
    def decorator(function):
        def wrapper(*args,**kwargs):
            while True:
                time.sleep(number)
                function(*args,**kwargs)
        return wrapper
    return decorator    

class Node:
    def __init__(self):
        self.id = 1
        self.m = 6
        self.finger = [0]
        #self.successor = self.finger[0].id
        self.predeccessor = None

    def open_open_interval(self,id,node_id,node_successor):
        return id > node_id and id < node_successor
    def open_close_interval(self,id,node_id,node_successor):
        return id > node_id and id <= node_successor
    def close_open_interval(self,id,node_id,node_successor):
        return id > node_id and id < node_successor

    def find_predecessor(self,id):
        x = self
        while not open_close_interval(id,x,x.successor):
            x = x.closest_preceding_node(id)
        return x

    def find_successor(self,id):
        x = self.find_predecessor(id)
        return x.successor

    def closest_preceding_node(self,id):
        for i in range(self.m,-1):
            finger_node = self.finger[i]
            if open_open_interval(finger_node.id,self.id,id):
                return finger_node
        return self
    
    def init_finger_table(self,node):
        self.successor = node.find_successor(self.id + 1)
        self.predeccessor = self.successor.predeccessor
        self.successor.predeccessor = self

    def update_finger_table(self,s,i):
        if close_open_interval(s.id,self.id,self.finger[i].id):
            self.finger[i] = s
            p = self.predeccessor
            p.update_finger_table(s,i)

    def update_others(self):
        for i in range(0,self.m):
            p = self.find_predecessor(self.id - pow(2,i - 1))
            p.update_finger_table(self,i)

    def join(self,node):
        if node is not None:
            init_finger_table(node)
            update_others()
        else:
            for i in range(0,self.m):
                self.finger[i] = n
            self.predeccessor = n
        

    def create(self):
        self.predeccessor = None
        self.successor = self


    @periodically(10)
    def stabilize(self):
        x = self.successor.predeccessor
        if interval(x,self.id,self.successor):
            self.successor = x
        self.successor.notify(self)

    def notify(self,node):
        if self.predeccessor is None or interval(node.id,self.predeccessor.id,self.id):
            self.predeccessor = node

    @periodically(10)
    def fix_finger(self):
        next = next + 1
        if next > self.m:
            next = 1
        self.finger[next] = self.find_successor(n + pow(2,next - 1))

    @periodically(10)
    def check_predeccessor(self):
        if self.predeccessor is not None:
            self.predeccessor = None

    




