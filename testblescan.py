# test BLE Scanning software
# jcs 6/8/2014

#coding: UTF-8

from blescan import BleScan
import sys
import bluetooth._bluetooth as bluez
import time
import slackweb
import slackurl

class Syain():
    def __init__(self, name):
        self.name = name
        self.losttime = 0
        self.flagRoom = 0
        self.mac = 0


bs = BleScan()
db = {"Shimada":"20:76:a7:0a:db:d5"}
syainDict = {}

for k, v in db.items():
	syainDict[k] = Syain(k)

TIMEOUT = 10 # sec
dev_id = 0

try:
    sock = bluez.hci_open_dev(dev_id)
    print "ble thread started"

except:
    print "error accessing bluetooth device..."
    sys.exit(1)

bs.hci_le_set_scan_parameters(sock)
bs.hci_enable_le_scan(sock)

while True:
    returnedList = bs.parse_events(sock, 10)
    print "----------"
    for k, v in db.items():

        for beacon in returnedList:
            if v == beacon.MACADDRESS:
                if syainDict[k].flagRoom == 0:
                    print k + "-san, find!!!"
                    syainDict[k].flagRoom = 1
                    #Change status
                    postString = slackurl.SHIMADAID
                    postString += " entry"
                    slack = slackweb.Slack(url=slackurl.SLACKURL)
                    slack.notify(text=postString)
                else:
                    print k + "-san, still in the office"

                syainDict[k].losttime = 0

        #if flag == 0:
        if syainDict[k].flagRoom == 1:
            print k + "-san, beacon is not recieved!"
            if syainDict[k].losttime == 0:
                #Start count Time out
                syainDict[k].losttime = time.time()
            else:
                if (time.time() - syainDict[k].losttime) > TIMEOUT:
                    print k + "-san, out of office"
                    syainDict[k].flagRoom = 0
                    #Change status
                    postString = slackurl.SHIMADAID
                    postString += " exit"
                    slack = slackweb.Slack(url=slackurl.SLACKURL)
                    slack.notify(text=postString)
                else:
                    print "Lost time: %d" %(time.time() - syainDict[k].losttime)
