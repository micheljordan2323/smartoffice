from grove import grove_sound_sensor as snd
from grove import grove_piezo_vibration_sensor as pie
import time


#from grove.helper import SlotHelper
#sh = SlotHelper(SlotHelper.GPIO)
#pin = sh.argv2pin()


n=pie.GrovePiezoVibrationSensor(5)

def call():
    print("detect")

n.on_detect=call

while(True):
    
    time.sleep(1)


