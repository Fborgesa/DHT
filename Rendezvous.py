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
                    listaIDAddr: %s\n"\
                   % (rootID, rootAddr, lastOp, offerIDAddr, listaIDAddr))

        elif op == '2':
            pass
############################## MOSTRA TOPOLÓGIA DAS ENTRADAS DOS NÓs ##################
############################################################################
def showTpoligi(DHTLocal):

    tamList = len(DHTLocal)
    Pini = 0

    if(len(DHTLocal) - 1 == 0):
        rtN = DHTLocal[0][0]
        print('Primeira entrada no DHT:\n\nrtN(%d)' %  (DHTLocal[0][0]))
    elif (len(DHTLocal) > 1):
        if(tamList%2 == 0):
            while ((Pini+1) != tamList):
                if (DHTLocal[Pini][0] == rtN):
                    if(Pini == 0):
                        print('<--->%d<--->rtN(%d)<--->' % (DHTLocal[tamList][0], DHTLocal[Pini][0]))
                        Pini = Pini+1
                        tamList = tamList-1
                    else:
                        pass
                elif (DHTLocal[tamList][0] == rtN):
                    if(len(DHTLocal) == tamList):
                        print('<--->rtN(%d)<--->%d<--->' % (DHTLocal[tamList][0], DHTLocal[Pini][0]))
                        Pini = Pini+1
                        tamList = tamList-1
        else:
            pass
            while True:
                if (DHTLocal[Pini][0] == rtN):
                    if(Pini == 0):
                        print('<--->%d<--->rtN(%d)<--->' % (DHTLocal[tamList][0], DHTLocal[Pini][0]))
                        Pini = Pini+1
                        tamList = tamList-1
                    else:
                        pass
                elif(DHTLocal[tamList][0] == rtN):
                    if(len(DHTLocal) == tamList):
                        print('<--->rtN(%d)<--->%d<--->' % (DHTLocal[tamList][0], DHTLocal[Pini][0]))
                        Pini = Pini+1
                        tamList = tamList-1


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

############################## Gerador de IDs ###############################
def gerarID():
    global usedIDs

    nodeID = random.randint(0, NODE_MAX)
    while (nodeID in usedIDs):
        nodeID = random.randint(0, NODE_MAX)
    usedIDs.append(nodeID)
    return nodeID
########################### CHECAGEM DA POSIÇÃO DE INSERÇÃO DO NOVO NÓ ################
##########################################################################
def chek_positionInList(a, listaIDAddrVar):
    pass
    global rootID, rootAddr, offerIDAddr, seq, lastOp,\
    listaIDAddr, usedIDs, DHTlocal, msg, msgString, msgR, msgStringR,\
    sock, server_addr

    listaIDAddrAux = []
    pos = 0
    b = listaIDAddrVar

    #print('O QUE ESTOU COMPARANDO????')
    #print("a = %d e b = %d" % (a, b[pos][0]))
    #print('LEN(B) = %d', len(b))
    if (a == b[pos][0]):
        print('IDs duplicado.')
        return 0
    elif (len(b) > 1):
        #print('TENTANDO RESOLVER ORDENAMENTO DO CASO TAM = 2')
        if (a > b[pos][0]):
            #print('A > PRIMEIRO ELEMENTO DA LISTA')
            if((len(b) - 1) > 1):
                while ((pos < len(b)-1) and (a > b[pos][0])):
                    #print('Entreando no while.')
                    #pass
                    if(a > b[pos][0]):
                        listaIDAddrAux.append(b[pos])
                        pos = pos + 1
                    else:
                        pass
                if((pos == (len(b)-1)) and (a > b[pos][0])) :
                    #print('CASO POS == LEN(B)-1 E A > B[POS][0]')
                    listaIDAddrAux.append(b[pos])
                    listaIDAddrAux.append(offerIDAddr)
                    listaIDAddrVar = listaIDAddrAux
                    #print ("listaIDAddrAux = %s,, offerIDAddr = %s, listaIDAddrVar: %s\n" % (listaIDAddrAux, offerIDAddr, listaIDAddrVar))
                elif((pos == (len(b)-1)) and (a < b[pos][0])) :
                    #print('CASO POS == LEN(B)-1 E A < B[POS][0]')
                    listaIDAddrAux.append(offerIDAddr)
                    listaIDAddrAux.append(b[pos])
                    listaIDAddrVar = listaIDAddrAux
                    #print ("listaIDAddrAux = %s,, offerIDAddr = %s, listaIDAddrVar: %s\n" % (listaIDAddrAux, offerIDAddr, listaIDAddrVar))
                elif (pos < (len(b)-1) and (a < b[pos][0])):
                    #print('CASO POS < LEN(B) E A < B[POS][0]')
                    listaIDAddrAux.append(offerIDAddr)
                    while pos < len(b)-1:
                        listaIDAddrAux.append(b[pos])
                        pos = pos+1
                    listaIDAddrAux.append(b[pos])
                    listaIDAddrVar = listaIDAddrAux
                    #print ("listaIDAddrAux = %s,, offerIDAddr = %s, listaIDAddrVar: %s\n" % (listaIDAddrAux, offerIDAddr, listaIDAddrVar))
            elif(a > b[pos+1][0]):
                #print('A > POS+1??')
                listaIDAddrVar.append(offerIDAddr)
                #print ("listaIDAddrAux = %s,, offerIDAddr = %s, listaIDAddrVar: %s\n" % (listaIDAddrAux, offerIDAddr, listaIDAddrVar))
                #listaIDAddrVar = listaIDAddrAux
            else:
                #print("O QUE ESTU COMPARANDO AQUI (A >B[POS+1] : %d > %d" % (a, b[pos+1][0]))
                #print('NÃAAOOOOO EHHHHH')
                listaIDAddrAux.append(b[pos])
                listaIDAddrAux.append(offerIDAddr)
                pos = pos+1
                listaIDAddrAux.append(b[pos])
                listaIDAddrVar = listaIDAddrAux
                #print ("listaIDAddrAux = %s,, offerIDAddr = %s, listaIDAddrVar: %s\n" % (listaIDAddrAux, offerIDAddr, listaIDAddrVar))
        else:
            #print('A < PRIMEIRO ELEMENTO DA LISTA')
            #pass
            listaIDAddrAux.append(offerIDAddr)
            while len(b)-1 > pos:
                listaIDAddrAux.append(b[pos])
                pos = pos+1
            listaIDAddrAux.append(b[pos])
            listaIDAddrVar = listaIDAddrAux
            #print ("listaIDAddrAux = %s,, offerIDAddr = %s, listaIDAddrVar: %s\n" % (listaIDAddrAux, offerIDAddr, listaIDAddrVar))
    else:
        #print('CASO LEN(B) == 1')
        if (a < b[pos][0]):
            listaIDAddrAux.append(offerIDAddr)
            listaIDAddrAux.append(b[pos])
            listaIDAddrVar = listaIDAddrAux
            #print ("listaIDAddrAux = %s,, offerIDAddr = %s, listaIDAddrVar: %s\n" % (listaIDAddrAux, offerIDAddr, listaIDAddrVar))
        else:
            listaIDAddrVar.append(offerIDAddr)
            #print ("listaIDAddrAux = %s,, offerIDAddr = %s, listaIDAddrVar: %s\n" % (listaIDAddrAux, offerIDAddr, listaIDAddrVar))
            #listaIDAddrVar = listaIDAddrAux
    return listaIDAddrVar

