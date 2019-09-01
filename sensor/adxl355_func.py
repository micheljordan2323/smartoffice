import spidev
import time
import numpy as np

import sys
sys.path.append("../")

import sensor.adxl_lib2 as adxl355


def measure(outputfilename,measuretime):
    ################################################################################
    # Some values for the recording                                                #
    #   measuretime unite is second
    ################################################################################

    # Filename for output
    outfilename = outputfilename
    # Measurement time in seconds
    mtime = measuretime
    # Data rate, only some values are possible. All others will crash
    # possible: 4000, 2000, 1000, 500, 250, 125, 62.5, 31.25, 15.625, 7.813, 3.906 

    #rate = 62.5
    rate = 1000


    ################################################################################
    # Initialize the SPI interface                                                 #
    ################################################################################
    spi = spidev.SpiDev()
    bus = 0
    device = 1
    spi.open(bus, device)
    spi.max_speed_hz = 5000000
    spi.mode = 0b00 #ADXL 355 has mode SPOL=0 SPHA=0, its bit code is 0b00

    ################################################################################
    # Initialize the ADXL355                                                       #
    ################################################################################
    acc = adxl355.ADXL355(spi.xfer2)
    acc.start()
    acc.setrange(adxl355.SET_RANGE_8G) # set range to 8g
    acc.setfilter(lpf = adxl355.ODR_TO_BIT[rate]) # set data rate


    ################################################################################
    # Record data                                                                  #
    ################################################################################
    datalist = []

    print("record start")

    msamples = mtime * rate
    mperiod = 1.0 / rate

    datalist = []
    acc.emptyfifo()
    t0 = time.time()

    while (len(datalist) < msamples):
        if acc.fifooverrange():
            print("The FIFO overrange bit was set. That means some data was lost.")
            print("Consider slower sampling. Or faster host computer.")
        if acc.hasnewdata():
            datalist += acc.get3Vfifo()
    #         datalist += [acc.getXRaw()]
    tc = time.time()
    # The get3Vfifo only returns raw data. That means three bytes per coordinate,
    # three coordinates per data point. Data needs to be converted first to <int>,
    # including, a twocomplement conversion to allow for negative values.
    # Afterwards, values are converted to <float> g values.

    # Convert the bytes to <int> (including twocomplement conversion)
    rawdatalist = acc.convertlisttoRaw(datalist)

    # Convert the <int> to <float> in g
    gdatalist = acc.convertRawtog(acc.convertlisttoRaw(datalist))

    # Add a column with a timestamp
    alldata = []
    #for i in range(len(gdatalist)):
    #for i in range(len(datalist)):
    #    alldata.append([0, i * mperiod] + gdatalist[i])
    #    alldata.append([0, i * mperiod] + datalist[i])


    # Save it as a csv file    
    #alldatanp = np.array(alldata)
    alldatanp = np.array(gdatalist)
    np.savetxt(outfilename, alldatanp, delimiter=",")
    print(alldatanp.shape)
    print("process time {0}".format(tc-t0))
    