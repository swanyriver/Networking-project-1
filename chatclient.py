import sys
import socket

def getInput(user):
    inpt = raw_input('%s>'%user)
    return inpt.strip()

def main(argv):
    #todo replace with safe parsing
    #specify host name and port number on the command line.
    TCP_IP = argv[0]
    TCP_PORT = int(argv[1])
    BUFFER_SIZE = 512
    QUIT="\quit"

    print "HOST:%s PORT:%d"%(TCP_IP, TCP_PORT)

    # create socket and connect to server specified in command line
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((TCP_IP, TCP_PORT))
    s.settimeout(.2)

    userHandle="player1"
    #TODO determine if verticalClient or horizontalClient

    msg = ""

    while msg != QUIT:

        msg = getInput("TEMPHANDLE")
        s.sendall(msg)

        #get update from server
        serverResponse = s.recv(BUFFER_SIZE)
        print serverResponse


    s.close()
    print "Connection with server closed"


if __name__ == "__main__":
    main(sys.argv[1:])
