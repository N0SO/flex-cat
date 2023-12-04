#!/usr/bin/env python
"""
GUI Display of input voltage and PA Temp
Uses the flexMeter class
"""
import socket
import time
import threading
import sys
sys.path.insert(0, 'lib')
from flexcat import flexcat
from lib.utils import genutils
from meter import voltMeter, tempMeter
from tkinter import *

fhost = 'AUTO'
fport = 4992
uport = 4993

class App(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.start()

    def callback(self):
        self.root.quit()

    def run(self):
        self.root = Tk()
        self.vdc = StringVar()
        self.vdc.set('VDCB = XX.XX  ')
        self.patemp = StringVar()
        self.patemp.set('TEMP = XXX.XX C')
        self.tod = StringVar()
        self.root.protocol("WM_DELETE_WINDOW", self.callback)
        self.root.title("NO RIG")

        self.labeltime = Label(self.root, textvariable=self.tod).pack()
        self.labelvdc = Label(self.root, textvariable=self.vdc).pack()
        self.labeltmp = Label(self.root, textvariable=self.patemp).pack()
        #self.label.pack()

        self.root.mainloop()

def onePass(app):
   data, addr = flex.udpread(flex.udpsock)
   print(f'Data from {addr[0]}:{addr[1]} -')
   print(utils.hexDump(data))
   M1.setmeterVal(data)
   #vdc = M1.setVoltsDC()
   M2.setmeterVal(data)
   if ( M1.vdcValid or M2.dataReady):
      s = time.strftime("%c")
      app.tod.set(s)
   if (M1.vdcValid):
      s = ('%s = %02.1f VDC'%(M1.name, M1.meterVDC))
      app.vdc.set(s)
      #print s

   if (M2.tempReady):
      #tempC = M2.metertoFloat(M2.getMeterval())
      s=('%s = %3.2f C'%(M2.name, M2.tempC))
      app.patemp.set(s)
      #print s
     
 
if __name__ == "__main__":
#   root = Tk()
#   T = Text(root, height=2, width=30)
#   T.pack()
   app = App()
   utils = genutils()
   flex = flexcat("auto")
   print('Version string = %s'%(flex.constring))
   print('Handle string = %s'%(flex.handlestring))
   if (flex.handlestring == None):
      print ("No radio connected.")
      exit()
   app.root.title(flex.nickname)

   #Setup meters
   meterList = flex.sendcmd('C17|meter list\n')   
   M1 = voltMeter('+13.8A', meterList)
   M2 = tempMeter('PATEMP', meterList)

   #Subscribe to PA voltage and temperature readings
   print(f'Subscribe to {M1.name}:')
   print(flex.sendcmd(f'C18|sub meter {M1.index}\n'))
   print(f'Subscribing to {M2.name}:')
   print(flex.sendcmd(f'C19|sub meter {M2.index}\n'))

   #Setting rig UDP port
   print(f'Setting rig UDP Port to {uport}')
   print(flex.sendcmd(f'C20|client udpport {uport}\n'))

   #Open port to UDP stream
   print (f'Opening UDP socket {uport}...')
   #sock1 = flex.udpconnect('', 4993)
   #Open port to UDP stream
   flex.udpsock = flex.udpconnect('', uport)

   
   while True:
      onePass(app)
 

