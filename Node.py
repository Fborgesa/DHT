# -*- coding: utf-8 -*-

import socket
import pickle
import hashlib
import copy
import time
import _thread
import RDT
from Mensagem import Mensagem

############################### Estado do Node ###############################
nodeID = -1
root = -1
rootID = -1
rootAddr = -1
prevID = -1
prevIDUpdt = -1
prevAddr = -1
prevAddrUpdt = -1
prevID2 = -1
prevAddr2 = -1
nextID = -1
nextIDUpdt = -1
nextAddr = -1
nextAddrUpdt = 1
nextID2 = -1
nextAddr2 = -1
seq = 0
lastOP = 0
listaKeyValue = []
listaKeyValueUpdt = []
# Todos os nós conhecidos, incluindo os sucessores, antecessores e o próprio nó.
listaIDAddr = []
msg = Mensagem()
msgString = -1
msgR = Mensagem()
msgStringR = -1

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_addr = ('localhost', 30000)
addrLastSent = server_addr
addrR = server_addr

############################### Thread Listen ###############################
# Thread que escuta e responde a chamadas. Nela estão os tratamentos das mensagens
# que não necessitam de nenhuma interação do usuário.
def threadListen():
    global nodeID, root, rootID, rootAddr, prevID, prevAddr,\
    prevID2, prevAddr2, nextID, nextAddr, nextID2, nextAddr2,\
    seq, lastOP, listaKeyValue, msg, msgString, msgR, msgStringR,\
    sock, server_addr, addrR

    # Variáveis que definem quantos timeouts ocorreram e quantos números de sequência
    # chegaram dessincronizados.
    timeOuts = 0
    seqNum = 0

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

        ### Tratamento de cada caso
        if msgR.op == 'ack':
            AckUpdt()

        if msgR.op == 'newNodeAns':
            if msgR.flagRoot == 1:
                newNodeAns_Ack()
            elif msgR.flagRoot == 0:
                newNodeAns_isCloser()

        if msgR.op == 'isCloser':
            isCloser_isCloserAns()

        if msgR.op == 'isCloserAns':
            if msgR.flagIsCloser == 1:
                isCloser_joinAsPrev()
            elif msgR.flagIsCloser == 0:
                isCloserAns_isCloser()

        if msgR.op == 'joinAsPrev':
            joinAsPrev_joinAsPrevAns()

        if msgR.op == 'joinAsPrevAns':
            joinAsPrevAns_joinAsNext()

        if msgR.op == 'joinAsNext':
            joinAsNext_joinAsNextAns()

        if msgR.op == 'joinAsNextAns':
            joinAsNextAns_Ack()

############################### Thread Start Communication ###############################
# Thread que exibe o menu e interage com o usuário. Nela estão os tratamentos das
# mensagens que começam a comunicação.
def threadStartCommu():
    global nodeID, root, rootID, rootAddr, prevID, prevAddr,\
    prevID2, prevAddr2, nextID, nextAddr, nextID2, nextAddr2,\
    seq, lastOP, listaKeyValue, msg, msgString, msgR, msgStringR,\
    sock, server_addr, addr, listaIDAddr

    while True:
        op = input("\
        Escolha uma opção:\n\
        0 - Testar comunicação.\n\
        1 - Imprimir estado.\n\
        2 - Imprimir nós conhecidos.\n\
        3 - Imprimir entradas da DHT.\n\
        4 - Entrar na DHT.\n\
        5 - Sair da DHT\n")

        if op == '0':
            testCom()

        elif op == '1':
            print ("\tnodeID = %d, root = %d, rootID = %d, rootAddr = %s\n\
            prevID = %d, prevAddr = %s, prevID2 = %d, prevAddr2 = %s\n\
            nextID = %d, nextAddr = %s, nextID2 = %d, nextAddr2 = %s\n"
            % (nodeID, root, rootID, rootAddr, prevID, prevAddr, prevID2, prevAddr2,
            nextID, nextAddr, nextID2, nextAddr2)
            )

        elif op == '2':
            print ("%s" % listaIDAddr)

        elif op == '3':
            pass

        elif op == '4':
            newNode()

        elif op == '5':
            pass