############################ GERENCIAMENTO DE DHT LOCAL ##########################
##########################################################################
def DHTmanagement():
    pass
    DHTlocalAux = []

############################ Ordenamento ##############################
def def_dist(a ,b):
    if (a == b):
        return 0
    elif (a < b):
        return b - a
    else:
        return 256 + b - a
###################################################################
def newNode_newNodeAns(addr):
    global rootID, rootAddr, rootPort, offerIDAddr, seq, lastOp,\
    nodeIDAddr, usedIDs, DHTlocal, msg, msgString, msgR, msgStringR,\
    sock, server_addr

    msg = Mensagem()
    msg.op = 2
    msg.nodeID = gerarID()
    if rootID == -1:
        msg.flagRoot = 1
        #offerIDAddr = (msg.nodeID, addr)
        #print ("nó <===== op = 2 (newNodeAns) =====")
       #sendNWait(addr)
    else:
        msg.flagRoot = 0
        msg.rootID = rootID
        msg.rootAddr = rootAddr
        #offerIDAddr = (msg.nodeID, addr)
        #print ("nó <===== op = 2 (newNodeAns) =====")
        #sendNWait(addr)
    offerIDAddr = (msg.nodeID, addr)
    print ("nó <===== op = 2 (newNodeAns) =====")
    sendNWait(addr)
##################################################################
def isNext_isNextAns():
    global rootID, rootAddr, rootPort, offerIDAddr, seq, lastOp,\
    nodeIDAddr, usedIDs, DHTlocal, msg, msgString, msgR, msgStringR,\
    sock, server_addr

    # Se nodeID do nó anterior for maior que o root

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

############ VERIFICAÇÃO DA REQUISIÇÃO DE CONEXÃO ###################
        elif msgR.op == 1:
            newNode_newNodeAns(addr)

        elif msgR.op == 3:
            isNext_isNextAns()

############## VERIFICAÇÃO DO Ack = 0 RECEBIDO DO NÓ #################
        elif msgR.op == 0 and lastOp == 2 and rootID == -1:
            rootID = offerIDAddr[0]
            rootAddr = offerIDAddr[1]
            listaIDAddr.append(offerIDAddr)
            DHTlocal = listaIDAddr
            #showTpoligi(DHTlocal)
        elif msgR.op == 0 and lastOp == 2 and rootID != -1:
            listaIDAddr = chek_positionInList(offerIDAddr[0], listaIDAddr)
            #DHTlocal = listaIDAddr
            #showTpoligi(DHTlocal)

if __name__ == "__main__":
    main()