#!/usr/bin/python
import logging, socket, sys

__NAME__ = "wbRedirector.py"
UDP_IP = "127.0.0.1"
UDP_PORT_SEND = 5005
UDP_PORT_LISTEN = 5006

sock_send = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock_listen = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

sock_listen.bind((UDP_IP, UDP_PORT_LISTEN))

logging.basicConfig(filename='example.log',level=logging.DEBUG)

logging.debug('%s called.' % (__NAME__))

while True:
	line = sys.stdin.readline().strip()
	logging.debug('Received %s from Squid.' % (line))
	list = line.split(' ')
        redirect = '%s\n' % (list[0])
	logging.debug('Returning %s.' % (redirect))
        sock_send.sendto(redirect, (UDP_IP, UDP_PORT_SEND))
        logging.debug('Waiting for response...')
        data, addr = sock_listen.recvfrom(1024)
        logging.debug('Received %s from %s.' % (data, addr))
        if (data == "OK"):
            logging.debug('Returning %s' % redirect)
            sys.stdout.write(redirect)
	    sys.stdout.flush()
        elif (data == "NO"):
            logging.debug('Returning 404\n")
            sys.stdout.write("404\n")
            sys.stdout.flush() 
