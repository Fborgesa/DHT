# -*- coding: utf-8 -*-

import socket
import pickle
import hashlib
import copy
from Mensagem import Mensagem

def testCom(sock, server_address):
    msg = Mensagem()
    msgString = pickle.dumps(msg)
    sock.sendto(msgString, server_address)

def newNode(sock, server_address):
    msg = Mensagem()
    msg.op = 1
    sock.bind(('localhost', 0))
    msgString = pickle.dumps(msg)
    sock.sendto(msgString, server_address)

def main():
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
    listaKeyValue = -1

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