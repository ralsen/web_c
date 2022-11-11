#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from logging import Logger
import yaml
import platform
import re
import DataStore as ds

with open("config.yml", "r") as ymlfile:
    cfg = yaml.safe_load(ymlfile)


logSuffix = cfg["suffixes"]["log"]
dataSuffix = cfg["suffixes"]["data"]
logYML = cfg["debug"]["logYML"]
datefmt = cfg["debug"]["datefmt"]
hirestime = cfg["debug"]["hirestime"]


with open(cfg["pathes"]["CONFIG_PATH"] + cfg["DATASTORE_YML"], "r") as file:    
    loc = yaml.safe_load(file)
cfg.update(yaml.safe_load(open(cfg["pathes"]["CONFIG_PATH"] + cfg["DATASTORE_YML"])))

DataStorePath = cfg["pathes"]["DATA_STORE_PATH"]

with open(cfg["pathes"]["CONFIG_PATH"] + cfg["DATASTORE_YML"], "r") as file:
    StoreYML = yaml.safe_load(file)

ds.DS(StoreYML) ######
#print("-----------------\nDataStore: \n", ds.DataStore.keys(), "\n-----------------")
# print("#######", ds.DataStore["EDAG_old"].DataShelf)