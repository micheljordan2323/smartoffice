# coding: utf-8
# Driver for D6T.
# Please execute the following command before use "pigpio"
# $ sudo pigpiod

import time
import pigpio
import numpy as np
#import matplotlib.pyplot as plt 

D6T={"44L":4*4,"8L":1*8,"32L":32*32}
D6T={"44L":{"SOSI":4*4,"BYTE":35},"8L":{"SOSI":1*8,"BYTE":19},"32L":{"SOSI":32*32,"BYTE":2051}}

class GroveD6t:
    I2C_ADDR = 0x0a
    pi = pigpio.pi()
    handle = 0
    d6type=None
    def reopen(self):
        try:
            print(self.I2C_ADDR)
            self.handle = self.pi.i2c_open(1, self.I2C_ADDR)
        except AttributeError:
            print('If you have not executed the "sudo pigpiod" command, please execute it.')
            raise
        

    def __init__(self,ty="44L"):
        self.d6type=ty
        self.I2C_ADDR = 0x0A

#        try:
#            self.handle = self.pi.i2c_open(1, 0x0a)
#        except AttributeError:
#            print('If you have not executed the "sudo pigpiod" command, please execute it.')
#            raise


    def readData2(self):
        try:
            self.handle = self.pi.i2c_open(1, 0x0a)
        except AttributeError:
            print('If you have not executed the "sudo pigpiod" command, please execute it.')
            raise

        data=None
        try:
            if self.d6type=="32L":
                self.pi.i2c_write_device(self.handle, [0x4D])
            else:
                self.pi.i2c_write_device(self.handle, [0x4c])

            data = self.pi.i2c_read_device(self.handle, D6T[self.d6type]["BYTE"])
        except pigpio.error:
            print('Failed to read data.')
            return None,None
        
        tp = []
        tptat = 0




        #try:

        
        print("loop")

        for ii in np.arange(0,D6T[self.d6type]["SOSI"]+1):
            t=(data[1][ii*2+1]*256+data[1][ii*2])/10
            tp.append(t)
        tptat=tp[0]
        tp=tp[1:]

#        except IndexError:
#            print('got an incorrect index.')
#            print(data)
#            return None,None

        self.pi.i2c_close(self.handle)
        return tp, tptat




    def close(self):
        self.pi.i2c_close(self.handle)


