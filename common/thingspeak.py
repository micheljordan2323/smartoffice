import urllib.request as ul
import json
import time
import os
#import psutil

class thingspeak:
    url="https://api.thingspeak.com/update?"
    apikey=""
    lastconnectiontime=0
    fieldlist=[]
    def __init__(self,apikey):
        self.apikey=apikey
    def set_field(self,fieldnames):
        self.fieldlist=[]
        self.fieldlist=[nn for nn in fieldnames]
    
    def send(self,fieldid,value):
        if self.lastconnectiontime - time.time() < 15 and self.lastconnectiontime - time.time() >0:
            return None
        url2=self.url+"api_key="+self.apikey+"&"+fieldname+"="+str(value)
        f=ul.urlopen(url2)
        if f.code==200:
            lastconnectiontime=time.time()
            
    def sendall(self,valuelist):
        if self.lastconnectiontime - time.time() < 15 and self.lastconnectiontime - time.time() >0:
            print("too fast {0}".format(self.lastconnectiontime - time.time()))
            return None
        if len(self.fieldlist)==0:
            print("set fieldlist")
            return None
        if len(self.fieldlist) != len(valuelist):
            print("length wrong")
            return None
        
        baseurl=self.url+"api_key="+self.apikey+"&"
        for field,val in zip(self.fieldlist,valuelist):
            addurl="&"+field+"="+str(val)
            baseurl=baseurl+addurl
        try:
            f=ul.urlopen(baseurl)
            if f.code==200:
                lastconnectiontime=time.time()
                print("OK")
            else:
                print(baseurl)
        except:
            print("thingspeak error")
            