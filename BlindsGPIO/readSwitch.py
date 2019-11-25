import smbus
import time
bus = smbus.SMBus(1)
address = 0x20

bus.write_byte_data(address,0x00,0xFF)
#bus.write_byte_data(address,0x06,0xFF)
print bus.read_byte_data(address,0x00)
print bus.read_byte_data(address,0x06)
print bus.read_byte_data(address,0x0A)
print "--------------"
print "--------------"
while True:
    print "{0:008b}".format(bus.read_byte_data(address,0x12))
    print "{0:008b}".format(bus.read_byte_data(address,0x13))
    time.sleep(1)

