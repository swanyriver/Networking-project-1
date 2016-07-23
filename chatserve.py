import socket
import sys
import SocketServer
import select

REC_BUFFER = 512

class ChatTCPHandler(SocketServer.BaseRequestHandler):

    def handle(self):
        # self.request is the TCP socket connected to the client
        for kv in self.__dict__.items():
            print kv
        print dir(self)
        print type(self)
        print dir(self.request)
        print self.__doc__
        while True:
            data = self.request.recv(REC_BUFFER)
            if len(data) == 0:
                #other end has "hung up"
                print "%s has disconnected"%(str(self.client_address))
                return
            data = data.strip()

            print "%r>%s"%(self.client_address, data)
            # just send back the same data, but upper-cased
            self.request.sendall(data.upper())


def serverStartupMessage(portNum, hostName):
    return "Server script started with hostname:%s port#:%d"%(hostName, portNum)



MIN_PORT = 0
MAX_PORT = 65536

if __name__ == "__main__":

    portNum = None
    hostName = None

    if len(sys.argv) < 2:
        print "(SERVER-TERMINATED) server must be launched with port number as first argument"
        exit()

    try:
        portNum = int(sys.argv[1])
        if not portNum or not MIN_PORT <= portNum <= MAX_PORT:
            raise ValueError("Port number out of range")
    except ValueError as error:
        print "(SERVER-TERMINATED) port number argument must be an integer between 0 to 65536 <%s>"%error
        exit()

    try:
        hostName = socket.gethostname()
        if not hostName:
            raise RuntimeError
    except RuntimeError:
        print "(SERVER-TERMINATED) Unable to get host-name"
        exit()

    print serverStartupMessage(portNum, hostName)

    #### invariant:
    #### server launched with valid command line arguments

    #server = SocketServer.TCPServer((hostName, portNum), MyTCPHandler)
    server = None
    while not server:
        try:
            server = SocketServer.TCPServer(("localhost", portNum), ChatTCPHandler)
        except socket.error as e:
            if e.errno == 98:
                print "Port # %d is unavailable currently"%portNum,
                response = raw_input("would you like to try %d? (y/n)"%((portNum+1)%MAX_PORT))
                if response.lower() == "y" or response.lower == "yes":
                    portNum = (portNum + 1)%MAX_PORT
                else:
                    print "(SERVER-TERMINATED) due to port unavailability"
                    exit()

            else:
                print "(SERVER-TERMINATED) due to failure to instantiate SocketServer object: <%s>"%str(e)
                exit()


    print "TCP Server Instantiated ", server.server_address

    # Activate the server; this will keep running until keyboard interupt or SIGINT
    print "BEFORE SERVER FOREVER"
    server.serve_forever()
    #this code is never reached
    print "AFTER SERVER FOREVER"


# import socket;
# sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# result = sock.connect_ex(('127.0.0.1',80))
# if result == 0:
#    print "Port is open"
# else:
#    print "Port is not open"
#
    ###############################################3
# import socket
# from contextlib import closing
#
# def check_socket(host, port):
#     with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
#         if sock.connect_ex((host, port)) == 0:
#             print "Port is open"
#         else:
#             print "Port is not open"


# class ThreadedTCPStreamServer(SocketServer.ThreadingMixin, SocketServer.TCPServer):
#     def __init__(self, server_address, RequestHandlerClass, bind_and_activate=True,
#                  queue=None):
#         self.queue = queue
#         SocketServer.TCPServer.__init__(self, server_address, RequestHandlerClass,
#                                         bind_and_activate=bind_and_activate)
#
# class ThreadedTCPStreamHandler(SocketServer.StreamRequestHandler):
#     def __init__(self, request, client_address, server):
#         self.queue = server.queue
#         StreamRequestHandler.__init__(self, request, client_address, server)
#
#     def handle(self):
#         while True:
#             self.data = self.rfile.readline().strip()
#             if not self.data:
#                 break
#             cur_thread = threading.current_thread()
#             command = self.data[0:2]
#             if command == "nr":
#                 info = self.data[2:]
#                 t1 = info.split("|")
#                 title = t1[0]
#                 self.queue.put(info)
#                 self.finish()
