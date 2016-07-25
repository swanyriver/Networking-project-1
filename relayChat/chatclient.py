import sys
import socket

REC_BUFFER = 512
MSG_LIMIT = 500
MIN_PORT = 0
PRIVILEGED = 1024
MAX_PORT = 65536
QUIT = "\\quit"


def getInput(user):
    inpt = raw_input('%s>'%user)
    if len(inpt) > MSG_LIMIT:
        inpt = inpt[:MSG_LIMIT-2] + "\n"
    return inpt.strip()

def getHandle():
    return raw_input("What would you like your handle to be>").strip()[:10]


def client_main(TCP_IP, TCP_PORT):
    #print "HOST:%s PORT:%d"%(TCP_IP, TCP_PORT)

    # create socket and connect to server specified in command line
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((TCP_IP, TCP_PORT))
    print "peerName:", s.getpeername()
    #s.settimeout(.2)

    handle = getHandle()


    msg = ""

    while True:

        msg = getInput(handle)
        if msg == QUIT:
            break
        s.sendall("%s>%s"%(handle,msg))

        #get update from server
        serverResponse = s.recv(REC_BUFFER)
        print serverResponse


    s.close()
    print "Connection with server closed"


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "must supply host and port number"
        sys.exit(1)

    port = None
    try:
        port = int(sys.argv[2])
        if not PRIVILEGED < port < MAX_PORT: raise ValueError("Out of range")
    except ValueError:
        print "Invalid port supplied"
        sys.exit(1)

    client_main(sys.argv[1], port)
