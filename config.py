#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from logging import Logger
import yaml
import platform
import re
import DataStore as ds

with open("./yml/config.yml", "r") as ymlfile:
    cfg = yaml.safe_load(ymlfile)

logSuffix = cfg["suffixes"]["log"]
dataSuffix = cfg["suffixes"]["data"]
logYML = cfg["debug"]["logYML"]
datefmt = cfg["debug"]["datefmt"]
hirestime = cfg["debug"]["hirestime"]

LogPath = cfg["pathes"]["ROOT_PATH"] + cfg["pathes"]["LOG"]
DataPath = cfg["pathes"]["ROOT_PATH"] + cfg["pathes"]["DATA"]
RRDPath = cfg["pathes"]["ROOT_PATH"] + cfg["pathes"]["RRD"]
YMLPath = cfg["pathes"]["ROOT_PATH"] + cfg["pathes"]["YML"]

with open(YMLPath + cfg["files"]["DATASTORE_YML"], "r") as file:
    StoreYML = yaml.safe_load(file)
ds.DS(StoreYML) 

print(cfg["devices"])
if "No_Name_70_03_9F_9A_7C_05" in cfg["devices"]:
    print("######### das gibt es ########")
    
print(cfg["archive"])
