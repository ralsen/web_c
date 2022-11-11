#!/usr/bin/env python3
# -*- coding: utf-8 -*-


#FOL import config as config
import logging
import time
import datetime
import threading
import re
import string

logger = logging.getLogger(__name__)

"""
    this is the DataStore-class()
    the class contains:
    - the DataStore -   
    - the DataShelf
    - the DataBox
    and some methods to deal with the store co ntent
"""

class DS():
    ds = dict()
    def __init__(self, StoreYML):
        for StoreName in StoreYML["DataStores"]:
            print("Building Store for: ", StoreName)
            self.ds[StoreName] = dict()
            for ShelfTag, x in StoreYML["DataStores"][StoreName].items():
                self.ds[StoreName][ShelfTag] = dict()
                if ShelfTag == "Commons":       # initialize Commons
                    self.ds[StoreName]["Commons"]["header"] = "time"
                    self.ds[StoreName]["Commons"]["Active"] = False
                    self.ds[StoreName]["Commons"]["initTime"] = datetime.datetime.now()
                if ShelfTag != "Commons":       # Commons are not part of the csv-header  
                  if x["STORE_MODE"] != "NONE":
                    self.ds[StoreName]["Commons"]["header"] += "," + ShelfTag
                self.ds[StoreName][ShelfTag]["CURRENT_DATA"] = 0
                self.ds[StoreName][ShelfTag]["STORE_MODE_DATA"] = None
                for DataBox, Value in x.items():
                    self.ds[StoreName][ShelfTag][DataBox] = dict()
                    self.ds[StoreName][ShelfTag][DataBox] = Value
            self.ds[StoreName]["Commons"]["Service"] = Service(StoreName) # start store handling