############################### Definições das funções   ###############################
############################### que tratam cada mensagem ###############################
def sendNWait(addr):
    global nodeID, root, rootID, rootAddr, prevID, prevAddr,\
    prevID2, prevAddr2, nextID, nextAddr, nextID2, nextAddr2,\
    seq, lastOP, listaKeyValue, msg, msgString, msgR, msgStringR,\
    sock, server_addr, addrLastSent

    msg.ack = msgR.seq
    msg.seq = seq
    lastOP = msg.op
    if msg.op != 'ack':
        sock.settimeout(2)
    msgString = pickle.dumps(msg)
    addrLastSent = addr
    print("%s Enviada ===== op = %s =====> %s" % (sock.getsockname(), msg.op, addr))
    sock.sendto(msgString, addr)
    time.sleep(0.1)

def dist(a,b):
    if (a == b):
        return 0
    elif (a < b):
        return b-a
    else:
        return 256 + b - a

def closerKnown():
    global nodeID, root, rootID, rootAddr, prevID, prevAddr,\
    prevID2, prevAddr2, nextID, nextAddr, nextID2, nextAddr2,\
    seq, lastOP, listaKeyValue, listaIDAddr, msg, msgString, msgR, msgStringR,\
    sock, server_addr, addr

    closer = (nodeID, sock.getsockname())
    closerDist = dist(msgR.nodeID, nodeID)
    for node in listaIDAddr:
        print(node)
        lastDist = dist(msgR.nodeID, node[0])
        if lastDist < closerDist:
            closer = node
            closerDist = lastDist

    return closer

def keyValueToUpdate():
    global listaKeyValue

    keys = []
    for entry in listaKeyValue:
        if msgR.nodeID >= entry[0]:
            keys.append(entry)

    return keys

def addToList(list, itemToAdd):
    if itemToAdd not in list:
        list.append(itemToAdd)

def testCom():
    global nodeID, root, rootID, rootAddr, prevID, prevAddr,\
    prevID2, prevAddr2, nextID, nextAddr, nextID2, nextAddr2,\
    seq, lastOP, listaKeyValue, msg, msgString, msgR, msgStringR,\
    sock, server_addr

    msg = Mensagem()
    msgString = pickle.dumps(msg)
    sock.sendto(msgString, server_addr)

def AckUpdt():
    global prevID, prevIDUpdt, prevAddr, prevAddrUpdt, msgR,\
    nextIDUpdt, nextAddrUpdt, nextID, nextAddr, listaKeyValue,\
    listaKeyValueUpdt, nextID2, nextAddr2, prevID2, prevAddr2

    if lastOP == 'joinAsPrevAns':
        # Somente para o segundo nó entrante.
        if nodeID == nextID2 and nodeID != nextID:
            prevID2 = nextID
            prevAddr2 = nextAddr
            nextID2 = prevIDUpdt
            nextAddr2 = prevAddrUpdt

        prevID = prevIDUpdt
        prevAddr = prevAddrUpdt

        # Deletando as entradas que foram repassadas.
        for entry in listaKeyValueUpdt:
            listaKeyValue.remove(entry)

    if lastOP == 'joinAsNextAns':
        # Somente para o segundo nó entrante.
        if nodeID == prevID2 and nodeID != nextID:
            nextID2 = prevID
            nextAddr2 = prevAddr
            prevID2 = nextIDUpdt
            prevAddr2 = nextAddrUpdt

        nextID = nextIDUpdt
        nextAddr = nextAddrUpdt

def newNode():
    global nodeID, root, rootID, rootAddr, prevID, prevAddr,\
    prevID2, prevAddr2, nextID, nextAddr, nextID2, nextAddr2,\
    seq, lastOP, listaKeyValue, msg, msgString, msgR, msgStringR,\
    sock, server_addr

    msg = Mensagem()
    msg.op = 'newNode'
    sendNWait(server_addr)

