import grove_d6t as d6t44
import time
d6t = d6t44.GroveD6t(ty="8L")
#d6t = d6t44.GroveD6t()


for i in range(50):
    #d6t.reopen()
    tpn0, tptat = d6t.readData2()
    #d6t.close()
    time.sleep(0.5)

    print(tpn0)