class Service():
    MyName = ""
    def __init__(self, StoreName):
        self.MyName = StoreName
        threading.Thread(target=self._monitoring_thread, daemon=True).start()        
      
    def _monitoring_thread(self):
        logger.info("DataStare monitoring started")
        while True:
            try:
                DS.ds[self.MyName]["Commons"]["MERGE"]
                self.merge()
            except:
                pass
            if(DS.ds[self.MyName]["Commons"]["TIMEOUT"]):
                DS.ds[self.MyName]["Commons"]["TIMEOUT"] -= 1
                if(not DS.ds[self.MyName]["Commons"]["TIMEOUT"]):
                    DS.ds[self.MyName]["Commons"]["Active"] = False
                    logger.error("Message missed: " + self.MyName)
                    print("Message missed: ", self.MyName )
            time.sleep(1)

    def handle_DataSet(self, DataSet):
        timeStamp = str(int(time.time()))
        for key in DataSet.keys():
            try:
                self.handleData(DataSet[key], timeStamp)
            except Exception as err:
                logger.error("receiving invalid DataSet: " + key, " - ", type(err))
                print("receiving invalid DataSet: ", key, " - ", type(err))
        
    def handleData(self, DataSet, timeStamp):
        if DS.ds[self.MyName]["Commons"]["TIMEOUT"] == 0 and DS.ds[self.MyName]["Commons"]["RELOAD_TIMEOUT"] != 0:
            logger.info("Message send resume: " + self.MyName)
            print("Message send resume: " + self.MyName)
        DS.ds[self.MyName]["Commons"]["Active"] = True
        if (type(DS.ds[self.MyName]["Commons"]["RELOAD_TIMEOUT"]) == int):
            DS.ds[self.MyName]["Commons"]["TIMEOUT"] = DS.ds[self.MyName]["Commons"]["RELOAD_TIMEOUT"]
        else:
            DS.ds[self.MyName]["Commons"]["TIMEOUT"] = int(DS.ds[self.MyName][DS.ds[self.MyName]["Commons"]["RELOAD_TIMEOUT"]]["CURRENT_DATA"]) * 2
        csv_line = timeStamp
        update = False
        resstr = ""
        for StoreShelf in DS.ds[self.MyName]:
            if StoreShelf == "Commons":
                continue
            res= None
            if StoreShelf in DataSet:
                res = self.updateData(StoreShelf, DataSet.get(StoreShelf))
                if res:
                    update = True

            try:
                x = DS.ds[self.MyName][DataShelf]["DECIMALS"] 
            except:
                x = 8

            if (res != None):
                try:
                    resstr = str(round(res, x))
                except Exception as err:
                    resstr = str(res)
            else:
                resstr = ""

            if DS.ds[self.MyName]["Commons"]["FORMAT"] == "SINGLE_CSV":
                if res != None:
                    self.writeDataSet(StoreShelf, csv_line + "," + resstr)
                    return

            if DS.ds[self.MyName]["Commons"]["FORMAT"] == "MULTI_CSV":
                try:
                    DS.ds[self.MyName]["Commons"]["FILLED_UP"]
                    try:
                        fillerstr = str(round(DS.ds[self.MyName][StoreShelf]["STORE_MODE_DATA"], x))
                    except:
                        fillerstr = str(DS.ds[self.MyName][StoreShelf]["STORE_MODE_DATA"])
                except Exception as e:
                    fillerstr = resstr
                if(DS.ds[self.MyName][StoreShelf]["STORE_MODE"] != "NONE"):
                    csv_line = csv_line + "," + fillerstr

        if update:
            self.writeDataSet(StoreShelf, csv_line)

    def updateData(self, DataShelf, DataBoxValue):
        try:
            DS.ds[self.MyName][DataShelf]["CURRENT_DATA"] = DataBoxValue
        except Exception as err:
            logger.error(type(err).__name__ + " in: "  + self.MyName + " - " + DataShelf)
            return None

        try: # values can be omitted in the *.signals.yml
            DS.ds[self.MyName][DataShelf]["CURRENT_IN_RANGE"] = DS.ds[self.MyName][DataShelf]["CURRENT_DATA"] >= \
                                                        DS.ds[self.MyName][DataShelf]["MIN"] and \
                                                        DS.ds[self.MyName][DataShelf]["CURRENT_DATA"] <= \
                                                        DS.ds[self.MyName][DataShelf]["MAX"]
        except: pass                                                                
        if(DS.ds[self.MyName][DataShelf]["STORE_MODE"] == "NONE"):
            return None
        if(DS.ds[self.MyName][DataShelf]["STORE_MODE"] == "ALL"):
            DS.ds[self.MyName][DataShelf]["STORE_MODE_DATA"] = DataBoxValue
            self.processValue(DataShelf, DataBoxValue)
            return DataBoxValue
        if(DS.ds[self.MyName][DataShelf]["STORE_MODE"] == "CHANGE"):
            if(DS.ds[self.MyName][DataShelf]["STORE_MODE_DATA"] != DataBoxValue):
                DS.ds[self.MyName][DataShelf]["STORE_MODE_DATA"] = DataBoxValue
                self.processValue(DataShelf, DataBoxValue)
                return DataBoxValue
            return None
        if(DS.ds[self.MyName][DataShelf]["STORE_MODE"] == "COUNT"):
            if(DS.ds[self.MyName][DataShelf]["CNT"]):
                DS.ds[self.MyName][DataShelf]["CNT"] -= 1
                return None
            else:
                DS.ds[self.MyName][DataShelf]["CNT"] = DS.ds[self.MyName][DataShelf]["RELOAD_CNT"] - 1
                DS.ds[self.MyName][DataShelf]["STORE_MODE_DATA"] = DataBoxValue
                self.processValue(DataShelf, DataBoxValue)
                return DataBoxValue
        if(DS.ds[self.MyName][DataShelf]["STORE_MODE"] == "AVR"):
            if DS.ds[self.MyName][DataShelf]["CNT"]:
                DS.ds[self.MyName][DataShelf]["CNT"] -= 1
                DS.ds[self.MyName][DataShelf]["AVR_SUBTOTAL"] += DataBoxValue
                return None
            else:
                DS.ds[self.MyName][DataShelf]["CNT"] = DS.ds[self.MyName][DataShelf]["RELOAD_CNT"] - 1
                DS.ds[self.MyName][DataShelf]["STORE_MODE_DATA"] = (DS.ds[self.MyName][DataShelf]["AVR_SUBTOTAL"] + DataBoxValue) / \
                                                    DS.ds[self.MyName][DataShelf]["RELOAD_CNT"]
                DS.ds[self.MyName][DataShelf]["AVR_SUBTOTAL"] = 0
                self.processValue(DataShelf, DS.ds[self.MyName][DataShelf]["STORE_MODE_DATA"])
                return DS.ds[self.MyName][DataShelf]["STORE_MODE_DATA"]

    def processValue(self, DataShelf, value):
        try:
            DS.ds[self.MyName][DataShelf]["CURRENT_IN_RANGE"] = DS.ds[self.MyName][DataShelf]["STORE_MODE_DATA"] >= \
                                                      DS.ds[self.MyName][DataShelf]["MIN"] and \
                                                      DS.ds[self.MyName][DataShelf]["STORE_MODE_DATA"] <= \
                                                      DS.ds[self.MyName][DataShelf]["MAX"]
        except KeyError:
            pass

    def mergeOperation(self, data, str):
        data[self.MyName][str[1]] = DS.ds[str[2]][str[3]][str[4]]
        if str[0] == "and":
            data[self.MyName][str[1]] = True
            for i in range(2, len(str), 3):
                data[self.MyName][str[1]] = data[self.MyName][str[1]] and DS.ds[str[i]][str[i+1]][str[i+2]]
        if str[0] == "or":
            data[self.MyName][str[1]] = False
            for i in range(2, len(str), 3):
                data[self.MyName][str[1]] = data[self.MyName][str[1]] or DS.ds[str[i]][str[i+1]][str[i+2]]
        if str[0] == "add":
            data[self.MyName][str[1]] = 0
            for i in range(2, len(str), 3):
                data[self.MyName][str[1]] = data[self.MyName][str[1]] + DS.ds[str[i]][str[i+1]][str[i+2]]
        return data

    def merge(self):
        data = dict()
        data[self.MyName] = dict()
        try:
            DS.ds[self.MyName]["Commons"]["TIMEOUT"] = DS.ds[self.MyName]["Commons"]["RELOAD_TIMEOUT"]
            DS.ds[self.MyName]["Commons"]["Active"] = True
            mergeInfo = DS.ds[self.MyName]["Commons"]["MERGE"]
            for mergeStr in mergeInfo:
                if mergeStr[0] == "get":
                    data[self.MyName][mergeStr[1]] = DS.ds[mergeStr[2]][mergeStr[3]][mergeStr[4]]
                else: data = self.mergeOperation(data, mergeStr)
            self.handle_DataSet(data)
        except Exception as err:
            logging.error("call of merge for a non merging device.")
            print("call of merge for a non merging device. ", err)
            pass

    def writeDataSet(self, Shelf, line): 
        try:
            if DS.ds[self.MyName]["Commons"]["FORMAT"] == "SINGLE_CSV":
                FileName = "./data/" + self.MyName + "_" + Shelf + "_" + DS.ds[self.MyName][Shelf]["STORE_MODE"] + DS.ds[self.MyName]["Commons"]["initTime"].strftime("-%Y_%m_%d__%H-%M-%S") + ".txt"
                DS.ds[self.MyName]["Commons"]["header"] = "time," + Shelf
            if DS.ds[self.MyName]["Commons"]["FORMAT"] == "MULTI_CSV":
                FileName = "./data/" + self.MyName + DS.ds[self.MyName]["Commons"]["initTime"].strftime("-%Y_%m_%d__%H-%M-%S") + ".txt"
            try:
                with open(FileName, 'r') as DataFile: 
                    pass
            except:        
                line = DS.ds[self.MyName]["Commons"]["header"] + "\n" + line
            with open(FileName, 'a') as DataFile: 
                DataFile.write(line + "\n")
                DataFile.close()
        except:
            logging.error("could not write data.")
            print("could not write data.") 

def pick(Store, Shelf, DataBox):
    return DS.ds[Store][Shelf][DataBox]

def put(Store, *args):
    data = dict()
    data[Store] = dict()
    for arg in args:
        data[Store][arg[0]] = arg[1]
    handle_DataSet(data)

def handle_DataSet(DataSet):
    DS.ds[list(DataSet.keys())[0]]["Commons"]["Service"].handle_DataSet(DataSet)
  
def handle_CAN(StoreName, DataSet):
    DS.ds[StoreName]["Commons"]["Service"].handle_CAN(DataSet)
    