#!/usr/bin/env python

"""
A simple Flex Radio client to monitor and display radio status messages.
"""
import sys, socket, traceback
sys.path.insert(0, 'lib')
from flexcat import flexcat 
from utils import genutils


fhost = 'AUTO'
fport = 4992
VERSION = '0.0.1'

class flexmon():
   def __init__(self, host=fhost, port=fport):
      self.flexradio=flexcat()
      if (self.flexradio.tsock != None):
         self.mainApp()
      else:
         print(f'Error, unable to connect to radio {host}:{port}')

   def __get_version__(self):
      return VERSION

   def mainApp(self):
      print('Version string = %s'%(self.flexradio.constring))
      print('Handle string = %s'%(self.flexradio.handlestring))
      print('Waiting for data from radio...\n\n')
      x=1
      utils = genutils()
      while True:
         try:
             retdata = self.flexradio.flexread()
             if retdata:
                 print(f'raw data from rig:\n{retdata}')
                 tout = False
                 if (self.flexradio.isCmdResponse(retdata)):
                     mn, me, m = self.flexradio.parseCmdResponse(retdata)
                     print('Response to command %s - Error status: %s'%(mn, me))
                     print('Response Text:%s'%(m))
                 elif (self.flexradio.isStatus(retdata)):
                     s = self.flexradio.parseStatus(retdata)
                     print(f'Message type:{s[0]} Status: {s[1]}  Source: {s[2]}')
                     for tag in s[3].keys():
                        print(f'{tag}={s[3][tag]}')
                 elif (self.flexradio.isMessage(retdata)):
                     mn, m = self.flexradio.parseMessage(retdata)
                     print('Message: %s'%(mn))
                     print('Message Text:%s'%(m))
                 else:
                     print('Test %d: %s'%(x, retdata))
                     print('%s'%(utils.hexDump(retdata.encode('utf-8'))))
             x += 1
         
         
         except Exception as e:
             if (e.args[0] != 'timed out'):
                 print('Exception detected -- FMITA!')
                 print("-"*60)
                 traceback.print_exc(file=sys.stdout)
                 print("-"*60)
                 exit()
             else:
                 if tout==False:
                     print('waiting for data...')
                     tout = True
         """
         except socket.timeout:
            pass
         except KeyboardInterrupt:
            print("Exception!")
            exit()
         """

"""
Unit test for flexcat class
"""
if __name__ == "__main__":
   flex = flexmon(fhost, fport)

