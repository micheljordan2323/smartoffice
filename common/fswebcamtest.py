import subprocess

def savepicture(folder,num):
    cmd="fswebcam "+folder+"{0}.jpg now".format(num)
    bolean=subprocess.call(cmd,shell=True)
    if bolean == 0:
        pass
    else:
        subprocess.call(cmd,shell=True)