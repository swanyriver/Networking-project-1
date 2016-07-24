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



