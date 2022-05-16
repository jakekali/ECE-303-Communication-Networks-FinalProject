import logging
import hashlib
import channelsimulator
import utils
import sys
import socket

class Receiver(object):

    def __init__(self, inbound_port=50005, outbound_port=50006, timeout=10, debug_level=logging.INFO):
        self.logger = utils.Logger(self.__class__.__name__, debug_level)

        self.inbound_port = inbound_port
        self.outbound_port = outbound_port
        self.simulator = channelsimulator.ChannelSimulator(inbound_port=inbound_port, outbound_port=outbound_port,
                                                           debug_level=debug_level)
        self.simulator.rcvr_setup(timeout)
        self.simulator.sndr_setup(timeout)

    def receive(self):
        raise NotImplementedError("The base API class has no implementation. Please override and add your own.")

class myReceive(Receiver):
    ACK_DATA = bytes(123)

    
    def receive(self):
        self.logger.info("Receiving on port: {} and replying with ACK on port: {}".format(self.inbound_port, self.outbound_port))
        dimension = 100
        storeArray = [[0] for i in dimension]
        finalStore = [0]
        
        while True:
            try:
                packet = self.simulator.u_receive()  # receive data
                checksum = hashlib.md5(bytes(bytearray(packet[0:1003]))).digest()[:16]
                data = bytearray(packet[0:999])
                #received number is byte 1000 to 1004
                num = bytes(bytearray(packet[1000:1003]))
                #hash is bytes 1005 to 1016
                receivedHash = bytes(bytearray(packet[1004:1020]))
                if (checksum == receivedHash):
                    if (num<dimension):
                        storeArray[num] = [1, data]
                        dimension = dimension + 1
                    else:
                        storeArray.extend([[] for i in ((num-dimension)+1)])
                        dimension = num
                    
                #sent checksum is in bytes 1001 to 1017
                #self.logger.info("Got data from socket: {}".format(
                 #   data.decode('ascii')))  # note that ASCII will only decode bytes in the range 0-127
                sys.stdout.write(packet)
                #toSend = checksum.encode()
                print ("Sending ACK")
                self.simulator.u_send(bytearray(packet[1000:1003]) + bytearray(packet[1000:1003]) + bytearray(packet[1000:1003]))  # send ACK
            except socket.timeout:
                for x in dimension:
                    finalStore[0].append(storeArray[x][1])

                sys.exit()


class BogoReceiver(Receiver):
    ACK_DATA = bytes(123)

    def __init__(self):
        super(BogoReceiver, self).__init__()

    def receive(self):
        self.logger.info("Receiving on port: {} and replying with ACK on port: {}".format(self.inbound_port, self.outbound_port))
        while True:
            try:
                data = self.simulator.u_receive()  # receive data
                self.logger.info("Got data from socket: {}".format(
                    data.decode('ascii')))  # note that ASCII will only decode bytes in the range 0-127
                sys.stdout.write(data)
                self.simulator.u_send(BogoReceiver.ACK_DATA)  # send ACK
            except socket.timeout:
                sys.exit()

if __name__ == "__main__":
    # test out BogoReceiver
    rcvr = myReceive()
    rcvr.receive()