#!/usr/bin/env python
"""
Request meter list from radio
Uses the flexMeter classes
"""
import sys, socket, time
sys.path.insert(0, 'lib')
from lib.flexcat import flexcat
from lib.meter import voltMeter, tempMeter
from lib.utils import genutils

#fhost = '192.168.1.83'
#fport = 4992
udp_port = 4993

class mainApp():
   def __init__(self):
      if __name__ == "__main__":
         self.appMain()

   def processCmd(self, cmd, flex):
      response = flex.sendcmd(cmd)
      print('command: %s\nresponse: %s'%(cmd, response))

   def enableSubs(self, flex):
      print(flex.sendcmd('C18|sub meter 4\n'))
      print(flex.sendcmd('C21|sub meter 10\n'))
      """
      print(flex.sendcmd('C18|sub meter 7\n'))
      print(flex.sendcmd('C19|sub meter 8\n'))
      print(flex.sendcmd('C20|sub meter 9\n'))
      print(flex.sendcmd('C22|sub meter 11\n'))
      print(flex.sendcmd('C23|sub meter 12\n'))
      """
   def onePass(self, flex, M1, M2):
      utils=genutils()

      data, addr = flex.udpread(self.udpsock)
      hexdata = utils.hexDump(data)
      M1.setmeterVal(data)
      M2.setmeterVal(data)
      print(f'M1 - {M1.name}\nRaw Data: {M1.index},{M1.meterVal}\nM1 DC Volts:{M1.meterVDC}\n')
      print(f'M2 - {M2.name}\nRaw Data: {M2.index},{M2.meterVal}\nM2 temperature:{M2.tempC}\n')
      #print(f'Voltmeter M1:\n{vars(M1)}\n\nPA Temperature M2:\n{vars(M2)}\n')
      #print(f'Hexdump of UDP Data from {addr[0]}:{addr[1]}:\n{hexdata}\n\n')

   def appMain(self):
      flex = flexcat()
      print('Version string = %s'%(flex.constring))
      print('Handle string = %s'%(flex.handlestring))
      meterNames = flex.sendcmd('C1|meter list\n')
      M1 = voltMeter('+13.8A', meterNames)
      M2 = tempMeter('PATEMP', meterNames)
      #print(self.meterNames)

      # Subscribe to meters
      self.enableSubs(flex)
      # Enable UDP stream
      cmd = (f'C24|client udpport {udp_port}\n')
      print(flex.sendcmd(cmd))
      

      #Open port to UDP stream
      self.udpsock = flex.udpconnect('', udp_port)
      
      while True:
          print("DateTime " + time.strftime("%c"))
          self.onePass(flex, M1, M2)
          #time.sleep(5)



if __name__ == "__main__":
   app = mainApp()

