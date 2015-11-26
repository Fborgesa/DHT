
class Mensagem:
    def __init__(self):
        self.op = -1
        self.seq = -1
        self.ack = -1
        self.flagRoot = -1
        self.flagIsNext = -1
        self.nodeID = -1
        self.rootID = -1
        self.rootAddr = []
        self.listaIDAddr = []
        self.listaKeyValue = []
