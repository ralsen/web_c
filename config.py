#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
import yaml
import platform
import re
import DataStore as ds
import socket
import datetime

dcfg = dict()
dcfg["logSuffix"] = None
dcfg["dataSuffix"] = None
dcfg["logYML"] = None
dcfg["datefmt"] = None
dcfg["hirestime"] = None
dcfg["LogPath"] = None
dcfg["DataPath"] = None
dcfg["RRDPath"] = None
dcfg["YMLPath"] = None

def init():
    global  dcfg

    with open("./yml/config.yml", "r") as ymlfile:
        ymlcfg = yaml.safe_load(ymlfile)
    dcfg["logSuffix"] = ymlcfg["suffixes"]["log"]
    dcfg["dataSuffix"] = ymlcfg["suffixes"]["data"]
    dcfg["logYML"] = ymlcfg["debug"]["logYML"]
    dcfg["datefmt"] = ymlcfg["debug"]["datefmt"]
    dcfg["hirestime"] = ymlcfg["debug"]["hirestime"]

    dcfg["LogPath"] = ymlcfg["pathes"]["ROOT_PATH"] + ymlcfg["pathes"]["LOG"]
    dcfg["DataPath"] = ymlcfg["pathes"]["ROOT_PATH"] + ymlcfg["pathes"]["DATA"]
    dcfg["RRDPath"] = ymlcfg["pathes"]["ROOT_PATH"] + ymlcfg["pathes"]["RRD"]
    dcfg["YMLPath"] = ymlcfg["pathes"]["ROOT_PATH"] + ymlcfg["pathes"]["YML"]

    x = datetime.datetime.now()
    logging.basicConfig(filename=dcfg["LogPath"] + socket.gethostname()+x.strftime(dcfg["logSuffix"])+".log",
                        level=logging.DEBUG,
                        format='%(asctime)s :: %(levelname)-s :: %(message)s [%(name)s] [%(lineno)s]',
                        datefmt=dcfg["datefmt"])

    logging.info("\r\n")
    logging.info("-----------------------------------------------------------")
    logging.info("dcfg is initialized ---> " +str(dcfg))
    with open(dcfg["YMLPath"] + ymlcfg["files"]["DATASTORE_YML"], "r") as file:
        StoreYML = yaml.safe_load(file)
    ds.DS(StoreYML) 

    print(ymlcfg["devices"])
    if "No_Name_70_03_9F_9A_7C_05" in ymlcfg["devices"]:
        print("######### das gibt es ########")
        
    print(ymlcfg["archive"])
    print(dcfg)
    logging.info("everything initialized !!!")