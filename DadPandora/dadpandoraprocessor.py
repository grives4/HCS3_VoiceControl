import os

import elementtree.ElementTree as ET

#from controllers import *

class pandoraprocessor(object):

   def send_info(self, information):
      file.open("/home/pi/.config/pianobar/ctl",'w')
      file.write(information + "\n")
      file.close()
      
   def get_info(self):
   
      fifo = open("/home/pi/.config/pianobar/output","r")

      while True:
         # Read parameters from input
         params = {}
         print fifo.readline()	

pandoraprocessor().get_info()