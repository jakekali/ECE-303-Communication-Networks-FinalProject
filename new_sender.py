# Written by S. Mevawala, modified by D. Gitzel

import logging
import socket
import hashlib
from xml.etree.ElementInclude import DEFAULT_MAX_INCLUSION_DEPTH
import channelsimulator
import utils
import sys
import struct

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
    ackAt = 0
    sendAt = 0
    chunks = []
    

    def chunk(data,size=1000):
        for i in range(0, len(data), size):
            yield data[i:i + size]
    
    def send(self, data):
        self.logger.info("Sending on port: {} and waiting for ACK on port: {}".format(self.outbound_port, self.inbound_port))
        
        self.chunks = self.chunk(data)
        self.dataFrame = [0,"fffffffffffffffffffffffffffffffffff"] * len(self.chunks)
        
        for(i, chunk) in enumerate(self.chunks):
            l = []
            l.extend(chunk)
            l.extend(struct.pack("I",i))
            self.dataFrame[i] = [2, hashlib.md5(l).digest()]
            
        
        while True:
            try:
                ## ACK RECEIVER
                ack = self.simulator.u_receive()  # receive ACK
                self.logger.info("Got ACK from socket: {}".format(
                    ack.decode('ascii')))  # note that ASCII will only decode bytes in the range 0-127
                #get the first 5 characters of the ACK
                ack_data = ack.splitlines()
                ack_num = ack_data[0]
                ack_has = ack_data[1]
                if(not self.ackNumbers[ack_num][0] and self.ackNumbers[ack_num][1] == ack_has):
                    self.ackNumbers[ack_num][0] = 1
                    self.logger.info("ACK received for packet {}".format(ack_num))
                    if(ack_num == self.ackAt):
                        while(self.ackNumbers[self.ackAt][0]):
                            self.ackAt += 1
                for i in range(self.ackAt,self.sendAt):
                    if self.ackNumbers[i][0] == 0:      
                        self.simulator.u_send(data)  # send data
                break
            except socket.timeout:
                self.logger.info("Timeout occurred. Resending data")
                pass
            
def _send(self):
    done = False
    while not done:
        for(i, chunk) in enumerate(self.chunks):
            if(self.dataFrame[i] != 1):
                l = []
                l.extend(chunk)
                l.extend(struct.pack("I",i))
                self.simulator.u_send(bytearray(chunk))
                self.dataFrame[i] = 0
            
            
        try: 
            if 
    

if __name__ == "__main__":
    # test out BogoSender
    DATA = bytearray(sys.stdin.read())
    sndr = BogoSender()
    sndr.send(DATA)
