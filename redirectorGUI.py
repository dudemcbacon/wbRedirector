#!/usr/bin/python
import json, re, socket, threading, urllib, urllib2, wx
from urlparse import urlparse

UDP_IP = "127.0.0.1"
UDP_PORT = 5005
urllist = []
index = 0

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

keepgoing = True

class SocketThread(threading.Thread):
    def run(self):
        while not t.stop_event.isSet():
            data, addr = sock.recvfrom(1024)
            parsed_url = urlparse(data)
            if (parsed_url[0]==""):
                parsed_url = []
                split_domain = data.split(":")
                if (split_domain[1] == "80\n"):
                    parsed_url.append("http")
                if (split_domain[1] == "443\n"):
                    parsed_url.append("https")
                parsed_url.append(split_domain[0])
            domain = '{}://{}/'.format(parsed_url[0], parsed_url[1])
            if domain not in urllist:
                urllist.append(domain)
                clbItem = listbox.Append(domain)
                listbox.Check(clbItem, check=True)
            else:
                print '%s already caught. Raw URL = %s' % (domain, data)   
        print "SocketThread stopped."   

t = SocketThread()
t.stop_event = threading.Event()
t.stop_event.clear()

app = wx.App()

frame = wx.Frame(None, -1, 'Woodburn SQUID Thinger', size=(465,920))
frame.Show()

def StartThread(event):
	btnStart.Disable()
        btnStop.Enable()
	t.start()

def StopThread(event):
        btnStart.Enable()
        btnStop.Disable()
        btnCreatePolicy.Enable()
        t.stop_event.set()

def CreatePolicy(event):
        data = {}
        data['domains'] = listbox.GetCheckedStrings()
        if (txtAddress.GetValue() == "" or txtAppName.GetValue() == "" or txtPolicyName.GetValue() == ""):
            print "Must enter a value for IP Address and App Name."
            lblAddress.SetForegroundColour((255,0,0))
            lblAppName.SetForegroundColour((255,0,0))
            lblPolicyName.SetForegroundColour((255,0,0))
        else:
            data['AppName'] = txtAppName.GetValue()
            data['PolicyName'] = txtPolicyName.GetValue()
            jdata = json.dumps(data)
            host = 'http://%s:8080/insertNewRule' % txtAddress.GetValue()
            print 'JSON string: %s' % jdata
            print 'Sending to: %s' % host
            #req = urllib2.Request(host, data)
            urllib2.urlopen(host, jdata)

listbox = wx.CheckListBox(frame, 26, pos=(10,130), size=(450, 750))
btnStart = wx.Button(frame, label="Start", pos=(0,0))
btnStart.Bind(wx.EVT_BUTTON, StartThread)

btnStop = wx.Button(frame, label="Stop", pos=(100,0))
btnStop.Bind(wx.EVT_BUTTON, StopThread)
btnStop.Disable()

btnCreatePolicy = wx.Button(frame, label="Create Policy", pos=(200,0))
btnCreatePolicy.Bind(wx.EVT_BUTTON, CreatePolicy)
btnCreatePolicy.Disable()

lblAddress = wx.StaticText(frame, pos=(10, 35), label="IP Address:")
txtAddress = wx.TextCtrl(frame, pos=(150, 35), size=(250, 25))
lblAppName = wx.StaticText(frame, pos=(10, 65), label="App Name:")
txtAppName = wx.TextCtrl(frame, pos=(150, 65), size=(250, 25))
lblPolicyName = wx.StaticText(frame, pos=(10, 95), label="Policy Name:")
txtPolicyName = wx.TextCtrl(frame, pos=(150, 95), size=(250, 25))

app.MainLoop()
