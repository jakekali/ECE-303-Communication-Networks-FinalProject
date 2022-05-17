import logging
import hashlib
import channelsimulator
import utils
import sys
import socket
import struct

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
            print(len(l))
            l.extend(bytearray(self.hash))
            print(len(l))
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
        


class myReceive(Receiver):
    ACK_DATA = bytes(123)

    
    def receive(self):
        self.logger.info("Receiving on port: {} and replying with ACK on port: {}".format(self.inbound_port, self.outbound_port))
        dimension = 10
        storeArray = [[0] for i in range(0,dimension)]
        finalStore = [0]
        
        #Tests the packet class
        # test_packet = packets(754,struct.pack("I",777))
        # sendMe = test_packet.mail()
        # test_packet2 = packets(sendMe)
        # print(struct.unpack("I",test_packet2.dataOut())[0])
        
        
        while True:
            try:
                #print("trying to recieve: ")
                packet_in = self.simulator.u_receive()  # receive data
                #print("recieved")
                incoming_packet = packets(packet_in)
                if (incoming_packet.isCorr()):
                    num = incoming_packet.number
                    data = incoming_packet.dataOut()
                    if (num<dimension):
                        storeArray[num] = [1, data]
                        #dimension = dimension + 1
                    else:
                        storeArray.extend([[] for i in ((num-dimension)+1)])
                        dimension = num + 1
                    
                    #print("=PACKET #{} RECIEVED".format(num))
                    ack_pack = packets(num,struct.pack("I",num))
                    self.logger.info("Sent ACK NUM: {} and it has data: {}".format(num, data))

                    self.simulator.u_send(ack_pack.mail())
                    #print(ack_pack)
            except socket.timeout:
                #print ("Timeout")
                store = ""
                for x in range(0,dimension-1):
                    if (storeArray[x][0] ==1):

                        toAdd = storeArray[x][1]
                        
                        store = store + toAdd
                        print(store)
                        sys.stdout.write(store)

                        #print (storeArray)
                
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
    print ()