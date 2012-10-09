#!/usr/bin/python
import socket, threading
from Tkinter import *

UDP_IP = "127.0.0.1"
UDP_PORT = 5005

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

class SocketThread(threading.Thread):
    def run():
        while(run==True):
            data, addr = sock.recvfrom(1024)
           
