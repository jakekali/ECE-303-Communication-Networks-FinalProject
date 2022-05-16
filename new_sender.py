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


class Jacob_Sender(Sender):

    # implement selective repeat
    ackNumbers = [[]]
    dataFrame = [0,"fffffffffffffffffffffffffffffffffff"]
    acksLeft = 0
    chunks = []
    

    def chunk(data,size=1000):
        for i in range(0, len(data), size):
            yield data[i:i + size]
    
    def send(self, data):
        self.logger.info("Sending on port: {} and waiting for ACK on port: {}".format(self.outbound_port, self.inbound_port))
        
        self.chunks = self.chunk(data)
        self.dataFrame = [0,"fffffffffffffffffffffffffffffffffff"] * len(self.chunks)
        self.acksLeft = self.chunks.size()
        
        for(i, chunk) in enumerate(self.chunks):
            l = []
            l.extend(chunk)
            l.extend(struct.pack("I",i))
            self.dataFrame[i] = [2, hashlib.md5(l).digest()]
            
        _send = threading.Thread(target=self._send)
        _send.daemon = True
        _send.start()
        
        self.recieve()
        
        
        
        
            
                
            
    def _send(self):
        while TRUE:
            for(i, chunk) in enumerate(self.chunks):
                if(self.dataFrame[i] != 1):
                    l = []
                    l.extend(chunk)
                    l.extend(struct.pack("I",i))
                    l.extend(self.dataFrame[i][1])
                    try: 
                        self.simulator.u_send(bytearray(chunk))
                        self.dataFrame[i] = 0
                    except socket.timeout:
                        pass
    
def recieve(self):
    
    while True:
        ## ACK RECEIVER 
        ack = self.simulator.u_receive()  # receive ACK
        
        self.logger.info("Got ACK from socket: {}".format(
            ack.decode('ascii')))  # note that ASCII will only decode bytes in the range 0-127
        #get the ack number
        ack_num_1 = struct.unpack('I',ack[0:4])
        ack_num_2 = struct.unpack('I',ack[4:8])
        ack_num_3 = struct.unpack('I',ack[8:12])
        if(ack_num_1 == ack_num_2 and ack_num_3 == ack_num_2):
            acksLeft = acksLeft - 1
            if acksLeft == 0:
                sys.exit(0)
            ack_num = ack_num_1 
            self.ackNumbers[ack_num][0] = 1
            self.logger.info("ACK received for packet {}".format(ack_num))
        
    

if __name__ == "__main__":
    # test out BogoSender
    DATA = bytearray(sys.stdin.read())
    sndr = Jacob_Sender()
    sndr.send(DATA)
