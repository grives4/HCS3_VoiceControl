import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setup(22,GPIO.IN,pull_up_down=GPIO.PUD_DOWN)


i = 0
while i == 0:
  if(GPIO.input(22)==1):
      print("up")
      i = 1
  else:
      print("down")
  time.sleep(1)

GPIO.cleanup()
