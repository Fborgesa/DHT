# -*- coding: utf-8 -*-

import socket
import pickle
import hashlib
import random
import time
import _thread
import RDT
from Mensagem import Mensagem
NODE_MAX = 100

############################### Estado do Rendezvous ###############################
rootID = -1
rootAddr = -1
offerIDAddr = (-1, '-1')
seq = 0
lastOp = -1
listaIDAddr = []
usedIDs = []
DHTlocal = []
msg = -1
msgString = -1
msgR = Mensagem()
msgStringR = -1

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_addr = ('localhost', 30000)

############################### Thread Menu ###############################
def threadMenu():
    global rootID, rootAddr, offerIDAddr, seq, lastOp,\
    listaIDAddr, usedIDs, DHTlocal, msg, msgString, msgR, msgStringR,\
    sock, server_addr

    while True:
        op = input("\
        Escolha uma opção:\n\
        1 - Imprimir estado.\n\
        2 - Imprimir entradas da DHT.\n")

        if op == '1':
            print ("\trootID = %d, rootAddr = %s, lastOP = %d, offerIDAddr = %s\n\
                    listaIDAdrr: %s\n"\
                   % (rootID, rootAddr, lastOp, offerIDAddr, listaIDAddr))

        elif op == '2':
            pass

############################### Definições das funções   ###############################
############################### que tratam cada mensagem ###############################
def sendNWait(addr):
    global rootID, rootAddr, offerIDAddr, seq, lastOp,\
    listaIDAddr, usedIDs, DHTlocal, msg, msgString, msgR, msgStringR,\
    sock, server_addr

    msg.ack = msgR.seq
    msg.seq = seq
    lastOp = msg.op
    if msg.op != 0:
        sock.settimeout(2)
    msgString = pickle.dumps(msg)
    sock.sendto(msgString, addr)
    time.sleep(3)

def gerarID():
    global usedIDs

    nodeID = random.randint(0, NODE_MAX)
    while (nodeID in usedIDs):
        nodeID = random.randint(0, NODE_MAX)
    usedIDs.append(nodeID)
    return nodeID

def newNode_newNodeAns(addr):
    global rootID, rootAddr, rootPort, offerIDAddr, seq, lastOp,\
    nodeIDAddr, usedIDs, DHTlocal, msg, msgString, msgR, msgStringR,\
    sock, server_addr

    msg = Mensagem()
    msg.op = 2
    msg.nodeID = gerarID()
    if rootID == -1:
        msg.flagRoot = 1
        offerIDAddr = (msg.nodeID, addr)
        print ("nó <===== op = 2 (newNodeAns) =====")
        sendNWait(addr)
    else:
        msg.flagRoot = 0
        offerIDAddr = (msg.nodeID, addr)
        msg.listaIDAddr.append(listaIDAddr[0])
        print ("nó <===== op = 2 (newNodeAns) =====")
        sendNWait(addr)

############################### Main ###############################
def main():
    global rootID, rootAddr, offerIDAddr, seq, lastOp,\
    listaIDAddr, usedIDs, DHTlocal, msg, msgString, msgR, msgStringR,\
    sock, server_addr

    sock.bind(server_addr)

    # Variáveis que definem quantos timeouts ocorreram e quantos números de sequência
    # chegaram dessincronizados.
    timeOuts = 0
    seqNum = 0
    addr = server_addr

    try:
        t = _thread.start_new_thread(threadMenu, ())

    except:
        print("Falha ao inicializar as threads.")

    while True:
        try:
            msgStringR, addr = sock.recvfrom(1024)
            time.sleep(1)
            msgR = pickle.loads(msgStringR)
            print("op = %d. Recebida." % msgR.op)
#            print ("msg.ack = %d. seq = %d." % (msgR.ack, seq))

            # Caso a mensagem chegue com o número de sequência dessicronizado.
            if sock.gettimeout() != None and msgR.ack != seq:
                print("Número de sequência dessincronizado.")
                msgR.op = -2
                if seqNum == 2:
                    sock.settimeout(None)
                    timeOuts = 0
                    seqNum = 0
                else:
                    print("Reenvio ===== op = %d =====>" % msg.op)
                    sock.sendto(msgString, addr)
                    seqNum = seqNum + 1

            # Caso a mensagem chegue corretamente.
            else:
                sock.settimeout(None)
                timeOuts = 0
                seqNum = 0
                seq = (seq - 1 if seq == 1 else seq + 1)

        # Caso a resposta não chegue.
        # O Node tenta reenviar a mensagem 2 vezes, Caso o destino não responda ele desiste.
        except socket.timeout:
            print ("Destino não responde.")
            msgR.op = -2
            if timeOuts == 2:
                sock.settimeout(None)
                timeOuts = 0
                seqNum = 0
            else:
                print("Reenvio ===== op = %d =====>" % msg.op)
                sock.sendto(msgString, addr)
                timeOuts = timeOuts + 1

        ### Tratamento de cada caso ###
        # Tratamento do caso 0 (teste).
        if msgR.op == -1 and msgR.flagRoot == -1 and msgR.nodeID == -1 and\
           msgR.listaIDIP == -1 and msgR.listaKeyValue == -1:
            print('Teste ok !!!')

        if msgR.op == 0 and lastOp == 2:
            rootID = offerIDAddr[0]
            rootAddr = offerIDAddr[1]
            listaIDAddr.append(offerIDAddr)

        # Tratamento do caso 1 (Entrar na DHT).
        if msgR.op == 1:
            newNode_newNodeAns(addr)


if __name__ == "__main__":
    main()