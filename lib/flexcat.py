#!/usr/bin/env python

"""
flexcat - Establish and manage CAT control with FlexRadio 6000 series
"""

import socket, time, os, sys, shutil
from lib.utils import genutils
from lib.discovery import discoverRigs

FHOST = 'AUTO'
FPORT = 4992
UPORT = 4993
DSIZE = 4096
DTIMEOUT = 1.0

DISCOVERTIME = 180 # Seconds
CLASSID1 = 0x00001C2D
CLASSID2 = 0x534CFFFF
VERSION = '0.0.1'

class flexcat():
   def __init__(self, host=FHOST, port=FPORT):
      self.tsock = None
      self.tport = port
      self.usock = None
      self.uport = None
      self.constring=None
      self.handlestring=None
      self.nickname = None
      self.host = host
      self.discoverData = None

      if ( (host.upper() == 'AUTO') ):
         print ('Discovering flex radio...')
         self.tsock, self.constring, self.handlestring=self.discoverFlex()
      else:
         self.tsock, self.constring, self.handlestring=self.flexconnect(host, port)

   def __get_version__(self):
      return VERSION

   def flexconnect(self, host, port = FPORT, timeout = DTIMEOUT):
      print(f'Connecting to {host}:{port}')
      s = None
      #constring=None
      #handlestring=None
      try:
         self.tsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
         self.tsock.connect((host,port))
         self.tsock.settimeout(timeout)
         temp = self.flexread() #version/handle
         constatus = self.flexread() #connection status 'M' message
         vstring = temp.splitlines()
         self.constring=vstring[0] #version
         self.handlestring=vstring[1] #handle
         print(f'Rig connection status message  = {constatus}')
      except Exception as e:
         print (f'Connect error!\n {e.args}')
      return self.tsock, self.constring, self.handlestring

   """
   Create UDP connection
   """
   def udpconnect(self, host, port):
      try:
         sock = socket.socket(socket.AF_INET, # Internet
                               socket.SOCK_DGRAM) # UDP
         server_address=(host, port)
         sock.bind(server_address)
      except:
         print ('UDP Connect Error!')
         sock = None
      return sock

   def udpread(self, udpsock, psize=1024):
      data, address = udpsock.recvfrom(psize)
      return data, address

   def flexclose(self, sock):
      sock.close

   def flexread(self, maxsize=DSIZE, timeout=DTIMEOUT):
      self.tsock.settimeout(timeout)
      rdata = self.tRecv(maxsize, timeout)
      return rdata.decode('utf8')

   def flexsend(self, data, maxsize=DSIZE, timeout=DTIMEOUT):
      """
      Most data sent to a Flex radio results in at least one
      status message. This method will send the data, then
      read data back from the radio.
      
      #bydata=bytes(data, 'utf-8')
      #print('bydata= {}\n'.format(bydata))
      #self.tsock.send(bydata)
      """
      self.tSend(data.encode('utf-8')) # Convert string to bytes
      temp = self.flexread()
      return temp

   def isStatus(self, data):
      if (data):
          if (data[0] =='S'):
             return True
      return False

   def isMessage(self, data):
      if (data):
          if (data[0] =='M'):
             return True
      return False

   def isCmdResponse(self, data):
      #print(f'data={data}\ndata[0]={data[0]}')
      if (data):
          if (data[0] =='R'):
             return True
      return False
      
   """ 
   Parse messages that begin with M
   """
   def parseMessage(self, data):
      if (self.isMessage(data)):
         split_dat = data.split('|')
         return split_dat[0][1:], split_dat[1]
      else:
         return None, None

   """ 
   Parse messages that begin with S
   """
   def parseStatus(self, data):
      if (self.isStatus(data)):
         statD= dict()
         split_dat = data.split('|')
         status=split_dat[0][1:]
         split_stg = split_dat[1].split(' ')
         source = ''
         for s in split_stg:
            if '=' in s:
               sd=s.split('=')
               statD[sd[0]] = sd[1]
            else:
               if len(source)>0:
                  source += f' {s}'
               else:
                  source = s
         rstat = ['S', status, source, statD]
         return rstat
      else:
         return None

   """ 
   Parse messages that begin with R
   """
   def parseCmdResponse(self, data):
      if (self.isCmdResponse(data)):
         split_dat = data.split('|')
         return split_dat[0][1:], split_dat[1], split_dat[2]
      else:
         return None, None, None

   def monMessage(self):
      while True:
         try:
            retdata = self.flexread()
            if (self.isCmdResponse(retdata)):
               mn, me, m = self.parseCmdResponse(retdata)
               print('Response to command %s - Error status: %s'%(mn, me))
               print('Response Text:%s'%(m))
            elif (self.isStatus(retdata)):
               mn, m = self.parseStatus(retdata)
               print('Status from client: %s'%(mn))
               print('Status Text:%s'%(m))
            elif (self.isMessage(retdata)):
               mn, m = self.parseMessage(retdata)
               print('Message: %s'%(mn))
               print('Message Text:%s'%(m))
            else:
               print('Test: %s'%(retdata))
               print('%s'%(self.hexDump(retdata)))
         except socket.timeout:
            pass
         except KeyboardInterrupt:
            print("Operator exit!")
            exit()
   """
   Send byte data to the TCP socket specified
   in self.tsock
   """
   def tSend(self, sdata):
       self.tsock.send(sdata)         
   """
   Receive byte data from the TCP socket specified in
   self.tsock.
   
   Returns raw byte data. 
   """
   def tRecv(self, maxsize=DSIZE, timeout=DTIMEOUT):
      rdata = None
      self.tsock.settimeout(timeout)  
      rdata = self.tsock.recv(maxsize)
      return rdata

   def sendcmd(self, cmdstring):
        utils = genutils()
        #print(f' {cmdstring}')
        searching = True
        cresponse = self.flexsend(cmdstring)
        #print(f'sendcmd output:\n{cresponse}')
        lc=0
        while searching:
            #print(lc)
            try:
                if utils.IsMsgResponse(cresponse, cmdstring):
                    #print(f'Match: {cresponse}')
                    searching = False
                else:
                    cresponse=self.flexread()
            except:
                searching = False
                cresponse=None
                #print('sendcmd: timeout')
            lc+=1
        return cresponse

   def discoverFlex(self):
      hostname = "NO CONNECTION"
      s= None
      constring = None
      handlestring = None
      rigs = discoverRigs()
      if len(rigs.rigList) > 0:
         self.discoverData = rigs.rigList[0]
      self.host=self.discoverData['ip']
      self.tport = int(self.discoverData['port'])
      self.nickname = self.discoverData['nickname']
      print(f"Radio detected: {self.discoverData['nickname']} at {self.host}:{self.tport} - connecting...")
      self.tsock, \
      self.constring, \
      self.handlestring=self.flexconnect(self.host, self.tport)
 
      return self.tsock, self.constring, self.handlestring



"""
Unit test for flexcat class
"""
if __name__ == "__main__":
   flex = flexcat("auto")
#   print flex.discoverFlex()

