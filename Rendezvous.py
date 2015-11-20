# -*- coding: utf-8 -*-

import socket
import pickle
import hashlib
import random
import time
import RDT
from Mensagem import Mensagem
NODE_MAX = 100

############################### Estado do Rendezvous ###############################
rootID = -1
rootAddr = -1
rootPort = -1
offerIDAddr = -1
seq = 0
nodeIDAddr = []
usedIDs = []
DHTlocal = []

############################### Definições das funções   ###############################
############################### que tratam cada mensagem ###############################
def gerarID(usedIDs):
    nodeID = random.randint(0, NODE_MAX)
    while (nodeID in usedIDs):
        nodeID = random.randint(0, NODE_MAX)
    usedIDs.append(nodeID)
    return nodeID, usedIDs

def entrarDHT(msg, sock, addr):
    global seq, usedIDs, rootID, rootAddr, offerIDAddr
    msgAns = Mensagem()
    msgAns.op = 2
    msgAns.seq = seq
    msgAns.ack = msg.seq
    msgAns.nodeID, usedIDs = gerarID(usedIDs)
    if rootID == -1:
        msgAns.flagRoot = 1
        offerIDAddr = (msgAns.nodeID, addr)
        print ("nó <===== op = 2 (newNodeAns) =====")
        msg, seq = RDT.rdt_send(msgAns, seq, sock, addr)
        if msg.op == 0:
            rootID = offerIDAddr[0]
            rootAddr = offerIDAddr[1]

############################### Main ###############################
def main():

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_addr = ('localhost', 30000)
    sock.bind(server_addr)


    while True:
        sock.settimeout(None)
        msgString, addr = sock.recvfrom(1024)
        msg = pickle.loads(msgString)

        # Tratamento do caso 0 (teste).
        if msg.op == -1 and msg.flagRoot == -1 and msg.nodeID == -1 and\
           msg.listaIDIP == -1 and msg.listaKeyValue == -1:
            print('Teste ok !!!')

        # Tratamento do caso 1 (Entrar na DHT).
        if msg.op == 1:
            print("op = 1 (newNode). Recebida.")
            entrarDHT(msg, sock, addr)


if __name__ == "__main__":
    main()