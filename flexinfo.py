#!/usr/bin/env python
"""
Uses the Flex Radio Discovery protocol to find your
radio on your lan, connect, then request and display
the radio info list from the radio.

If you have more than one radio and they are all powered, 
it will connect to the first one it sees.
"""
import sys
sys.path.insert(0, 'lib')
from lib import flexcat 
import socket

fhost = 'AUTO'
fport = 4992
if __name__ == "__main__":
   flex = flexcat.flexcat(fhost, fport)
   print(f'Version string = {flex.constring}')
   print(f'Handle string = {flex.handlestring}')

   print(f"\nRadio {flex.discoverData['nickname']} discovery data:")
   for tag in flex.discoverData.keys():
      print(f"{tag}: {flex.discoverData[tag]}")

   cmdstring = 'C1234|info\n'
   response = flex.sendcmd(cmdstring)
   iresponses=response.split(',')
   print(f'\n\nResponse to command {cmdstring[0:len(cmdstring)-1]}:')
   for s in iresponses:
      print (f'{s}')
