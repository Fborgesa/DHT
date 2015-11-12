# -*- coding: utf-8 -*-

import socket
import pickle
import hashlib
import copy
from Mensagem import Mensagem
from MsgCheckSum import MsgCheckSum

def testCom(sock, server_address):
    msg = Mensagem()
    msgString = pickle.dumps(msg)
    sock.sendto(msgString, server_address)

def newNode(sock, server_address):
    msg = Mensagem()
    msg.op = 1
    sock.bind('localhost', 0)
    msgString = pickle.dumps(msg)
    msgCheckSum = MsgCheckSum()
    msgCheckSum.msg = msg
    msgCheckSum.checkSum = hashlib.md5(msgString)
    msgCheckSumString = pickle.dumps(msgCheckSum)
    sock.sendto(msgCheckSumString, server_address)

def main():
    nodeID = -1
    root = -1
    rootID = -1
    rootIP = -1
    prevID = -1
    prevIP = -1
    prevID2 = -1
    prevIP2 = -1
    nextID = -1
    nextIP = -1
    nextID2 = -1
    nextIP2 = -1
    listaKeyValue = -1

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = ('localhost', 30000)

    op = input("\
    Escolha uma opção:\n\
    0 - Testar comunicação.\n\
    1 - Entrar na DHT.")

    if op == '0':
        testCom(sock, server_address)

    elif op == '1':
        newNode(sock, server_address)

if __name__ == "__main__":
    main()