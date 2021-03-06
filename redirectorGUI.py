#!/usr/bin/python
import logging, json, MySQLdb, re, socket, time, threading, urllib, urllib2, wx
from urlparse import urlparse

logging.basicConfig(level=logging.INFO)
logging.info("redirectoryGUI.py starting...")

UDP_IP = "127.0.0.1"
UDP_PORT_RECV = 5005
UDP_PORT_SEND = 5006

urllist = []
whiteList = [
	'cnn.com',
	'turner.com'
]
badTLDs = [
	'doubleclick.net',
	'google-analytics.com',
	'quantserve.com',
	'scorecardresearch.com',
	'atdmt.com',
	'chartbeat.net'
]

conn = MySQLdb.connect(host="localhost", user="root", passwd="bacon", db="squidlog_db")

sock_recv = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock_send = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock_recv.bind((UDP_IP, UDP_PORT_RECV))

startTime = 0
stopTime = 0

keepgoing = True

class SocketThread(threading.Thread):
    def run(self):
        logging.info("SocketThread loop started.")
        while not t.stop_event.isSet():
            data, addr = sock_recv.recvfrom(1024)
            logging.debug("Recieved %s from %s." % (data, addr))
            parsed_url = urlparse(data)
            logging.debug(parsed_url)
            if (parsed_url[0]==""):
                logging.debug("Received URL without preceding http/https.")
                parsed_url = []
                split_domain = data.split(":")
                if (split_domain[1] == "80\n"):
                    logging.debug("Port 80, setting to http.")
                    parsed_url.append("http")
                if (split_domain[1] == "443\n"):
                    logging.debug("Port 443, setting to https.")
                    parsed_url.append("https")
                parsed_url.append(split_domain[0])
            domain = '{}://{}/'.format(parsed_url[0], parsed_url[1])
            logging.info("Domain: %s" % domain)
            if domain not in urllist:
                logging.debug("Domain is not in urllist. Adding.")
                urllist.append(domain)
                clbItem = listbox.Append(domain)
                listbox.Check(clbItem, check=True)
            else:
                logging.debug('%s already caught. Raw URL = %s' % (domain, data))   
            if domain in listbox.GetCheckedStrings():
                logging.info("Domain is checked. Sending OK.")
                sock_send.sendto('OK', (UDP_IP, UDP_PORT_SEND))
            else:
                logging.info("Domain is not checked. Sending NO.")
                sock_send.sendto('NO', (UDP_IP, UDP_PORT_SEND))
        print "SocketThread stopped."   

with open("effective_tld_names.dat.txt") as tld_file:
	 tlds = [line.strip() for line in tld_file if line[0] not in "/\n"]

def get_domain(url, tlds):
    url_elements = urlparse(url)[1].split('.')
    # url_elements = ["abcde","co","uk"]

    for i in range(-len(url_elements), 0):
        last_i_elements = url_elements[i:]
        #    i=-3: ["abcde","co","uk"]
        #    i=-2: ["co","uk"]
        #    i=-1: ["uk"] etc

        candidate = ".".join(last_i_elements) # abcde.co.uk, co.uk, uk
        wildcard_candidate = ".".join(["*"] + last_i_elements[1:]) # *.co.uk, *.uk, *
        exception_candidate = "!" + candidate

        # match tlds: 
        if (exception_candidate in tlds):
            return ".".join(url_elements[i:]) 
        if (candidate in tlds or wildcard_candidate in tlds):
            return ".".join(url_elements[i-1:])
            # returns "abcde.co.uk"

    raise ValueError("Domain not in global list of TLDs")

t = SocketThread()
t.stop_event = threading.Event()
t.stop_event.clear()

app = wx.App()

frame = wx.Frame(None, -1, 'Granite Street Policy Creation Tool', size=(465,1000))
frame.Show()

def StartThread(event):
    btnStart.Disable()
    btnStop.Enable()
    startTime = time.mktime(time.gmtime())
    logging.info('Start time is %d' % startTime)
    t.start()

