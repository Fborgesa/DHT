# -*- coding: utf-8 -*-

import socket
import pickle
import time
from Mensagem import Mensagem

# Função utilizada para enviar mensagens de modo confiável.
# Retorna: msg, seq
def rdt_send(msg, seq, sock, addr):
    """
    @type msg: Mensagem
    @param msg: Mensagem a ser enviada.
    @sock: Socket a ser usado para o envio.
    @seq: Número de sequência a ser utilizado para o envio.
    @addr: (IP, port) de destino.
    """
    # Estado 0: recebeu chamada de cima.
    time.sleep(1)
    sock.settimeout(2)
    msgString = pickle.dumps(msg)
    sock.sendto(msgString, addr)

    # Estado 1: esperar ack(n+1).
    timeOuts = 0
    seqNum = 0
    while True:
        try:
            msgString, addr = sock.recvfrom(1024)
            msg = pickle.loads(msgString)
            time.sleep(1)
            print("op = %d. Recebida." % msg.op)
#            print ("msg.ack = %d. seq = %d." % (msg.ack, seq))
            if msg.ack != seq:
                if seqNum == 2:
                    print("Número de sequência dessincronizado.")
                    return -1, (seq - 1 if seq == 1 else seq + 1)
                sock.sendto(msgString, addr)
                seqNum = seqNum + 1
            else:
                sock.settimeout(None)
                return msg, (seq - 1 if seq == 1 else seq + 1)
        except socket.timeout:
            if timeOuts == 2:
                print ("Destino não responde.")
                return -1, (seq - 1 if seq == 1 else seq + 1)
            else:
                timeOuts = timeOuts + 1
                print ("Tentativa %d" % timeOuts)
                sock.sendto(msgString, addr)

# # Função utilizada pelo receptor RDT
# # Retorna: msg, seq
# def rdt_rcv(self, seq, sock):
#     msgString, addr = sock.recvfrom(1024)
#     msg = pickle.loads(msgString)
#     if msg.seq == 0:
#         oncethru = 1




