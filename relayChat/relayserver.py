import socket
import sys
from collections import namedtuple
from log import log
from multiprocessing import Pipe, Process


NetworkInfo = namedtuple("networkInfo", ['portNum', 'hostName', 'ipAddress'])

## Constants
REC_BUFFER = 512
MSG_LIMIT = 500
MIN_PORT = 0
PRIVILEGED = 1024
MAX_PORT = 65536
CONNECTION_QUE_SIZE = 10
HANDLE = "SERVER"
QUIT = "\\quit"
TIMEOUT = .1
TIMEOUT = 1.5


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
            # for convenience of testing on flip server with congestion ports, advance consecutively
            if e.errno == 98 or e.errno == 13:
                candidate = nextPort(portNum)
                print "Port # %d is %s"%(portNum, ("unavailable" if e.errno == 98 else "privileged")),
                print "would you like to try %d? (y/n)"%candidate,
                response = raw_input()
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




def relayToClient(clientSocket, pipeToServer):
    """
    :type clientSocket: socket.socket
    """
    clientSocket.settimeout(TIMEOUT)
    while True:
        #log("(PROCESS STATE) checking socket again\n")

        msgFromClient = None
        try:
            msgFromClient = clientSocket.recv(REC_BUFFER)
        except socket.timeout:
            pass
        except socket.error as e:
            log( "(PROCESS-STATE) unable to recieve from client\n" )
            break


        if msgFromClient and len(msgFromClient) == 0:
            # other end has "hung up"
            peername = None
            try:
                str(clientSocket.getpeername())
            except socket.error:
                pass
            finally:
                log(peername if peername else "client" + "has disconnected\n")

            break

        if msgFromClient:
            msgFromClient = msgFromClient.strip()
            msgFromClient = msgFromClient.replace('\n','')
        if msgFromClient:
            pipeToServer.send(msgFromClient)

        # prompt server for chat message
        messageToClient = None
        if pipeToServer.poll(TIMEOUT):
            messageToClient = pipeToServer.recv()
            if not messageToClient: continue
            messageToClient = messageToClient.strip()
            messageToClient.replace('\n', '')
            if not messageToClient: continue

            log("(PROCESS-STATE) message to send to clients: %s\n"%str(messageToClient))

            try:
                clientSocket.sendall(messageToClient)
            except socket.timeout:
                log("(PROCESS STATE) send timedout\n")
            except socket.error as e:
                if e.errno == 107 or e.errno == 104:
                    log( "(PROCESS-STATE) Cannot send message, client has disconnected\n")
                else:
                    log( "(PROCESS STATE) Unable to send message, disconnecting from client\n" )
                clientSocket.close()
                return

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
    print ".././chatclient %s %d" % (initInfo.ipAddress, serverPort)
    print ".././chatclient %s %d" % (initInfo.hostName, serverPort)
    print "python chatclient.py %s %d" % (initInfo.ipAddress, serverPort)
    print "python chatclient.py %s %d" % (initInfo.hostName, serverPort)
    print "\n Awaiting client connections \n"

    #### invariant:
    #### server socket has bound to an open port and is listening for connections

    #accept concurrent connections
    serverSocket.settimeout(TIMEOUT)
    # {process: duplex-Pipe}
    pool = {}

    #will run until keyboard interrupt
    while True:
        try:
            log("Listening on port: %d\n"%serverPort)
            (clientSocket, address) = serverSocket.accept()
            if clientSocket:
                log("connected to:%s\n" % str(address))
                myEnd, processEnd = Pipe(duplex=True)
                chatConnection = Process(target=relayToClient, args=(clientSocket, processEnd))
                chatConnection.start()
                pool[chatConnection] = myEnd
        except socket.timeout:
            pass

        pool = {k:v for k,v in pool.items() if k.is_alive()}

        log("communing with process pool %s\n"%str(pool))

        messages = []
        for proc, pipe in pool.items():
            if pipe.poll(TIMEOUT):
                msg = pipe.recv()
                if msg: messages.append((proc, msg))

        if not messages:
            continue

        log("msgsFromClients:%s\n" % str(messages))
        print "\n".join(msg[1] for msg in messages)

        pool = {k:v for k,v in pool.items() if k.is_alive()}
        for proc, pipe in pool.items():
            for p, msg in messages:
                if p != proc:
                    log("sending {%s} to {%s}\n"%(msg, proc))
                    pipe.send(msg)


if __name__ == "__main__":
    main(sys.argv)







