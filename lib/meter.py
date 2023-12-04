#!/usr/bin/env python

from utils import genutils

"""
A simple Flex Radio Meter library.
Needs documentation.
"""

VERSION = '1.0.0'

class flexMeter():
   def __init__(self, namestring=None, meterstring=None):
      self.index=0
      self.src=''
      self.num=0
      self.name=''
      self.low=0.0
      self.hi=0.0
      self.desc=''
      self.unit=''
      self.fps=0
      self.meterVal = 0
      self.dataReady = False
      if ( (meterstring != None) and (namestring != None) ):
         self.getMeterDetails(namestring, meterstring)

   def __get_version__(self):
      return VERSION

   def getMeterval(self):
      self.dataReady=False
      return self.meterVal
          
   def parseMeterEntry(self, entry):
      temp=entry.split('.',1)
      temp=temp[1].split('=')
      #print temp
      if (temp[0]=='src'):
         self.src = temp[1]
      if (temp[0]=='num'):
         self.num = int(temp[1])
      if (temp[0]=='nam'):
         self.name = temp[1]
      if (temp[0]=='low'):
         self.low = float(temp[1])
      if (temp[0]=='hi'):
         self.hi = float(temp[1])
      if (temp[0]=='desc'):
         self.desc = temp[1]
      if (temp[0]=='unit'):
         self.unit = temp[1]
      if (temp[0]=='fps'):
         self.fps = int(temp[1])
         
   def getMeterDetails(self,namestring, meterstring):
      #split meterstring into a list of entries
      meterlist=meterstring.split('#')
      #Find the name we are looking for and get its index number
      for entry in meterlist:
         #print entry
         if (namestring in entry):
            temp = entry.split('.')
            self.index = int(temp[0])
            break
      # Parse out the entries starting with self.index
      numstg = temp[0] + '.'
      for entry in meterlist:
         if (numstg in entry):
            self.parseMeterEntry(entry)

   def parseMeters(self, data):
      utils=genutils()
      i=0
      #print('data: {}\nFirstWord: {}\n'.format(data, data[0:2]))
      counter = utils.unpack_word(data[0:2])
      psize = utils.unpack_word(data[2:4])
      streamid = utils.unpack_lword(data[4:8])
      classid = utils.unpack_lword(data[8:12])
      classid2 = utils.unpack_lword(data[12:16])
      meterlist = []
      di = 16
      for i in range(0, psize-4):
         meterid = utils.unpack_word(data[di:di+2])
         di += 2
         meterval = utils.unpack_word(data[di:di+2])
         meter = [meterid, meterval]
         meterlist.append(meter)
         di +=2
         if (meterid==self.index):
            self.meterVal = meterval
            self.dataReady = True
      return meterlist
      
class voltMeter(flexMeter):

   def __init__(self, namestring=None, meterstring=None):
      flexMeter.__init__(self, namestring, meterstring)
      self.meterVDC = 0.0
      self.vdcValid = False

   def calcFrac(self, bfrac):
      frac = 0.0
      if (bfrac & 0x80 != 0):
         frac += 1.0/2.0
      if (bfrac & 0x40 != 0):
         frac += 1.0/4.0
      if (bfrac & 0x20 != 0):
         frac += 1.0/8.0
      if (bfrac & 0x10 != 0):
         frac += 1.0/16.0
      if ((bfrac & 0x08) != 0):
         frac += 1.0/32.0
      if (bfrac & 0x04 != 0):
         frac += 1.0/64.0
      if (bfrac & 0x02 != 0):
         frac += 1.0/128.0
      if (bfrac & 0x01 != 0):
         frac += 1.0/256.0
      #print frac
      return frac

   def metertoFloat(self, meterval):
      floatval = float(meterval)/256.0
      """
      upper = (meterval & 0xff00)>>8
      lower = meterval & 0x00ff
      floatval = self.calcFrac(lower) + upper
      """
      return floatval

   def setVoltsDC(self):
      if (self.dataReady):
         self.meterVDC = self.metertoFloat(self.meterVal)
         self.vdcValid = True
      return self.meterVDC 

   def getVoltsDC(self):
      self.vdcValid=False
      return self.meterVDC  

   def setmeterVal(self, meterdata):
       meterpacket = self.parseMeters(meterdata)
       for m in meterpacket:
           if m[0] == self.index:
               self.meterVal = m[1]
               self.dataReady=True
               self.setVoltsDC()
       return self.meterVal

class tempMeter(flexMeter):
   def __init__(self, namestring=None, meterstring=None):
      flexMeter.__init__(self, namestring, meterstring)
      self.tempC = 0.0
      self.tempReady = False

   def calcFrac(self, bfrac):
      frac = 0.0
      if (bfrac & 0x200 != 0):
         frac += 1.0/2.0
      if (bfrac & 0x100 != 0):
         frac += 1.0/4.0
      if (bfrac & 0x80 != 0):
         frac += 1.0/8.0
      if (bfrac & 0x40 != 0):
         frac += 1.0/16.0
      if ((bfrac & 0x20) != 0):
         frac += 1.0/32.0
      if (bfrac & 0x10 != 0):
         frac += 1.0/64.0
      if (bfrac & 0x08 != 0):
         frac += 1.0/128.0
      if (bfrac & 0x04 != 0):
         frac += 1.0/256.0
      if (bfrac & 0x02 != 0):
         frac += 1.0/512.0
      if (bfrac & 0x01 != 0):
         frac += 1.0/1024.0
      #print frac
      return frac

   def metertoFloat(self, meterval):
      floatval = float(meterval)/64.0
#      upper = (meterval & 0xff80)>>7
#      lower = meterval & 0x0003
#      floatval = self.calcFrac(lower) + upper
      return floatval

   def setmeterVal(self, meterdata):
       meterpacket = self.parseMeters(meterdata)
       for m in meterpacket:
           if m[0] == self.index:
               self.meterVal = m[1]
               self.dataReady=True
               self.setTempC()
       return self.tempC

   def setTempC(self):
      if (self.dataReady):
         self.tempC = self.metertoFloat(self.meterVal)
         self.tempReady = True
      return self.tempC 



if __name__ == "__main__":
   M1 = voltMeter()
   M1.index = 4
   print (vars(M1))
   print(M1.meterVal,M1.meterVDC)
   ml=b'8Y\x00\t\x00\x00\x07\x00\x00\x00\x1c-SL\x80\x02ej\x1b\x0b\x00\x00\x00\x00\x00\x00\x00\x00\x00\x04\r\x9d\x00\n\x06\xcf'
   M1.setmeterVal(ml)
   print (vars(M1))
   """
   M1.dataReady = True
   print ('TEST 1:')
   print (M1.vdcValid)
   vdc=M1.setVoltsDC()
   print (M1.meterVDC, M1.vdcValid)
   print ('TEST 2:')
   print (M1.meterVDC, M1.vdcValid)
   print (M1.name)
   """
   M2 = tempMeter()
   M2.index = 10
   M2.setmeterVal(ml)
   print(vars(M2))
