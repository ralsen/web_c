#!/usr/bin/env python

import requests
import time
import socket

BASE_URL = 'http://192.168.1.34:8080'

device = dict()
device["name"] = socket.gethostname()
device["ip"] = socket.gethostbyname(socket.gethostname())
device["uptime"] = str(int(time.time()))
device["hello"] = "world"

print("Client started, sending to: ", BASE_URL)

while True:
    device["uptime"] = str((time.time()))
    try:
      response = requests.post(f"{BASE_URL}/", json=device)
    except:
      print("could not send, abort")
      exit()
    print(response.text)
    time.sleep(1)
