
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

#additional install
import pigpio
#import numpy as np
import configparser
#import pandas as pd



import common.sql_lib as sql_lib
import common.thingspeak as thingspeak
#import common.fswebcamtest as fswebcamtest

import scratch
import numpy


################
#
# センサ用のライブラリをインポートしておく
#

#omron 評価ボード用
#import sensor.grove_d6t as d6t_lib
import sensor.sht30_lib as sht30
import sensor.omron_2smpd_lib as omron_2smpd_lib



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

#tof.init()


#from grove.helper import SlotHelper
#sh = SlotHelper(SlotHelper.GPIO)
#pin = sh.argv2pin()


#n=pie.GrovePiezoVibrationSensor(5)



################
#
# 設定ファイルの読み込み
#




print("Initilize")

configfile="./scratch.ini"
conf=configparser.ConfigParser()

if os.path.exists(configfile):
    conf.read(configfile)
else:
    print("No ini")
    sys.exit(1)
    with open(configfile, 'w') as configfile:
        conf.write(configfile)

#ThingPeriod=float( conf.get("period","thing_sampling"))






### connect to scratch
#
print("conneting to scratch")
hostip=conf.get("setting","host")

print(hostip)

s=scratch.Scratch(host=hostip)


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
sht=sht30.SHT30()
#d6t = d6t_lib.GroveD6t("44L")
psensor = omron_2smpd_lib.Grove2smpd02e()

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
        self.cnt=0

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



pi.t0=time.time()


while(True):
    buf=s.receive()
    print(buf)

    if buf["broadcast"]==["get"]:
        print("get")
#        dis=tof.getdistance()
#        light=sensor.light
        temp,humid=sht.read()
        press, temp2 = psensor.readData()



        pi.buf0=temp
        pi.buf1=humid
        pi.buf2=press

        pi.cnt=pi.cnt+1
        tm=dt.datetime.now()

        #localDB用の出力
        #dat=[pi.cnt,tm,dis,light,0]
        dat=[pi.cnt,tm,temp,humid,press]

        db.append2(dat)
        s.sensorupdate({"temp":temp})
        s.sensorupdate({"humid":humid})
        s.sensorupdate({"press":press})
        s.sensorupdate({"cnt":pi.cnt})

    if buf["broadcast"]==["upload"]:
        print("-----------upload-------------------")
        datlist=[pi.buf0,pi.buf1,pi.buf2]
        thg.sendall(datlist)









