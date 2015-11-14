# -*- coding: utf-8 -*-

import socket
import pickle
import hashlib
import copy
import time
import RDT
from Mensagem import Mensagem

nodeID = -1
root = -1
rootID = -1
rootAddr = -1
prevID = -1
prevAddr = -1
prevID2 = -1
prevAddr2 = -1
nextID = -1
nextAddr = -1
nextID2 = -1
nextAddr2 = -1
seq = 0
listaKeyValue = []

def testCom(sock, server_address):
    msg = Mensagem()
    msgString = pickle.dumps(msg)
    sock.sendto(msgString, server_address)

def newNode(sock, server_address):
    global seq, nodeID, root, rootID, rootAddr
    msg = Mensagem()
    msg.op = 1
    msg.seq = seq
    print("%s" % sock.getsockname)
    sock.bind(('localhost', 0))
    print("===== op = 1 (newNode) =====> rendezvous")
    msgR, seq = RDT.rdt_send(msg, seq, sock, server_address)
    # Caso a mensagem recebida seja uma op = 2 (newNodeAns)
    # e o nó seja indicado como root.
    if msgR.op == 2 and msgR.flagRoot == 1:
        nodeID = msgR.nodeID
        root = 1
        rootID = nodeID
        rootAddr = sock.getsockname()
        # Confirmando o recebimento da mensagem op = 2 (newNodeAns)
        # com um ack.
        msg = Mensagem()
        msg.op = 0
        msg.ack = msgR.seq
        msg.seq = seq
        msgString = pickle.dumps(msg)
        print("===== op = 0 (Ack) =====> rendezvous")
        sock.sendto(msgString, server_address)

    # Caso a mensagem recebida seja uma op = 2 (newnodeAns)
    # e o nó NÃO seja indicado como root.
    if msg.op == 2 and msg.flagRoot == 0:
        pass

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = ('localhost', 30000)

    while True:
        op = input("\
        Escolha uma opção:\n\
        0 - Testar comunicação.\n\
        1 - Imprimir estado.\n\
        2 - Imprimir entradas da DHT.\n\
        3 - Entrar na DHT.")

        if op == '0':
            testCom(sock, server_address)

        elif op == '1':
            print ("nodeID = %d, root = %d, rootID = %d, rootAddr = %s\n\
            prevID = %d, prevAddr = %s, prevID2 = %d, prevAddr2 = %s\n\
            nextID = %d, nextAddr = %s, nextID2 = %d, nextAddr2 = %s\n"
            % (nodeID, root, rootID, rootAddr, prevID, prevAddr, prevID2, prevAddr2,
            nextID, nextAddr, nextID2, nextAddr2)
            )

        elif op == '2':
            pass

        elif op == '3':
            newNode(sock, server_address)

if __name__ == "__main__":
    main()