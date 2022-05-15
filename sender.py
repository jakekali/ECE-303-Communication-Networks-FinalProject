# Written by S. Mevawala, modified by D. Gitzel

from curses import has_colors
from time import time
import logging
import threading
import socket
import hashlib
import channelsimulator
import utils
import sys

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
def getACK(self):
        return self.simulator.u_receive()

class mySend(Sender):
    

    def send (self, data):
        self.logger.info("Sending on port: {} and waiting for ACK on port: {}".format(self.outbound_port, self.inbound_port))
        while True:
            try:
                checksum = hashlib.md5(bytes(bytearray(data))).digest()[:16]
                sendTime = int(time() * 1000)
                self.simulator.u_send(data)  # send data
                ack = ""
                l = []
                l.extend(bytearray(checksum))
                print l
                
                test = RunWithTimeout(getACK, self)
                test.run(0.1)
                ack = self.simulator.u_receive()  # receive ACK
               # self.logger.info("Got ACK from socket: {}".format(
                 #   ack.digest()))  # note that ASCII will only decode bytes in the range 0-127
                print "Got ACK"
                l = []
                l.extend(ack)
                print l
                if (ack == bytearray(checksum)):
                    break 
                else:
                    pass
            except socket.timeout:
                pass



class BogoSender(Sender):

    def __init__(self):
        super(BogoSender, self).__init__()

    def send(self, data):
        self.logger.info("Sending on port: {} and waiting for ACK on port: {}".format(self.outbound_port, self.inbound_port))
        while True:
            try:
                self.simulator.u_send(data)  # send data
                ack = self.simulator.u_receive()  # receive ACK
                self.logger.info("Got ACK from socket: {}".format(
                    ack.decode('ascii')))  # note that ASCII will only decode bytes in the range 0-127
                break
            except socket.timeout:
                pass

class RunWithTimeout(object):
    def __init__(self, function, args):
        self.function = function
        self.args = args
        self.answer = None

    def worker(self):
        self.answer = self.function(*self.args)

    def run(self, timeout):
        thread = threading.Thread(target=self.worker)
        thread.start()
        thread.join(timeout)
        return self.answer

if __name__ == "__main__":
    # test out BogoSender
    DATA = bytearray(sys.stdin.read())
    sndr = mySend()
    sndr.send(DATA)