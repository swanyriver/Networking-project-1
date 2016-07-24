import socket
import sys
import SocketServer
from collections import namedtuple

NetworkInfo = namedtuple("networkInfo", ['portNum', 'hostName', 'ipAddress'])

## Constants
REC_BUFFER = 512
MSG_LIMIT = 500
MIN_PORT = 0
PRIVILEGED = 1024
MAX_PORT = 65536
CONNECTION_QUE_SIZE = 10
HANDLE = "SERVER"

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

def nextPort(portNum):
    portNum += 1
    return portNum if PRIVILEGED < portNum <= MAX_PORT else PRIVILEGED

def getListeningSocket(portNum, hostName, ipAddress):
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # todo port avail and permission check (can be coppied from above pretty easily)
    while True:
        try:
            serverSocket.bind((hostName, portNum))
            # binding to port was successful exit loop
            break
        except socket.error as e:
            # for convinince of testing on flip server with congestion ports, advance consecutively
            if e.errno == 98 or e.errno == 13:
                candidate = nextPort(portNum)
                print "Port # %d is %s"%(portNum, ("unavailable" if e.errno == 98 else "privileged")),
                response = raw_input("would you like to try %d? (y/n)"%candidate)
                if response.lower() == "y" or response.lower == "yes":
                    portNum = candidate
                else:
                    print "(SERVER-TERMINATED) due to port unavailability"
                    exit()

    serverSocket.listen(CONNECTION_QUE_SIZE)
    return serverSocket

def getInput():
    inpt = raw_input("%s>"%HANDLE)
    inpt = inpt.strip()
    if len(inpt) > MSG_LIMIT:
        inpt = inpt[:MSG_LIMIT]
        print " <MESSAGE TRUNCATED TO %d CHARS>"%MSG_LIMIT
    return inpt


def chatWithClient(clientSocket):
    while True:
        try:
            msgFromClient = clientSocket.recv(REC_BUFFER)
        except socket.errno as e:
            print "(SERVER-STATE) unable to recieve from client"
            break
        if len(msgFromClient) == 0:
            # other end has "hung up"
            peername = None
            try:
                str(clientSocket.getpeername())
            except socket.error:
                pass
            finally:
                print peername if peername else "client", "has disconnected"

            break
        msgFromClient = msgFromClient.strip()

        #with socket info
        #print "%r>%s" % (clientSocket.getpeername(), msgFromClient)

        print msgFromClient

        # prompt server for chat message
        msgToClient = getInput()
        try:
            clientSocket.sendall("%s>%s"%(HANDLE,msgToClient))
        except socket.error as e:
            if e.errno == 107 or e.errno == 104:
                print "(SERVER-STATE) Cannot send message, client has disconnected"
            else:
                print "(SERVER STATE) Unable to send message, disconnecting from client"
            clientSocket.close()
            break

def main(argv):

    initInfo = InitializeParamaters(argv)
    print "Server script started with hostname:%s ip-addr:%s port#:%d" % (initInfo.hostName,
                                                                          initInfo.ipAddress,
                                                                          initInfo.portNum)
    #### invariant:
    #### server script launched with valid command line arguments

    serverSocket = getListeningSocket(*initInfo)
    serverIp, serverPort = serverSocket.getsockname()
    print "Listening on port %d To connect on remote host run either:"%serverPort
    print "python chatclient.py %s %d" % (initInfo.ipAddress, serverPort)
    print "python chatclient.py %s %d" % (initInfo.hostName, serverPort)
    print "./chatclient %s %d 3>pipe" % (initInfo.ipAddress, serverPort)
    print "./chatclient %s %d 3>pipe" % (initInfo.hostName, serverPort)

    #### invariant:
    #### server socket has bound to an open port and is listening for connections

    #todo modularize this
    #tod fork procecess for chatting and display with queue
    #accept consective connections
    while True:
        print "\n Awaiting client connections \n"
        (clientSocket, address) = serverSocket.accept()
        print "connected to:", address

        chatWithClient(clientSocket)


if __name__ == "__main__":
    main(sys.argv)