def StopThread(event):
    btnStart.Enable()
    btnStop.Disable()
    btnCreatePolicy.Enable()
    stopTime = time.mktime(time.gmtime())
    logging.info('Stop time is %d' % stopTime)
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(reply_size) FROM access_log WHERE timestamp >= %d AND timestamp <= %d" % (int(startTime), int(stopTime)))
    result_set = cursor.fetchall()
    lblUsedBand.SetLabel(str(result_set[0][0]))
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

def PrintSelectedItem(event):
	selectedItem = listbox.GetString(listbox.GetSelection())
	logging.info("%s selected." % selectedItem)
	tld = get_domain(selectedItem, tlds)
	logging.info("TLD: %s" % tld)
	if tld in badTLDs:
		logging.info("%s is blacklisted." % seletedItem)

def ExperienceAdjust(event):
	sliderValue = sldExperience.GetValue()
	logging.debug('Slider Value: %d' % sliderValue)
	if sliderValue == 50:
		logging.info('Slider at 50.')
		for domain in listbox.GetStrings():
			tld = get_domain(domain, tlds)
			if tld not in whiteList:
				index = listbox.GetStrings().index(domain)
				logging.info("%s not in whiteList. Index: %d" % (domain,index))
				listbox.Check(index, check=False)
	if sliderValue == 80:
		logging.info('Slider at 80.')
		listbox.SetCheckedStrings(listbox.GetStrings())
		for domain in listbox.GetStrings():
			tld = get_domain(domain, tlds)
			if tld in badTLDs:
				index = listbox.GetStrings().index(domain)
				logging.info("%s in badDomains. Index: %d" % (domain,index))
				listbox.Check(index, check=False)
	elif sliderValue == 100:
		logging.info('Slider at 100.')
		for domain in listbox.GetStrings():
			tld = get_domain(domain, tlds)
			if tld in badTLDs:
				index = listbox.GetStrings().index(domain)
				logging.info("%s in badDomains. Index: %d" % (domain,index))
				listbox.Check(index, check=True)
		

listbox = wx.CheckListBox(frame, 26, pos=(10,130), size=(450, 750))
listbox.Bind(wx.EVT_LISTBOX, PrintSelectedItem)
btnStart = wx.Button(frame, label="Start", pos=(0,0))
btnStart.Bind(wx.EVT_BUTTON, StartThread)

btnStop = wx.Button(frame, label="Stop", pos=(100,0))
btnStop.Bind(wx.EVT_BUTTON, StopThread)
btnStop.Disable()

btnCreatePolicy = wx.Button(frame, label="Create Policy", pos=(200,0))
btnCreatePolicy.Bind(wx.EVT_BUTTON, CreatePolicy)
btnCreatePolicy.Disable()

sldExperience = wx.Slider(frame, -1, 100, 0, 100, (150, 890), (250, -1), wx.SL_AUTOTICKS | wx.SL_HORIZONTAL)
sldExperience.Bind(wx.EVT_SLIDER, ExperienceAdjust)

lblAddress = wx.StaticText(frame, pos=(10, 35), label="IP Address:")
txtAddress = wx.TextCtrl(frame, pos=(150, 35), size=(250, 25))
lblAppName = wx.StaticText(frame, pos=(10, 65), label="App Name:")
txtAppName = wx.TextCtrl(frame, pos=(150, 65), size=(250, 25))
lblPolicyName = wx.StaticText(frame, pos=(10, 95), label="Policy Name:")
txtPolicyName = wx.TextCtrl(frame, pos=(150, 95), size=(250, 25))
lblExperience = wx.StaticText(frame, pos=(10,890), label="Experience:")
lblBandwidth = wx.StaticText(frame, pos=(10, 920), label="Bandwidth Used:")
lblUsedBand = wx.StaticText(frame, pos=(150,920), label="(Press stop button to calculate.)")

app.MainLoop()