# Utilizada caso o nó seja o root.
def newNodeAns_Ack():
    global nodeID, root, rootID, rootAddr, prevID, prevAddr,\
    prevID2, prevAddr2, nextID, nextAddr, nextID2, nextAddr2,\
    seq, lastOP, listaKeyValue, listaIDAddr, msg, msgString, msgR, msgStringR,\
    sock, server_addr, addrR

    # Atualizando estado
    nodeID = msgR.nodeID
    root = 1
    rootID = nodeID
    rootAddr = sock.getsockname()
    prevID = rootID
    prevAddr = rootAddr
    prevID2 = rootID
    prevAddr2 = rootAddr
    nextID = rootID
    nextAddr = rootAddr
    nextID2 = rootID
    nextAddr2 = rootAddr
    addToList(listaIDAddr, (nodeID, rootAddr))
    # Confirmando o recebimento da mensagem op = 2 (newNodeAns)
    # com um ack.
    msg = Mensagem()
    msg.op = 'ack'
    sendNWait(addrR)

# Utilizada caso o nó não seja o root.
def newNodeAns_isCloser():
    global nodeID, root, rootID, rootAddr, prevID, prevAddr,\
    prevID2, prevAddr2, nextID, nextAddr, nextID2, nextAddr2,\
    seq, lastOP, listaKeyValue, listaIDAddr, msg, msgString, msgR, msgStringR,\
    sock, server_addr, addr

    # Atualizando estado
    nodeID = msgR.nodeID
    root = 0
    rootID = msgR.listaIDAddr[0][0]
    rootAddr = msgR.listaIDAddr[0][1]
    prevID = nodeID
    prevAddr = sock.getsockname()
    prevID2 = nodeID
    prevAddr2 = sock.getsockname()
    nextID = nodeID
    nextAddr = sock.getsockname()
    nextID2 = nodeID
    nextAddr2 = sock.getsockname()
    addToList( listaIDAddr, ( nodeID, sock.getsockname() ) )
    addToList( listaIDAddr, msgR.listaIDAddr[0] )
    # Confirmando o recebimento da mensagem op = 2 (newNodeAns)
    # com um ack.
    msg = Mensagem()
    msg.op = 'ack'
    sendNWait(server_addr)
    # Encontrar seu sucessor
    msg = Mensagem()
    msg.op = 'isCloser'
    msg.nodeID = nodeID
    sendNWait(rootAddr)

def isCloser_isCloserAns():
    global nodeID, root, rootID, rootAddr, prevID, prevAddr,\
    prevID2, prevAddr2, nextID, nextAddr, nextID2, nextAddr2,\
    seq, lastOP, listaKeyValue, listaIDAddr, msg, msgString, msgR, msgStringR,\
    sock, server_addr, addrR

    closer = closerKnown()
    msg = Mensagem()
    msg.op = 'isCloserAns'
    msg.listaIDAddr.append(closer)
    if closer[0] == nodeID:
        msg.flagIsCloser = 1
    else:
        msg.flagIsCloser = 0
    sendNWait(addrR)

def isCloserAns_isCloser():
    global nodeID, root, rootID, rootAddr, prevID, prevAddr,\
    prevID2, prevAddr2, nextID, nextAddr, nextID2, nextAddr2,\
    seq, lastOP, listaKeyValue, listaIDAddr, msg, msgString, msgR, msgStringR,\
    sock, server_addr, addrR

    # Confirmando o recebimento da mensagem op = 3 (isCloser)
    # com um ack.
    msg = Mensagem()
    msg.op = 'ack'
    sendNWait(addrR)
    # Encontrar seu sucessor
    msg = Mensagem()
    msg.op = 'isCloser'
    msg.nodeID = nodeID
    sendNWait(msgR.listaIDAddr[0][1])

# Utilizada após o nó descobrir seu par mais próximo.
# Comunica a entrada na DHT.
def isCloser_joinAsPrev():
    global nodeID, msg, msgR, addrR

    # Confirmando o recebimento da mensagem op = 3 (isCloser)
    # com um ack.
    msg = Mensagem()
    msg.op = 'ack'
    sendNWait(addrR)

    # Avisar para o par mais próximo que nó quer entrar na DHTl.
    msg = Mensagem()
    msg.op = 'joinAsPrev'
    msg.nodeID = nodeID
    sendNWait(msgR.listaIDAddr[0][1])

