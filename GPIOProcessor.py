import RPi.GPIO as GPIO
import smbus
import threading
from time import *
import datetime
import time
import os

class GPIOProcessor(threading.Thread):

    def __init__(self,LCDQueue, LCDEvent):
        super(GPIOProcessor, self).__init__()
        self.LCDQueue = LCDQueue
        self.LCDEvent = LCDEvent
        self.pressTimer = 0
        
        #Location of the i2c DIO chip
        self.bus = smbus.SMBus(1)
        self.address = 0x24

    def run(self):
        #Configure the inputs on the i2c DIO chip.

        #Set direction of port a and b to read.
        self.bus.write_byte_data(self.address,0x00,0xFF)
        self.bus.write_byte_data(self.address,0x01,0xFF)

        #Set pins to be monitored by interrupts
        self.bus.write_byte_data(self.address,0x04,0xFF)
        self.bus.write_byte_data(self.address,0x05,0xFF)

        #Set the default value for the GPIO for the interrupt to compare against
        self.bus.write_byte_data(self.address,0x06,0x00)
        self.bus.write_byte_data(self.address,0x07,0x00)

        #setup interrupts to trigger on either port change
        self.bus.write_byte_data(self.address,0x0A,0x42)
        self.bus.write_byte_data(self.address,0x0B,0x42)
    
        #Flush the data on the lines so its back to 0.
        flushData = "{0:016b}".format(self.bus.read_byte_data(self.address,0x12))
        flushData = "{0:016b}".format(self.bus.read_byte_data(self.address,0x13))
    
        #Configure the interrupts on the GPIO on the pi.
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(17,GPIO.IN,pull_up_down=GPIO.PUD_DOWN)    
        GPIO.add_event_detect(17, GPIO.RISING, callback=self.buttonEventHandler, bouncetime=200)
        
        #print "GPIO Initialized"  
        secondsCount = 0  
        while 1==1:
           sleep(1)

    def buttonEventHandler(self, pin):  
        flushData = "{0:016b}".format(self.bus.read_byte_data(self.address,0x0E))
        flushData = "{0:016b}".format(self.bus.read_byte_data(self.address,0x0F))
        flushData = "{0:016b}".format(self.bus.read_byte_data(self.address,0x12))
        flushData = "{0:016b}".format(self.bus.read_byte_data(self.address,0x13))
        self.pressTimer = 0
        flag = False
        while (flag == False):
           while (self.bus.read_byte_data(self.address,0x13)==1):
               self.pressTimer +=1
               #if self.pressTimer == 1:
               #   self.LCDQueue.put(["Dim / Brighten?",""])
               if self.pressTimer == 1:
                  self.LCDQueue.put(["Reboot?",""])
               if self.pressTimer == 2:
                  self.LCDQueue.put(["Shutdown?",""])
               if self.pressTimer == 3:
                  self.LCDQueue.put(["Do nothing?",""])
                  self.pressTimer = 0
               self.LCDEvent.set()
               sleep(1)
           timer = 0
           while (self.bus.read_byte_data(self.address,0x13)==0 and flag == False):          
               sleep(0.25)
               timer += 0.25
               if timer > 5:
                  #if self.pressTimer == 1:
                  #   self.LCDQueue.put(["backlight",""])
                  if self.pressTimer == 1:
                     self.LCDQueue.put(["Rebooting",""])
                     os.system("sudo shutdown -r now")
                  if self.pressTimer == 2:
                     self.LCDQueue.put(["",""])
                     os.system("sudo shutdown -h now")
                  if self.pressTimer == 4 or self.pressTimer == 0:
                     self.LCDQueue.put([datetime.datetime.now().strftime("%b %d, %Y"), datetime.datetime.now().strftime("%I:%M %p")])
                  self.LCDEvent.set()
                  flag = True
               

        