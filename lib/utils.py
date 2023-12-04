#!/usr/bin/env python

"""
A set of general utilities for strings and binary data
"""

VERSION = '0.0.1'

class genutils():
   def __init__(self):
      pass

   def vitaHeader(self, data):
      counter = self.unpack_word(data[0:2])
      psize = self.unpack_word(data[2:4])
      streamid = self.unpack_lword(data[4:8])
      classid = self.unpack_lword(data[8:12])
      classid2 = self.unpack_lword(data[12:16])
      return counter, psize, streamid, classid, classid2

   def hexDump(self, data):
      retbuf=''
      pdata=''
      hdata=''
      charcount = 0
      for c in data:
         #print(c)
         #hdata += chr(c)
         hdata += ('%02X' % c) + ' '
         if ( (c >= 0x20) and ( c <= 0x7e) ):
            pdata+=chr(c)
         else:
            pdata+='.'
         charcount += 1
         if (charcount == 16):
            retbuf += pdata + '   ' + hdata + '\n'
            pdata = ''
            hdata = ''
            charcount = 0
      if (charcount != 0):
         retbuf += pdata.ljust(16,' ') + '   ' + hdata + '\n'
      return retbuf

   def unpack_word(self, rawdata):
      word = None
      if len(rawdata) == 2:
         word = rawdata[0]<<8
         word += (rawdata[1])
      #print(f'{rawdata},{word}')
      return word   

   def unpack_lword(self, rawdata):
      lword = None
      if len(rawdata) == 4:
         lword = rawdata[0]<<24
         lword += rawdata[1]<<16
         lword += rawdata[2]<<8
         lword += rawdata[3]
      return lword 

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
      
   def splitcmdBytes(self, bydata):
        """
        Convert received byte array to string and 
        separate command/status from data. 
        """
        sdata = bydata.decode('utf-8')
        m=self.splitcmdStg(sdata)
        return m

   def splitcmdStg(self, sdata):
        """
        separate command/status from data string.
        returns m[cmdstatus. data]
        """
        m=sdata.split(' ',1)
        #print(m)
        return m

   def parseResponseHead(self, response):
        """
        Strip the T|nnnn|S data frpm a radio response.
        Return as a dict() object:
        ret['type'] = TYPE (C,R,S or M?)
        ret['num'] = number (echoed command number)
        ret['stat'] = number (represents status, should be 0)
        """
        rType=None
        rNum=None
        rStat=None
        rhead = response.split(' ')
        rels = rhead[0].split('|')
        rType=rels[0][0]
        rNum=rels[0][1:]
        rStat=rels[1]
        #Return as a dict() object.
        return {'type':rType,
                 'num':rNum,
                 'stat':rStat}

   def parseCommandHead(self, command):
        """
        Strip the T|nnnn data frpm a radio command.
        Return as a dict() object:
        ret['type'] = TYPE (C,R,S or M?)
        ret['num'] = number (command seq number - status msg
                             should echo this back)
        ret['stat'] = number (represents status, should be 0)
        """
        cType=None
        cNum=None
        rStat=None
        chead = command.split(' ')
        cels = chead[0].split('|')
        cType=cels[0][0]
        cNum=cels[0][1:]
        #Return as a dict() object.
        return {'type':cType,
                 'num':cNum}

   def IsMsgResponse(self, response, command):
       """
       Compare response seq number to command seq number.
       if match and response status = 0, return True       
       """
       cmd = self.parseCommandHead(command)
       res = self.parseResponseHead(response)
       #print(f'inputs: {res}  {cmd}')
       if (cmd['num'] == res['num']) and res['stat']=='0':
           return True
       else:
           return False
