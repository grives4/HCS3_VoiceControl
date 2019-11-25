import RPi.GPIO as GPIO
import time
import smbus
import time

bus = smbus.SMBus(1)
address = 0x24

#Set direction of port a and b to read.
bus.write_byte_data(address,0x00,0xFF)
bus.write_byte_data(address,0x01,0xFF)

#Set pins to be monitored by interrupts
bus.write_byte_data(address,0x04,0xFF)
bus.write_byte_data(address,0x05,0xFF)

#Set the default value for the GPIO for the interrupt to compare against
bus.write_byte_data(address,0x06,0x00)
bus.write_byte_data(address,0x07,0x00)


#setup interrupts to trigger on either port change
bus.write_byte_data(address,0x0A,0x42)
bus.write_byte_data(address,0x0B,0x42)

GPIO.setmode(GPIO.BCM)
GPIO.setup(17,GPIO.IN,pull_up_down=GPIO.PUD_DOWN)


i = 0
while i == 0:
  print "-------- int Value -------"
  print "{0:016b}".format(bus.read_byte_data(address,0x0E))
  print "{0:016b}".format(bus.read_byte_data(address,0x0F))
  print "-------- IO Value -------"
  print "{0:016b}".format(bus.read_byte_data(address,0x12))
  print bus.read_byte_data(address,0x13)

  if(GPIO.input(17)==1):
      print("up")
  else:
      print("down")
  time.sleep(1)

GPIO.cleanup()


