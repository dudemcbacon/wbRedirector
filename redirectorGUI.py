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
        while(keepgoing==True):
            data, addr = sock.recvfrom(1024)
            parsed_url = urlparse(data)
            domain = '{}://{}/'.format(parsed_url[0], parsed_url[1])
            if domain not in urllist:
                urllist.append(domain)
                listbox.Append(domain)
            else:
                print '%s already caught.' % domain   


app = wx.App()

frame = wx.Frame(None, -1, 'Woodburn SQUID Thinger', size=(500,850))
frame.Show()

def StartThread(event):
	btnStart.Disable()
        btnStop.Enable()
        t = SocketThread()
	t.start()

def StopThread(event):
        btnStart.Enable()
        btnStop.Disable()
        btnCreatePolicy.Enable()
        print urllist

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
