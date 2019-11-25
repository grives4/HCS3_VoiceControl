#!/usr/bin/python

from Adafruit_PWM_Servo_Driver import PWM
import time

# ===========================================================================
# Example Code
# ===========================================================================

# Initialise the PWM device using the default address
# bmp = PWM(0x40, debug=True)
pwm = PWM(0x40, debug=True)

servoMin = 150  # Min pulse length out of 4096
servoMax = 600  # Max pulse length out of 4096

def setServoPulse(channel, pulse):
  pulseLength = 1000000                   # 1,000,000 us per second
  pulseLength /= 60                       # 60 Hz
  print "%d us per period" % pulseLength
  pulseLength /= 4096                     # 12 bits of resolution
  print "%d us per bit" % pulseLength
  pulse *= 1000
  pulse /= pulseLength
  pwm.setPWM(channel, 0, pulse)

pwm.setPWMFreq(60)                        # Set frequency to 60 Hz
#while (True):
  # Change speed of continuous servo on channel O
  #pwm.setPWM(0, 0, servoMin)
  #time.sleep(1)

#i = 150
#while i < 600:
#  pwm.setPWM(0, 0, i)
#  time.sleep(1)
#  i = i + 25
#  print i
#pwm.setPWM(0,0,0)

pwm.setPWM(0, 0, 600)
time.sleep(0.50)
pwm.setPWM(0, 0, 000)
pwm.setPWM(1, 0, 600)
time.sleep(0.50)
pwm.setPWM(1, 0, 000)
pwm.setPWM(2, 0, 600)
time.sleep(0.50)
pwm.setPWM(2, 0, 000)
pwm.setPWM(3, 0, 600)
time.sleep(0.50)
pwm.setPWM(3, 0, 000)
pwm.setPWM(4, 0, 600)
time.sleep(0.50)
pwm.setPWM(4, 0, 000)
pwm.setPWM(5, 0, 600)
time.sleep(0.50)
pwm.setPWM(5, 0, 000)
