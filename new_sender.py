# Written by S. Mevawala, modified by D. Gitzel

import logging
from pickle import TRUE
import socket
import hashlib
#from xml.etree.ElementInclude import DEFAULT_MAX_INCLUSION_DEPTH
import channelsimulator
import utils
import sys
import struct
import threading

class Sender(object):

    def __init__(self, inbound_port=50006, outbound_port=50005, timeout=10, debug_level=logging.INFO):
        self.logger = utils.Logger(self.__class__.__name__, debug_level)

        self.inbound_port = inbound_port
        self.outbound_port = outbound_port
        self.simulator = channelsimulator.ChannelSimulator(inbound_port=inbound_port, outbound_port=outbound_port,
                                                           debug_level=debug_level)
        self.simulator.sndr_setup(timeout)
        self.simulator.rcvr_setup(timeout)

    def send(self, data):
        raise NotImplementedError("The base API class has no implementation. Please override and add your own.")

class packets: 
    number = None
    data = None
    hash = None
    sendMe = None
    recieved = False
    isCorrect = False
    numPad = None
    
    def __init__(self, *args):
        
        if(len(args) == 2):
            
            self.number = args[0]
            self.data = args[1]
            l = []
            l.extend(bytearray(self.data))
            q = len(l)
            l.extend([0]*(1000-len(l)))
            l.extend(struct.pack("=I",(q)))
            l.extend((struct.pack("=I",self.number)))
            self.hash = hashlib.md5(bytearray(l)).digest()
            #print(len(l))
            l.extend(bytearray(self.hash))
            #print(len(l))
            self.sendMe = bytearray(l)
            
        
        elif(len(args) == 1):
            packetIn = args[0]
            self.hash = hashlib.md5(bytes(bytearray(packetIn[0:1008]))).digest() 
            self.numPad = struct.unpack('=I', packetIn[1000:1004])[0]
            self.data = bytearray(packetIn[0:self.numPad]) 
            self.number = struct.unpack('=I', packetIn[1004:1008])[0] 
            #Check to see if the hash is correct
            if bytearray(self.hash) == packetIn[1008:1024]: 
                self.isCorrect = True 
            
            #if this failes then you have a problem with the code above.
            #test_packet = packets(self.number, self.data)
            #if(test_packet.mail() != packetIn):
            #    print("Error: Packet not read correctly, or corrupted packet")
        
    def isCorr(self):
        return self.isCorrect
             
    def mail(self):
        return self.sendMe
        
    def markRecieved(self):
        self.recieved = True
        return self.recieved
    
    def beenRecieved(self):
        return self.recieved
    
    def __str__(self):
        return "Hello! I'm Packet #{} and I have data ' {} ' and hash '{}' ".format(self.number, self.data, self.hash)
    def __repr__(self):
        return "Hello! I'm Packet #{} and I have data {} and hash {} \n I have been received? {}".format(self.number, self.data, self.hash, self.recieved)
    
    def dataOut(self):
        return self.data
        
class Jacob_Sender(Sender):

    # implement selective repeat
    ackNumbers = [[]]
    dataFrame = []
    acksLeft = 0
    chunks = []

    def chunk(self, data,size=1000):
        for i in range(0, len(data), size):
            yield data[i:i + size]
    
    def send(self, data):
        self.logger.info("Sending on port: {} and waiting for ACK on port: {}".format(self.outbound_port, self.inbound_port))
        self.chunks = self.chunk(data)
        
        for(i, chunk) in enumerate(self.chunks):
            pack = packets(i, chunk)
            self.dataFrame.append(pack)
        
        self.acksLeft = len(self.dataFrame)
         
        _send = threading.Thread(target=self._send)
        _send.daemon = True
        _send.start()
        
        recieve(self)
        
    def _send(self):
        while TRUE:
            for frame in self.dataFrame:
                if(not frame.beenRecieved()):
                    try: 
                        self.simulator.u_send(frame.mail())
                    except socket.timeout:
                        pass
    
def recieve(self):
    while True:
        ## ACK RECEIVER 
        #print("waiting for an acknowledgement")
        ack = self.simulator.u_receive()  # receive ACK
        #print("I got an ack!")
        ack_pack = packets(ack)
        if(ack_pack.isCorr()):
            #print("ACK NUM: %d", ack_pack.number)
            self.acksLeft = self.acksLeft - 1
            print(self.acksLeft)
            if self.acksLeft == 0:
                sys.exit(0)
            ack_num = ack_pack.number
            self.dataFrame[ack_num].markRecieved()
            self.logger.info("ACK received for packet {}".format(ack_num))
        
    

if __name__ == "__main__":
    # test out BogoSender
    DATA = bytearray(sys.stdin.read())    
    sndr = Jacob_Sender()
    sndr.send(DATA)
