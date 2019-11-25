import re
import serial
import time
import urllib
import urllib2
import elementtree.ElementTree as ET
import socket
from time import gmtime, strftime
import json
import sys
import os
import subprocess
from pandora import *


class controllers(object):
      
   def write_to_serial_port(self, data, location='1'):
      try:
         sp = serial.Serial(self.config('serial', location,'address'),self.config('serial', location,'baud'), timeout=0)
         sp.flush()
         sp.write(data + '\r')
         temp = sp.read(9999)
         i = 1
         
         while  re.match(r'^\*AH66(.+)\r',temp) == None and i < 10: 
            time.sleep(.05)
            temp += sp.read(9999)
            i += 1
         sp.close()
         temp = temp.split('\r')
         for i in range(0, len(temp)):
            if temp[i].find('MDF') == -1 and temp[i].find('SIGNAL') == -1 and temp[i].find('ACK') == -1 and temp[i].find('66') > 0:
               response = temp[i].replace('*AH66,','')
               #print response
               return response
         return ""
      except:
         print "Error writing to serial port."
         return ""
      
   def write_to_ir(self, data, location):
      try:
         s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
         s.connect((self.config('ir', location, 'address'),4998))
         s.sendall(data + '\r')
         temp = s.recv(24)
         s.close()
      except:
         print "Issue occurred writing to ir."
      
   def write_to_computer(self, data, location='1'):
         try:
            if data == '':
               data = '{ENTER}'
            params = urllib.urlencode({'keypresses': data})
            #print "-" + data + "-"
            keyrequest = urllib2.Request(self.config('keypress', location,'address'), params)
            response = urllib2.urlopen(keyrequest,timeout=2)
            tempData = response.read()
            response.close()   
         except:
            print "Issue occurred sending key presses"
            

         
         #----------------
         # Put the below in the run definition in the pandora thread
         #----------------
   def change_pandora_station (self, data, location='1'):
           print "Changing pandora station - controllers.py"
           print data                
             
   def config(self,setting, location, info):
         XMLtree = ET.parse("Configuration/config.xml")
         doc = XMLtree.getroot()
         config = []
         for elem in doc.findall('config'): 
            if elem.get('name') == setting:        
               for item in elem.findall('item'):
                  if item.get('location') == location:
                    return item.get(info)
         return
        
