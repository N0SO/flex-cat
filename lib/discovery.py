#!/usr/bin/env python

"""
discoverRigs - A class to implement Flex Radio Discovery Protocol
"""

import socket
from lib.utils import genutils

FHOST = 'AUTO'
FPORT = 4992
UPORT = 4993
DSIZE = 4096
DTIMEOUT = 1.0
MAXCOUNT = 3

DISCOVERTIME = 180 # Seconds

class discoverRigs():
    def __init__(self, discover=True, 
                       port=FPORT, 
                       timeout=DTIMEOUT, 
                       dsize=DSIZE):
        self.port=port
        self.timeout=DTIMEOUT
        self.dsize=DSIZE
        self.rigList=[]
        if discover:
            self.Discover()

    def getData(self, s):
        m=None
        try:
            m=s.recvfrom(1024)
        except Exception as e:
            if (e.args[0] != 'timed out'):
                print('Radio Discover Read failed!')
                print("-"*60)
                traceback.print_exc(file=sys.stdout)
                print("-"*60)
            
        return m

    def Discover(self):
        rigList = []    
        #Open a UDP
        s=socket.socket( socket.AF_INET, socket.SOCK_DGRAM)
        s.bind(('',4992))
        s.settimeout(DISCOVERTIME)
        
        #Wait for discovery packet from the rig
        counter = 0
        while counter < MAXCOUNT:
            radData = self.getData(s)
            if radData:
                radEntry = self.parsePacket(radData)
                if self.IsRadio(radEntry):
                    self.rigList.append(radEntry)
                    counter = 0
                else:
                    radEntry = None
            counter += 1
        return self.rigList

    def IsRadio(self, packet):
        notDupe = False
        if packet:
            if 'vitahead' in packet.keys() and \
                           'ip' in packet.keys():
                notDupe = True
                if len(self.rigList)>0:
                    for rig in self.rigList:
                        if packet['ip'] == rig['ip']:
                            notDupe = False #duplicate
        
        return notDupe
        
    def parsePacket(self, m):
        """
        *** Where did I get this information? VITA docs cost $$$ ***
        The first 28 bytes of m[0] are binary hex data (VITA header?).
        Get the 28 bytes m[0] hex data in t0. Radio version / ID?
        Get the  other descriptive strings in t1. Both are byte arrays.
        Keep t0 in byte array format. t1 can be a string
        """
        dpacket = None
        t0=m[0][0:28]
        t1=m[0][28:].decode('utf-8')

        """
        Now complete the 'split' of m[0]
        Put Discovery data in a dict() object dpacket.
        t0 binary data will be in dpacket['vitahead'].
        *** is this a VITA header? Need more research ***
        t1 data is in the format tag_name=tag_value. Split it on the = 
        and create dpacket['tag_name']=tag_value dictionary elements.
        """
        dpacket = dict()
        dpacket['vitahead']=t0
        for t in  t1.split(' '):
             if('=' in t):
                 pdata = t.split('=')
                 #print(pdata)
                 dpacket[pdata[0]]=pdata[1]
             
        return dpacket        
        
"""
Unit test for flexcat class.
Listen and report which radios are seen on the lan
"""
if __name__ == "__main__":
   flex = discoverRigs()
   if len(flex.rigList) > 0:
       print(f'rigs found = {len(flex.rigList)}')
       for rig in flex.rigList:
           print(f"{rig['nickname']} {rig['ip']}:{rig['port']}")
