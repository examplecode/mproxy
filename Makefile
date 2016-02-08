CC = gcc
CFLAGS = -g -Wall -Werror

all: mproxy

mproxy: mproxy.o
	$(CC) $(CFLAGS) mproxy.o -o mproxy

mproxy.o: mproxy.c
	$(CC) $(CFLAGS) -c mproxy.c

clean:
	rm -rf *.o
	rm mproxy