# -*- coding: utf-8 -*-

import socket
import pickle
import hashlib
from Mensagem import Mensagem
from MsgCheckSum import MsgCheckSum

def main():
    rootID = -1
    rootIP = -1
    rootPort = -1
    DHTlocal = -1

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = ('localhost', 30000)
    sock.bind(server_address)

    while True:
        msgCheckSumStringN, addr = sock.recvfrom(1024)
        msgCheckSumN = pickle.loads(msgCheckSumStringN)
        assert isinstance(msgCheckSumN, MsgCheckSum)
        msgStringS = pickle.dumps(msgCheckSumN.msg )
        msgCheckSumS = hashlib.md5()

        assert isinstance(msg, Mensagem)
        if msg.op == -1:
            print('op  = %d' % msg.op)

if __name__ == "__main__":
    main()