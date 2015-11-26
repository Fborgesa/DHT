# -*- coding: utf-8 -*-

import socket
import pickle
import hashlib
import random
import time
import _thread
import RDT
from Mensagem import Mensagem
NODE_MAX = 256

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
addrLastSent = server_addr

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
            print ("\trootID = %s, rootAddr = %s, lastOP = %s, offerIDAddr = %s\n\
                    listaIDAdrr: %s\n"\
                   % (rootID, rootAddr, lastOp, offerIDAddr, listaIDAddr))

        elif op == '2':
            pass

############################### Definições das funções   ###############################
############################### que tratam cada mensagem ###############################
def sendNWait(addr):
    global rootID, rootAddr, offerIDAddr, seq, lastOp,\
    listaIDAddr, usedIDs, DHTlocal, msg, msgString, msgR, msgStringR,\
    sock, server_addr, addrLastSent

    msg.ack = msgR.seq
    msg.seq = seq
    lastOp = msg.op
    if msg.op != 'ack':
        sock.settimeout(2)
    msgString = pickle.dumps(msg)
    addrLastSent = addr
    print("%s Enviada ===== op = %s =====> %s" % (sock.getsockname(), msg.op, addr))
    sock.sendto(msgString, addr)
    time.sleep(1)

def dist(a,b):
    if (a == b):
        return 0
    elif (a < b):
        return b-a
    else:
        return 256 + b - a

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
    msg.op = 'newNodeAns'
    msg.nodeID = gerarID()
    if rootID == -1:
        msg.flagRoot = 1
        offerIDAddr = (msg.nodeID, addr)
        sendNWait(addr)
    else:
        msg.flagRoot = 0
        offerIDAddr = (msg.nodeID, addr)
        msg.listaIDAddr.append(listaIDAddr[0])
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

    try:
        t = _thread.start_new_thread(threadMenu, ())

    except:
        print("Falha ao inicializar as threads.")

    while True:
        try:
            msgStringR, addrR = sock.recvfrom(1024)
            time.sleep(1)
            msgR = pickle.loads(msgStringR)
            print("%s Recebida <===== op = %s ===== %s" % (sock.getsockname(), msgR.op, addrR))
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
                    print("Reenvio %s ===== op = %s =====> %s" % (sock.getsockname(), msg.op, addrLastSent))
                    sock.sendto(msgString, addrLastSent)
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
                print("Reenvio %s ===== op = %s =====> %s" % (sock.getsockname(), msg.op, addrLastSent))
                sock.sendto(msgString, addrLastSent)
                timeOuts = timeOuts + 1

        ### Tratamento de cada caso ###
        # Tratamento do caso 0 (teste).
        if msgR.op == -1 and msgR.flagRoot == -1 and msgR.nodeID == -1 and\
           msgR.listaIDAddr == [] and msgR.listaKeyValue == []:
            print('Teste ok !!!')

        if msgR.op == 'ack' and lastOp == 'newNodeAns':
            rootID = offerIDAddr[0]
            rootAddr = offerIDAddr[1]
            listaIDAddr.append(offerIDAddr)
            listaIDAddrSort = sorted(listaIDAddr, key=lambda tup: tup[0])
            print ("\nDHT local:")
            for entry in listaIDAddrSort:
                print( "%s ===>" % (entry,) )
            print("\n")

        if msgR.op == 'newNode':
            newNode_newNodeAns(addrR)

if __name__ == "__main__":
    main()