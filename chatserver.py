import socket
import sys
import SocketServer
from collections import namedtuple

NetworkInfo = namedtuple("networkInfo", ['portNum', 'hostName', 'ipAddress'])

## Constants
REC_BUFFER = 512
MIN_PORT = 0
MAX_PORT = 65536

#
# class ChatTCPHandler(SocketServer.BaseRequestHandler):
#
#     def handle(self):
#         while True:
#             data = self.request.recv(REC_BUFFER)
#             if len(data) == 0:
#                 #other end has "hung up"
#                 print "%s has disconnected"%(str(self.client_address))
#                 return
#             data = data.strip()
#
#             print "%r>%s"%(self.client_address, data)
#             # just send back the same data, but upper-cased
#             self.request.sendall(data.upper())
#
#



def InitializeParamaters(argv):
    portNum = None
    hostName = None
    ipAddress = None
    if len(sys.argv) < 2:
        print "(SERVER-TERMINATED) server must be launched with port number as first argument"
        exit()
    try:
        portNum = int(argv[1])
        if not portNum or not MIN_PORT <= portNum <= MAX_PORT:
            raise ValueError("Port number out of range")
    except ValueError as error:
        print "(SERVER-TERMINATED) port number argument must be an integer between 0 to 65536 <%s>" % error
        exit()
    try:
        hostName = socket.gethostname()
        if not hostName:
            raise RuntimeError
    except RuntimeError:
        print "(SERVER-TERMINATED) Unable to get host-name"
        exit()
    try:
        ipAddress = socket.gethostbyname(hostName)
        if not ipAddress:
            raise RuntimeError
    except RuntimeError:
        print "(SERVER-TERMINATED) Unable to get host ip address"
        exit()

    return NetworkInfo(portNum=portNum, hostName=hostName, ipAddress=ipAddress)


# def createServer(portNum, hostName, ipAddress):
#     # Attempt to instantiate a server instance,  recover from occupied port error and offer use an alternative port
#     server = None
#     while not server:
#         try:
#             if ipAddress.split('.')[0] == "127":
#                 print "launching home network version"
#                 # required for local Ubuntu machine testing
#                 server = SocketServer.TCPServer(("localhost", portNum), ChatTCPHandler)
#             else:
#                 server = SocketServer.TCPServer((hostName, portNum), ChatTCPHandler)
# #                server = SocketServer.TCPServer((ipAddress, portNum), ChatTCPHandler)
#         except socket.error as e:
#             if e.errno == 98:
#                 print "Port # %d is unavailable currently"%portNum,
#                 response = raw_input("would you like to try %d? (y/n)"%((portNum+1)%MAX_PORT))
#                 if response.lower() == "y" or response.lower == "yes":
#                     portNum = (portNum + 1)%MAX_PORT
#                 else:
#                     print "(SERVER-TERMINATED) due to port unavailability"
#                     exit()
#
#             else:
#                 #errno 11 = priviled port
#                 print "(SERVER-TERMINATED) due to failure to instantiate SocketServer object: <%s>"%str(e)
#                 exit()
#
#     return server

#def listenOnSocket(portNum, hostName, ipAddress):


def main(argv):

    initInfo = InitializeParamaters(argv)
    print "Server script started with hostname:%s ip-addr:%s port#:%d" % (initInfo.hostName,
                                                                          initInfo.ipAddress,
                                                                          initInfo.portNum)
    print "To connect on remote host run either:"
    print "python chatclient.py %s %d"%(initInfo.ipAddress, initInfo.portNum)
    print "python chatclient.py %s %d"%(initInfo.hostName, initInfo.portNum)

    #### invariant:
    #### server script launched with valid command line arguments

    # todo modularize this code
    #serverSocket = listenOnSocket(*initInfo)

    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #todo port avail and permission check (can be coppied from above pretty easily)
    serverSocket.bind((initInfo.hostName, initInfo.portNum))
    #serverSocket.bind((initInfo.ipAddress, initInfo.portNum))
    serverSocket.listen(10)

    while True:
        # accept connections from outside
        (clientSocket, address) = serverSocket.accept()

        print "connected to:", clientSocket, address

        while True:
            data = clientSocket.recv(REC_BUFFER)
            if len(data) == 0:
                # other end has "hung up"
                print "%s has disconnected" % (str(clientSocket.getpeername()))
                break
            data = data.strip()

            print "%r>%s" % (clientSocket.getpeername(), data)
            # just send back the same data, but upper-cased
            clientSocket.sendall(data.upper())


    #######################################
    ## abandon ???? #######################
    #######################################
    # server = createServer(*initInfo)
    # print "TCP Server Instantiated ", server.server_address
    #
    # #### invariant:
    # #### SocketServer has been instantiated properly
    #
    # # Activate the server; this will keep running until keyboard interupt or SIGINT
    # print "Launching server that will accept consecutive but not concurrent connections"
    # server.serve_forever()
    # # this code is never reached
    # print "Server has exited"
    ######################################
    ######################################
    ######################################

if __name__ == "__main__":
    main(sys.argv)







