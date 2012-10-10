#!/usr/bin/python
import logging, socket, sys

__NAME__ = "wbRedirector.py"
UDP_IP = "127.0.0.1"
UDP_PORT_SEND = 5005
UDP_PORT_RECV = 5006

sock_send = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock_recv = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

sock_recv.bind((UDP_IP, UDP_PORT_RECV))

logging.basicConfig(filename='example.log',level=logging.INFO)

logging.debug('%s started...' % (__NAME__))

while True:
    line = sys.stdin.readline().strip()
    logging.debug('Received %s from Squid.' % (line))
    list = line.split(' ')
    redirect = '%s\n' % (list[0])
    logging.info('Sending %s to GUI.' % list[0])
    sock_send.sendto(redirect, (UDP_IP, UDP_PORT_SEND))
    logging.info('Waiting for response from GUI...')
    data, addr = sock_recv.recvfrom(1024)
    logging.info('Received %s from %s.' % (data, addr))
    if (data == "OK"):
        logging.info('Received OK. Returning %s to squid.' % list[0])
        sys.stdout.write(redirect)
        sys.stdout.flush()
    elif (data == "NO"):
        logging.info('Received NO. Returning 404 to squid.')
        sys.stdout.write("404\n")
        sys.stdout.flush() 
