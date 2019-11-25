import smbus
import time
bus = smbus.SMBus(1)
address = 0x20

#Set direction of port a and b to read.
bus.write_byte_data(address,0x00,0xFF)
bus.write_byte_data(address,0x01,0xFF)

#setup interrupts to trigger on either port change
bus.write_byte_data(address,0x0A,0x42)
bus.write_byte_data(address,0x0B,0x42)
while True:
    print "{0:016b}".format(bus.read_byte_data(address,0x12))
    print "{0:016b}".format(bus.read_byte_data(address,0x13))
    time.sleep(1)

