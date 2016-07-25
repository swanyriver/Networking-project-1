chatserver.py will create a server listening for connections on the supplied port and accepts consecutive connections
(after one client disconnects the next client connected to via socket.accept() will begin a chat session) with
clients and exchange messages with them back-and-forth,  halting for input from the server before sending to client
and awaiting response from client.

program was tested on flip1.engr.oregonstate.edu flip2.engr.oregonstate.edu and was capable of connecting a server
process on flip1 to a client process on flip2 and vice-versa.

---------------------------
---- Compile and Run ------
---------------------------

-----Server------
To run server program no compilation necessary, supply a port number as first argument:
python chatserver.py 9999

----Client------
To run the client first compile client.c using supplied makefile via "make all" or "make chatclient"
equivalent to: gcc client.c -o chatclient -std=gnu99
NOTE:  do not run "make client.c",  this is equivalent to "gcc client.c -o client" and is not the proper compilation

Then connect to server program running by supplying hostname/ip-address and port as paramaters to chatclient executable.
(chatserver.py will display the necessary hostname and port number when launched)


---------------------------
---- Example Execution ----
---------------------------

$ ssh <username>@flip2.engr.oregonstate.edu
$ cd BrandonSwansonCS372Project1
$ python chatserver.py 9999
Server script started with hostname:flip2.engr.oregonstate.edu ip-addr:128.193.54.182 port#:9999
Listening on port 9999 To connect on remote host run either:
./chatclient 128.193.54.182 9999
./chatclient flip2.engr.oregonstate.edu 9999

 Awaiting client connections

connected to: ('128.193.54.168', 57073)
brandon>hello server
SERVER>why hello client
brandon>how are you
SERVER>im good im running in python and on flip2 how about you
brandon>im on flip 1 running c
SERVER>good
client has disconnected

 Awaiting client connections



--------client--------
$ ssh <username>@flip1.engr.oregonstate.edu
$ cd BrandonSwansonCS372Project1
$make
gcc client.c -o chatclient -std=gnu99
$ ./chatclient flip2.engr.oregonstate.edu 9999
Client chat program launched preparing to connect to:
Host:flip2.engr.oregonstate.edu, port:9999
What would you like your chat handle to be>brandon
brandon>hello server
SERVER>why hello client
brandon>how are you
SERVER>im good im running in python and on flip2 how about you
brandon>im on flip 1 running c
SERVER>good
brandon>\quit

Disconnected from server






---------------------------------------------------------------------
------- EXTRA CREDIT ------------------------------------------------
---------------------------------------------------------------------

see contents of relayChat directory

as an extra credit project I created a server that could accept concurrent connections from multiple clients.
Instead of that server being involved in the chatting it instead displays all incoming messages and forwards the
messages to all connected clients (excluding the one that sent the message).  It will continue to accept connections
and begin relieving messages and forwarding all other clients messages at any time even after all clients have
disconnected

The server achieves this by setting a timeout on socket sending, receiving and accepting.  It then alternates between
accepting new connections and receiving and transmitting messages to clients.  It is not multithreaded but is instead
multi-processed,  each new client connection creates a new process and the process and server communicate over a
class wrapper around *nix fifo pipes (called Pipe).

The clients I have implemented that connect to this server still block when waiting for user input so after a user
has submitted input they will see all of the messages from other users (provided it hasn't overflowed either the socket
recieve buffer or the interprocess pipe).  There are two clients available for connecting to this server, one the same
C chatclient from the assignment and another python client in the relayChat folder

I tested this relay server runing on flip2.engr.oregonstate.edu and accepting connections from 3 clients on:
flip1.engr.oregonstate.edu
flip2.engr.oregonstate.edu
flip3.engr.oregonstate.edu

attached is a screenshot of that test


Invocation example

----Server------

$ cd relayChat
$ python relayserver.py 9999
Server script started with hostname:flip2.engr.oregonstate.edu ip-addr:128.193.54.182 port#:9999
Listening on port 9999 To connect on remote host run either:
.././chatclient 128.193.54.182 9999
.././chatclient flip2.engr.oregonstate.edu 9999
python chatclient.py 128.193.54.182 9999
python chatclient.py flip2.engr.oregonstate.edu 9999

 Awaiting client connections

whatUp>hey everyone
dave>hey lads
brandon>we are all on flip
dave>yep flip 1 flip 2
whatUp>even flip 3
brandon>what a lovely day to be testing on flip
dave>see you all next week
whatUp>ok


----Client--1--
.././chatclient flip2.engr.oregonstate.edu 9999


----Client--2--
python chatclient.py flip2.engr.oregonstate.edu 9999




------------------
-- Debug View  ---
------------------


If you would like to observe the multi-process servers activities more closely simply apply the debug patch below
(enables logging, increases timeout delay) and then redirect the stderr stream to a file or pipe

--flip connection 1--- debug-view
$ cd relayChat
$ mkfifo logpipe
$ tail -f logpipe

--flip connection 2 -- server
$ cd relayChat
$ git apply debug.patch
$ python relayserver.py 9999 2>logpipe
Server script started with hostname:flip2.engr.oregonstate.edu ip-addr:128.193.54.182 port#:9999
Listening on port 9999 To connect on remote host run either:
.././chatclient 128.193.54.182 9999
.././chatclient flip2.engr.oregonstate.edu 9999
python chatclient.py 128.193.54.182 9999
python chatclient.py flip2.engr.oregonstate.edu 9999

 Awaiting client connections


--flip connection 3 ----Client--1--
.././chatclient flip2.engr.oregonstate.edu 9999


--flip connection 4 ----Client--2--
python chatclient.py flip2.engr.oregonstate.edu 9999