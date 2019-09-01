
from __future__ import print_function

import datetime as dt
import time
import os
from transitions import Machine

#original
import sys
sys.path.append("../")
sys.path.append("../grove/")
import common.sql_lib as sql_lib


from grove import grove_sound_sensor as snd #ok
from grove import grove_piezo_vibration_sensor as pie #ok
from grove import grove_light_sensor_v1_2 as lt   #ok
from grove import grove_rotary_angle_sensor as ang #ok
from grove import grove_sound_sensor as snd #ok
#from grove import grove_time_of_flight_distance as tof #ok
import grove_time_of_flight_distancemiya as tof #ok

#for TOF
#from grove.i2c import Bus
#from rpi_vl53l0x.vl53l0x import VL53L0X
#tof._adapter = Bus()
#GroveTofDistanceVL53L0X = tof.VL53L0X(bus = _adapter.bus)
tof.init()


#from grove.helper import SlotHelper
#sh = SlotHelper(SlotHelper.GPIO)
#pin = sh.argv2pin()


n=pie.GrovePiezoVibrationSensor(5)


#additional install
import pigpio
#import numpy as np
import configparser
#import pandas as pd



import common.sql_lib as sql_lib
import common.thingspeak as thingspeak
#import common.fswebcamtest as fswebcamtest

#import sensor.grove_d6t as d6t_lib
#import sensor.sht30_lib as sht30
#import sensor.omron_2smpd_lib as omron_2smpd_lib

import scratch
import numpy




print("Initilize")

configfile="./scratch.ini"
conf=configparser.ConfigParser()

if os.path.exists(configfile):
    conf.read(configfile)
else:
    conf.add_section("setting")
    conf.set("setting","D6T_type","8L")
#    conf.set("setting","dbfile","./hotel.db")
#    conf.set("setting","log","./log/")
#    conf.set("setting","camera","yes")
    conf.add_section("thingspeak")
    conf.set("thingspeak","APIKEY","VXI31K2ILAHWUOKS")
    conf.add_section("period")

    conf.set("period","total_period",str(3*60))#sec単位
    conf.set("period","sampling",str(10))#sec単位
#    conf.set("period","thing_sampling",str(30))#sec単位

    print("make config")
    with open(configfile, 'w') as configfile:
        conf.write(configfile)

TotalPeriod=int( conf.get("period","total_period"))
SamplingPeriod=float( conf.get("period","sampling"))
#ThingPeriod=float( conf.get("period","thing_sampling"))






### connect to scratch
#
print("conneting to scratch")
hostip=conf.get("setting","host")

print(hostip)

s=scratch.Scratch(host=hostip)

s.sensorupdate({"tof":0})
time.sleep(1)

#buf=s.receive()

s.sensorupdate({"light":0})
time.sleep(1)
#buf=s.receive()

s.sensorupdate({"cnt":0})
time.sleep(1)
buf=s.receive()
print(buf)

################
#
# local DBの設定
#

key = [("cnt","int"),("time","text"),("d0","real"),("d1","real"),("d2","real")]
#key={"cnt":"int","time":"text","temp":"real","humid":"real","th_avez":"real","th_std":"real","pressure":"real","rawdata":"text"}
print(conf.get("setting","dbfile"))
db=sql_lib.miyadb(conf.get("setting","dbfile"),key)

#dbの中身を削除する
db.clear()
db.init_table2()



#############
#
# クラウド、DataBaseの設定
#
#thingspeak
# temp,humid,thermo_ave,themo_std,pressure
#　つかうセンサの数だけ並べる
print("Initilize thingspeak")

fieldlist=["field1","field2","field3"]
thg=thingspeak.thingspeak(conf.get("thingspeak","APIKEY"))
thg.set_field(fieldlist)


#############
#
# Sensor
#
#    センサのオブジェクトを作成

print("Sensor initilize")

#OMRON のセンサ
#sht=sht30.SHT30()
#d6t = d6t_lib.GroveD6t("44L")
#psensor = omron_2smpd_lib.Grove2smpd02e()

#Groveのセンサ

### Piezo vibration
#piezo=pie.GrovePiezoVibrationSensor(5)
#Example
#def call():
#    print("detect")
#piezo.on_detect=call


### Light sensor
sensor = lt.GroveLightSensor(0) 
#sensor.light


### TOF
#vl53 = tof.GroveTofDistanceVL53L0X
#vl53.begin()

#Exapmle
#st = vl53.wait_ready()
#if not st:
#    continue
#print("Distance = {} mm".format(vl53.get_distance()))


### AngleSensor
#sensor = ang.GroveRotaryAngleSensor(0)
#Example
# sensor.value


