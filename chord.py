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

class Node:
    def __init__(self):
        self.id = 1
        self.m = 6
        self.finger = []
        self.successor = self.finger[0].id

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
    
    