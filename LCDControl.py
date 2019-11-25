import lcddriver
import threading
from time import *
import datetime
import time
import pywapi

class LCDControl(threading.Thread):
   def __init__(self,LCDQueue,LCDEvent):
      super(LCDControl, self).__init__()
      self.LCDQueue = LCDQueue
      self.LCDEvent = LCDEvent
      self.rowSize = [14,0]
      self.lcd = lcddriver.lcd()   
      self.lcd.lcd_display_string("System Running", 1) 
      self.lcd.lcd_display_string("v3.00", 2) 
   def run(self):
      backlight = True
      while 1 == 1:
         self.LCDEvent.wait()
         while not self.LCDQueue.empty():
            #Get stuff off the queue (i.e. flush it.)
            #If I just read each item, 5 seconds per...it may take a while to finish if there are a lot of commands!
            while not self.LCDQueue.empty():
                displayData = self.LCDQueue.get()
            #if displayData[0] == 'backlight':
            #   if backlight == True:
            #      self.lcd.lcd_backlight(False)
            #      backlight = False
            #   else:
            #      self.lcd.lcd_backlight(True)
            #      backlight = True
            if self.rowSize[0] > len(displayData[0]) or self.rowSize[1] > len(displayData[1]):
                self.lcd.lcd_clear()
            self.lcd.lcd_display_string(displayData[0], 1)
            self.lcd.lcd_display_string(displayData[1], 2)
            self.rowSize[0] = len(displayData[0])
            self.rowSize[1] = len(displayData[1])
            self.LCDQueue.task_done()
            self.LCDEvent.clear()
      
class LCDClock(threading.Thread):
#This puts in to the queue the time once a minute.
   def __init__(self,LCDQueue, LCDEvent):
      super(LCDClock, self).__init__()
      self.LCDQueue = LCDQueue
      self.LCDEvent = LCDEvent
   def run(self):
      i = 15
      weatherDisplay = ""
      while 1==1:     
         i += 1
         if i > 15:
            i = 0
            try:
               weather_com_result = pywapi.get_weather_from_weather_com('78728')
               temperature =  int(weather_com_result['current_conditions']['temperature'])
               temperature = (9 * temperature) / 5 + 32
               weatherDisplay = str(temperature) + "F, " + weather_com_result['current_conditions']['text']
            except:
               pass
         self.LCDQueue.put([datetime.datetime.now().strftime("%m/%d  %I:%M %p"), weatherDisplay])
         self.LCDEvent.set()
         time.sleep(60)
         