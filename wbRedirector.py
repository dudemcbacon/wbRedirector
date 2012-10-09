#!/usr/bin/python
import logging, socket, sys

__NAME__ = "wbRedirector.py"
UDP_IP = "127.0.0.1"
UDP_PORT = 5005

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

logging.basicConfig(filename='example.log',level=logging.DEBUG)

logging.debug('%s called.' % (__NAME__))

while True:
	line = sys.stdin.readline().strip()
	logging.debug('Received %s from Squid.' % (line))
	list = line.split(' ')
        redirect = '%s\n' % (list[0])
	logging.debug('Returning %s.' % (redirect))
        sock.sendto(redirect, (UDP_IP, UDP_PORT))
        logging.debug('finished sending')
        sys.stdout.write(redirect)
	sys.stdout.flush()
