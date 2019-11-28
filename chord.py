import hashlib, sys, random, time, math

k = 16

class Identifier:
    def __init__(self,number,ip,port):
        self.identifier = str(number) + ip + str(port)
        self.identifier = hashlib.sha256(self.identifier.encode())

def between(n1,n2,n3):
    if n1 < n3:
        return n1 < n2 and n2 < n3
    else:
        return n1 < n2 or n2 < n3


def periodically(number):
    def decorator(function):
        def wrapper(*args,**kwargs):
            while True:
                time.sleep(number)
                function(*args,**kwargs)
        return wrapper
    return decorator  

class Node:
    def __init__(self,id):
        self.id = id
        self.m = int(math.log2(k))
        self.finger_table = [None] * self.m
        self.start = [None] * self.m
        for i in range(self.m):
            self.start[i] = (self.id + (2**i)) % (2**k)
        self.predeccessor = None

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
            shift = k - node_id
            node_id = 0
            node_successor = (node_successor + shift) % k
            id = (id + shift) % k
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
        while not self.betweenE(id,x.id,x.successor().id):
            x = x.closest_preceding_node(id)
        return x

    def find_successor(self,id):
        if self.betweenE(id,self.predeccessor.id,self.id):
            return self
        x = self.find_predecessor(id)
        return x.successor()

    def closest_preceding_node(self,id):
        for i in range(self.m - 1,-1,-1):
            finger_node = self.finger_table[i]
            if self.between(finger_node.id,self.id,id):
                return finger_node
        return self
    
    def init_finger_table(self,node):
        self.finger_table[0] = node.find_successor(self.start[0])
        self.predeccessor = self.successor().predeccessor
        self.successor().predeccessor = self
        self.predeccessor.finger_table[0] = self
        for i in range(self.m - 1):
            if self.Ebetween(self.start[i+1],self.id,self.finger_table[i].id):
                self.finger_table[i + 1] = self.finger_table[i]
            else:
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
        if node != self:
            self.init_finger_table(node)
            self.update_others()
            print(str(self.id) + ': ')
            for i in self.finger_table:
                print(i.id)
            print(str(node.id) + ': ')
            for i in node.finger_table:
                print(i.id)
        else:
            for i in range(self.m):
                self.finger_table[i] = self
            self.predeccessor = self
        

    @periodically(10)
    def stabilize(self):
        x = self.successor.predeccessor
        if self.open_open_interval(x.id,self.id,self.successor.id):
            self.successor = x
        self.successor.notify(self)

    def notify(self,node):
        if self.predeccessor is None or self.open_open_interval(node.id,self.predeccessor.id,self.id):
            self.predeccessor = node

    @periodically(10)
    def fix_finger(self):
        next = random.randint(1,self.m)
        self.finger_table[next] = self.find_successor(self.id + pow(2,next - 1))

    @periodically(10)
    def check_predeccessor(self):
        if self.predeccessor is not None:
            self.predeccessor = None

    




