CFLAGS = -std=gnu99

all: chatclient

chatclient: client.c
	gcc client.c -o chatclient $(CFLAGS)
