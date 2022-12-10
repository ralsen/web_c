#!/usr/bin/env python

import requests
import time
import socket

BASE_URL = 'http://172.19.159.192:8080'

device = dict()
device["name"] = "Testrechner"
#device["name"] = socket.gethostname()
device["IP"] = socket.gethostbyname(socket.gethostname())
device["Version"] = "tolle Version"
device["Hardware"] = "super Hardware"
device["Network"] = "ESPNet"
device["APName"] = "APNet"
device["MAC"] = "AC_0B_FB_D6_41_74"
device["TransmitCycle"] = "100"
device["MeasuringCycle"] = "101"
device["Hash"] = "0xabcdef"
device["Size"] = "0x123"
device["PageReload"] = "10"
device["Server"] = BASE_URL
device["delivPages"] = "1"
device["goodTrans"] = "2"
device["badTrans"] = "3"
device["LED"] = "on"
device["uptime"] = str((time.time()))
device["Adress_0"] = "0123456789abcdef"
device["Value_0"] = "18"
device["Adress_1"] = "fedcba9876543210" 
device["Value_1"] = "20"


print("Client started, sending to: ", BASE_URL)

while True:
    device["uptime"] = str((time.time()))
    try:
      # print("sending: ", device, " to: ", BASE_URL) 
      response = requests.post(f"{BASE_URL}/", json=device)
    except:
      print("could not send, abort: ", response)
      #exit()
    print(response.text)
    time.sleep(1)