### SoundSensor
#sensor = snd.GroveSoundSensor(0)
#Example
#sensor.sound
### 


#####################
#
#   　ステートマシンで実装



#状態の定義
states = ['init', 'wait', 'measure1','measure2', 'quit']

#遷移の定義
# trigger：遷移の引き金になるイベント、source：トリガーイベントを受ける状態、dest：トリガーイベントを受けた後の状態
# before：遷移前に実施されるコールバック、after：遷移後に実施されるコールバック
transitions = [
    { 'trigger': 'end_init',       'source': 'init',   'dest': 'wait'},

#    { 'trigger': 'trig1',  'source': 'wait',  'dest': 'measure1','before': 'checktime1'},
#    { 'trigger': 'end_measure',  'source': 'measure1',   'dest': 'wait','before': 'checktime1'},

    { 'trigger': 'trig2',  'source': 'wait',  'dest': 'measure2','before': 'checktime2'},
    { 'trigger': 'end_measure',  'source': 'measure2',   'dest': 'wait','before': 'checktime2'},

    { 'trigger': 'timeend',     'source': 'wait',     'dest': 'quit'}
]


#状態を管理したいオブジェクトの元となるクラス
# 遷移時やイベント発生時のアクションがある場合は、当クラスのmethodに記載する
class Matter(object):
    t0=0
    t1=0
    t2=0
    cnt=0
    buf0=0
    buf1=0
    buf2=0
    buf3=0
    buf4=0
    buf5=0

    def __init__(self):
        self.t1=time.time()
        self.t2=time.time()

    def checktime1(self):
        self.t1=time.time()
        print(self.state)
    def checktime2(self):
        self.t2=time.time()
        print(self.state)



pi = Matter()
machine = Machine(model=pi, states=states, transitions=transitions, initial='init', auto_transitions=False)

#####################
#
#   メインループ
print("Start loop")
print("total")
print(TotalPeriod)
print("sampling")
print(SamplingPeriod)



pi.t0=time.time()

while pi.state != "quit":
    if pi.state == "init":

        pi.end_init()
    elif pi.state=="wait":

        if time.time()-pi.t0 > TotalPeriod:
            pi.timeend()
        if time.time()-pi.t1 > SamplingPeriod:
            pass
#            pi.trig1()
#        if time.time()-pi.t2 > ThingPeriod:
#            pi.trig2()
#        temp,humid=sht.read()
#        press, temp = psensor.readData()
        pi.cnt=pi.cnt+1

        dis=tof.getdistance()
        print("Distance = {} mm".format(dis))
        pi.buf0=dis

        light=sensor.light
        pi.buf1=dis

        tm=dt.datetime.now()
        dat=[pi.cnt,tm,dis,light,0]
        db.append2(dat)





        s.sensorupdate({"tof":dis})
#        buf=s.receive()
#        print(buf)


        s.sensorupdate({"lit":light})
#        buf=s.receive()
#        print(buf)

        s.sensorupdate({"cnt":pi.cnt})
#        buf=s.receive()
#        print(buf)


#        s.sensorupdate({"cnt":pi.cnt})
#        buf=s.receive()
#        print(buf)

        time.sleep(1.0)
        buf=s.receive()
        print(buf)

#        if buf[0]=="broadcast":
#            print(buf)

        if buf["broadcast"]==["upload"]:
            dat=[pi.cnt,tm,dis,light,1]
            db.append2(dat)
            print("upload")
            pi.trig2()


    elif pi.state=="measure1":

        print("*** measure ***")
        temp,humid=sht.read()
        press, temp = psensor.readData()

#        s.sensorupdate({"temp":temp})
#        s.sensorupdate({"humid":humid})
#        s.sensorupdate({"press":press})


        pi.end_measure()


    elif pi.state=="measure2":

        print("*** measure2 thing ***")

                
        #thing speak
        datlist=[pi.buf0,pi.buf1]
        thg.sendall(datlist)

        #camera
        #if conf.get("setting","camera")=="yes":
        #    fswebcamtest.savepicture(conf.get("setting","log"),pi.cnt)

        pi.end_measure()









#while True:
#    try:
#        temp,humid=sht.read()
#        press, temp = psensor.readData()

#        a=numpy.random.randint(50)

#        s.sensorupdate({"temp":temp})
#        s.sensorupdate({"humid":humid})
#        s.sensorupdate({"press":press})

#        time.sleep(1)
#        buf=s.receive()
#        print(buf)
#        if buf[0]=="broadcast":
#            print(buf)
#        if buf["broadcast"]==["upload"]:
#            print("upload func")


#    except KeyboardInterrupt:
#        print("Disconnected")
#        break



