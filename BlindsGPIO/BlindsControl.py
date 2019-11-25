#!/usr/bin/python

from Adafruit_PWM_Servo_Driver import PWM
import time
import cgi
import BaseHTTPServer
import SimpleHTTPServer
import elementtree.ElementTree as ET
import math
import lcddriver

class MyHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
   
   def __init__(self, *args, **kwargs):
      SimpleHTTPServer.SimpleHTTPRequestHandler.__init__(self, *args, **kwargs)
      lcd = lcddriver.lcd()
         
   def setServoPulse(channel, pulse):
      pulseLength = 1000000                   # 1,000,000 us per second
      pulseLength /= 60                       # 60 Hz
      print "%d us per period" % pulseLength
      pulseLength /= 4096                     # 12 bits of resolution
      print "%d us per bit" % pulseLength
      pulse *= 1000
      pulse /= pulseLength
      pwm.setPWM(channel, 0, pulse)

   def get_blind_data(self):
      XMLtree = ET.parse("Blinds.xml")
      doc = XMLtree.getroot()
      blinds = []
      for elem in doc.findall('blind'):
         blinds.append({'name' : elem.get('name'), 'room': elem.get('room'), 'PWM' : elem.get('PWM'), 'OpenLocation' : elem.get('OpenLocation'), 'CloseLocation' : elem.get('CloseLocation')  })
      return blinds
   
   def do_POST(self):
      # Initialise the PWM device (I2C address of 0x40)
      pwm = PWM(0x40, debug=True)
      pwm.setPWMFreq(60) 
      if self.path == '/command':
         form = cgi.FieldStorage(fp=self.rfile, headers=self.headers, environ={'REQUEST_METHOD':'POST'})
         room = form['room'].value
         name = form['name'].value
         lcd.lcd_display_string("Open Blinds", 1)
         location = float(form['location'].value)  #% Open
         print time.strftime("[%Y/%m/%d %H:%M:%S]  ", time.localtime()) + "Web Command Received."
         blinds = self.get_blind_data()
         for blind in blinds:
            if (blind.get('room') == room or blind.get('name') == name):
               servoOpenLocation = float(blind.get('OpenLocation'))
               servoCloseLocation = float(blind.get('CloseLocation'))
               PWMLocation = int(blind.get('PWM'))
               location = 100 - location
               servoLocation = int(location * math.fabs(servoOpenLocation - servoCloseLocation) + servoOpenLocation)
               pwm.setPWM(PWMLocation, 0, servoLocation)
               time.sleep(0.50)
               pwm.setPWM(PWMLocation, 0, 000)
      
         #--- Added...may not be needed.
         self.send_response(200)
         self.send_header('Content-type','text-html')
         self.end_headers()
         self.wfile.write('Command Received and Processed')
         #---
         return
         
      return self.do_GET()

# Fix bug where BaseHTTPServer is really slow.
# See: https://gist.github.com/santa4nt/374606
def _bare_address_string(self):
   host, port = self.client_address[:2]
   return str(host)
 
BaseHTTPServer.BaseHTTPRequestHandler.address_string = _bare_address_string
      
print time.strftime("[%Y/%m/%d %H:%M:%S]  ", time.localtime()) + "started"
server = BaseHTTPServer.HTTPServer(('', 8002), MyHandler).serve_forever()
