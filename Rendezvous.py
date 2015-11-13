# -*- coding: utf-8 -*-

import socket
import pickle
import hashlib
import random
from Mensagem import Mensagem
NODE_MAX = 100

def gerarID(usedIDs):
    nodeID = random.randint(0, NODE_MAX)
    while (nodeID in usedIDs):
        nodeID = random.randint(0, NODE_MAX)
    usedIDs = usedIDs.append(nodeID)
    return nodeID, usedIDs

def main():
    rootID = -1
    rootIP = -1
    rootPort = -1
    nodeIDAddr = -1
    usedIDs = []
    DHTlocal = -1

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = ('localhost', 30000)
    sock.bind(server_address)

    while True:
        msgString, addr = sock.recvfrom(1024)
        msg = pickle.loads(msgString)

        # Tratamento do caso 0 (teste).
        if msg.op == -1 and msg.flagRoot == -1 and msg.nodeID == -1 and\
           msg.listaIDIP == -1 and msg.listaKeyValue == -1:
            print('Teste ok !!!')

        # Tratamento do caso 1 (Entrar na DHT).
        if msg.op == 1:
            msg = Mensagem()
            msg.op = 2
            msg.nodeID = gerarID(usedIDs)



if __name__ == "__main__":
    main()