def joinAsPrev_joinAsPrevAns():
    global nodeID, prevID, prevAddr, nextID, nextAddr, listaIDAddr, msg,\
        listaKeyValueUpdt, prevIDUpdt, prevAddrUpdt, addrR, sock, nextID2,\
        msgR

    # ## Atualizando estado.
    # # O next deve ser atualizado em um caso específico. Caso o par entrate venha a ser o
    # # anterior e o próximo do nó. Isso só ocorre para o segundo nó entrante.
    # if nodeID == prevID:
    #     nextID = msgR.nodeID
    #     nextAddr = addrR


    msg = Mensagem()
    msg.op = 'joinAsPrevAns'
    ## O next do novo nó.
    msg.listaIDAddr.append((nodeID, sock.getsockname()))
    ## O next2 do novo nó.
    if nodeID == nextID2:
        msg.listaIDAddr.append((msgR.nodeID, addrR))
    else:
        msg.listaIDAddr.append((nextID, nextAddr))
    ## O prev, a ser contatado para finalização da entrada na DHT.
    msg.listaIDAddr.append((prevID, prevAddr))
    prevIDUpdt = msgR.nodeID
    prevAddrUpdt = addrR
    addToList( listaIDAddr, (msgR.nodeID, addrR) )
    listaKeyValueUpdt = keyValueToUpdate()
    msg.listaKeyValue = listaKeyValueUpdt
    sendNWait(addrR)

def joinAsPrevAns_joinAsNext():
    global msg, nextID, nextAddr, nextID2, nextAddr2, listaIDAddr,\
           prevID, prevAddr

    nextID = msgR.listaIDAddr[0][0]
    nextAddr = msgR.listaIDAddr[0][1]
    nextID2 = msgR.listaIDAddr[1][0]
    nextAddr = msgR.listaIDAddr[1][1]
    prevID = msgR.listaIDAddr[2][0]
    prevAddr = msgR.listaIDAddr[2][1]
    # next
    addToList(listaIDAddr, msgR.listaIDAddr[0])
    # next2
    addToList(listaIDAddr, msgR.listaIDAddr[1])
    # prev
    addToList(listaIDAddr, msgR.listaIDAddr[2])

    ## Confirmando o recebimento da mensagem op = 6 (joinAsPrevAns)
    ## com um ack.
    msg = Mensagem()
    msg.op = 'ack'
    sendNWait(addrR)

    ## joinAsNext
    msg = Mensagem()
    # msg.op = 7 (joinAsNext)
    msg.op = 'joinAsNext'
    msg.nodeID =  nodeID
    sendNWait(msgR.listaIDAddr[2][1])

def joinAsNext_joinAsNextAns():
    global msg, nodeID, prevID, prevAddr, listaIDAddr, nextIDUpdt,\
           nextAddrUpdt, listaIDAddr, addrR

    ## Atualizando estado.
    # Salvando ID e Addr do next para atualizar no Ack.
    nextIDUpdt = msgR.nodeID
    nextAddrUpdt = addrR
    addToList( listaIDAddr, (msgR.nodeID, addrR) )

    ## Confirmando o recebimento da mensagem op = 7 (joinAsNext)
    ## com um ack.
    msg = Mensagem()
    msg.op = 'ack'
    sendNWait(addrR)

    ## joinAsNextAns
    msg = Mensagem()
    msg.op = 'joinAsNextAns'
    # O prev do novo nó.
    msg.listaIDAddr.append((nodeID, sock.getsockname()))
    # O prev2 do novo nó.
    msg.listaIDAddr.append((prevID, prevAddr))
    sendNWait(addrR)

def joinAsNextAns_Ack():
    global msg, msgR, addrR, prevID2, prevAddr2, listaIDAddr

    ## Atualizando estado
    prevID2 = msgR.listaIDAddr[1][0]
    prevAddr2 = msgR.listaIDAddr[1][1]

    ## Confirmando o recebimento da mensagem op = 8 (joinAsNextAns)
    ## com um ack.
    msg = Mensagem()
    msg.op = 'ack'
    sendNWait(addrR)

############################### Main ###############################
def main():
    global nodeID, root, rootID, rootAddr, prevID, prevAddr,\
    prevID2, prevAddr2, nextID, nextAddr, nextID2, nextAddr2,\
    seq, lastOP, listaKeyValue, msg, msgString, msgR, msgStringR,\
    sock, server_addr

    sock.bind(('localhost', 0))

    try:
        t = _thread.start_new_thread(threadStartCommu, ())
        t2 = _thread.start_new_thread(threadListen, ())
    except:
        print("Falha ao inicializar as threads.")

    while True:
        pass

if __name__ == "__main__":
    main()