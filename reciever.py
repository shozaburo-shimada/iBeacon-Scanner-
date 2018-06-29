#coding: UTF-8

from blescan import BleScan
import sys
import bluetooth._bluetooth as bluez
import time
import slackweb
import privatedb

class Syain():
    def __init__(self, name, mac, slackid):
        self.name = name
        self.mac = mac
        self.slackid = slackid
        self.losttime = 0
        self.flagRoom = 0

bs = BleScan()
syainList = []

for item in privatedb.SYAIN:
    syainList.append(Syain(item["NAME"], item["MAC"], item["SLACKID"]))

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

    for index, item in enumerate(syainList):
        for beacon in returnedList:
            if item.mac == beacon.MACADDRESS:
                if item.flagRoom == 0:
                    print item.name + "-san, find!!!"
                    item.flagRoom = 1
                    #Change status
                    postString = item.slackid
                    postString += " entry"
                    slack = slackweb.Slack(url=privatedb.SLACKURL)
                    slack.notify(text=postString)
                else:
                    print item.name + "-san, still in the office"

                item.losttime = 0

        if item.flagRoom == 1:
            print item.name + "-san, beacon is not recieved!"
            if item.losttime == 0:
                #Start count Time out
                item.losttime = time.time()
            else:
                if (time.time() - item.losttime) > TIMEOUT:
                    print item.name + "-san, out of office"
                    item.flagRoom = 0
                    #Change status
                    postString = item.slackid
                    postString += " exit"
                    slack = slackweb.Slack(url=privatedb.SLACKURL)
                    slack.notify(text=postString)
                else:
                    print "Lost time: %d" %(time.time() - item.losttime)
