#coding: UTF-8

from blescan import BleScan
import sys
import bluetooth._bluetooth as bluez
import time
from datetime import datetime, timedelta, tzinfo
import slackweb
from gsheet import SpreadSheet
import privatedb

class Syain():
    def __init__(self, name, mac, slackid):
        self.name = name
        self.mac = mac
        self.slackid = slackid
        self.losttime = 0
        self.flagRoom = 0

class JST(tzinfo):
    def utcoffset(self, dt):
        return timedelta(hours=9)


    def dst(self, dt):
        return timedelta(0)


    def tzname(self, dt):
        return 'JST'

bs = BleScan()
sheet = SpreadSheet(privatedb.SHEETID)

syainList = []

for item in privatedb.SYAIN:
    syainList.append(Syain(item["NAME"], item["MAC"], item["SLACKID"]))

TIMEOUT = 60 # sec
dev_id = 0

try:
    sock = bluez.hci_open_dev(dev_id)
    print "ble thread started"

except:
    print "error accessing bluetooth device..."
    sys.exit(1)

bs.hci_le_set_scan_parameters(sock)
bs.hci_enable_le_scan(sock)

cnt = 0
while True:
    returnedList = bs.parse_events(sock, 10)
    #print "----------"

    for index, item in enumerate(syainList):
        for beacon in returnedList:
            if item.mac == beacon.MACADDRESS:
                if item.flagRoom == 0:
                    print item.name + "-san, find!!!"
                    item.flagRoom = 1
                    cnt += 1

                    #Change status
                    sheet.write(index+1, [item.name, "IN", datetime.now(tz=JST()).strftime("%H:%M:%S")])

                    #postString = item.slackid
                    #postString += " entry"
                    #slack = slackweb.Slack(url=privatedb.SLACKURL)
                    #slack.notify(text=postString)

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
                    cnt -= 1

                    #Change status
                    sheet.write(index+1, [item.name, "OUT", datetime.now(tz=JST()).strftime("%H:%M:%S")])
                    if cnt < 1:
                        postString = item.slackid
                        postString += ", Security"
                        slack = slackweb.Slack(url=privatedb.SLACKURL)
                        slack.notify(text=postString)

                else:
                    print "Lost time: %d" %(time.time() - item.losttime)
