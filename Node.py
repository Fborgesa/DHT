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
prevAddr = -1
prevID2 = -1
prevAddr2 = -1
nextID = -1
nextAddr = -1
nextID2 = -1
nextAddr2 = -1
seq = 0
lastOP = 0
listaKeyValue = []
msg = Mensagem()
msgString = -1
msgR = Mensagem()
msgStringR = -1

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_addr = ('localhost', 30000)

############################### Thread Listen ###############################
# Thread que escuta e responde a chamadas. Nela estão os tratamentos das mensagens
# que não necessitam de nenhuma interação do usuário.
def threadListen():
    global nodeID, root, rootID, rootAddr, prevID, prevAddr,\
    prevID2, prevAddr2, nextID, nextAddr, nextID2, nextAddr2,\
    seq, lastOP, listaKeyValue, msg, msgString, msgR, msgStringR,\
    sock, server_addr

    # Variáveis que definem quantos timeouts ocorreram e quantos números de sequência
    # chegaram dessincronizados.
    timeOuts = 0
    seqNum = 0

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

        ### Tratamento de cada caso
        if msgR.op == 2:
            if msgR.flagRoot == 1:
                newNodeAns_Ack(addr)
            if msgR.flagRoot == 0:
                newNodeAns_isNext(addr)


############################### Thread Start Communication ###############################
# Thread que exibe o menu e interage com o usuário. Nela estão os tratamentos das
# mensagens que começam a comunicação.
def threadStartCommu():
    global nodeID, root, rootID, rootAddr, prevID, prevAddr,\
    prevID2, prevAddr2, nextID, nextAddr, nextID2, nextAddr2,\
    seq, lastOP, listaKeyValue, msg, msgString, msgR, msgStringR,\
    sock, server_addr

    while True:
        op = input("\
        Escolha uma opção:\n\
        0 - Testar comunicação.\n\
        1 - Imprimir estado.\n\
        2 - Imprimir entradas da DHT.\n\
        3 - Entrar na DHT.\n\
        4 - Sair da DHT\n")

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
            pass

        elif op == '3':
            newNode()

        elif op == '4':
            pass

############################### Definições das funções   ###############################
############################### que tratam cada mensagem ###############################
def sendNWait(addr):
    global nodeID, root, rootID, rootAddr, prevID, prevAddr,\
    prevID2, prevAddr2, nextID, nextAddr, nextID2, nextAddr2,\
    seq, lastOP, listaKeyValue, msg, msgString, msgR, msgStringR,\
    sock, server_addr

    msg.ack = msgR.seq
    msg.seq = seq
    lastOP = msg.op
    if msg.op != 0 and not 3:
        sock.settimeout(2)
    msgString = pickle.dumps(msg)
    sock.sendto(msgString, addr)
    time.sleep(3)

def testCom():
    global nodeID, root, rootID, rootAddr, prevID, prevAddr,\
    prevID2, prevAddr2, nextID, nextAddr, nextID2, nextAddr2,\
    seq, lastOP, listaKeyValue, msg, msgString, msgR, msgStringR,\
    sock, server_addr

    msg = Mensagem()
    msgString = pickle.dumps(msg)
    sock.sendto(msgString, server_addr)

def newNode():
    global nodeID, root, rootID, rootAddr, prevID, prevAddr,\
    prevID2, prevAddr2, nextID, nextAddr, nextID2, nextAddr2,\
    seq, lastOP, listaKeyValue, msg, msgString, msgR, msgStringR,\
    sock, server_addr

    msg = Mensagem()
    msg.op = 1
    print("===== op = 1 (newNode) =====> rendezvous")
    sendNWait(server_addr)

# Utilizada caso o nó seja o root.
def newNodeAns_Ack(addr):
    global nodeID, root, rootID, rootAddr, prevID, prevAddr,\
    prevID2, prevAddr2, nextID, nextAddr, nextID2, nextAddr2,\
    seq, lastOP, listaKeyValue, msg, msgString, msgR, msgStringR,\
    sock, server_addr

    # Atualizando estado
    nodeID = msgR.nodeID
    root = 1
    rootID = nodeID
    rootAddr = sock.getsockname()
    prevID = rootID
    prevAddr = rootAddr
    nextID = rootID
    nextAddr = rootAddr
    # Confirmando o recebimento da mensagem op = 2 (newNodeAns)
    # com um ack.
    msg = Mensagem()
    msg.op = 0
    print("===== op = 0 (Ack) =====> rendezvous")
    sendNWait(addr)

# Utilizada caso o nó não seja o root.
def newNodeAns_isNext(addr):
    global nodeID, root, rootID, rootAddr, prevID, prevAddr,\
    prevID2, prevAddr2, nextID, nextAddr, nextID2, nextAddr2,\
    seq, lastOP, listaKeyValue, msg, msgString, msgR, msgStringR,\
    sock, server_addr

    # Atualizando estado
    nodeID = msgR.nodeID
    root = 0
    rootID = msgR.rootID
    rootAddr = msgR.rootAddr
    # Criando mensagem
    msg = Mensagem()
    ###################
    msg.op = 0
    print("===== op = 0 (Ack) =====> rendezvous")
    sendNWait(addr)
    ###################
    msg.op = 3
    msg.nodeID = nodeID

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