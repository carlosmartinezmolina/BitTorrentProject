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

    def interval(self,id,node_id,node_successor):
        return id >= node_id and id <= node_successor

    def closest_preceding_node(id):
        for i in range(self.m,-1):
            finger_node = self.finger[i]
            if interval(finger_node.id,self.id,id):
                return finger_node
        return self

    def find_successor(id):
        if interval(id,self.id,self.successor):
            return self.successor
        n = closest_preceding_node(id)
        return n.find_successor(id)
    
    def create(self):
        self.predeccessor = None
        self.successor = self

    def join(self,node):
        self.predeccessor = None
        self.successor = node.find_successor(self.id)

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

    




