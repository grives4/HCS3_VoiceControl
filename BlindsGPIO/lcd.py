import lcddriver
from time import *

lcd = lcddriver.lcd()
lcd.lcd_write(0x08 | 0x04)
lcd.lcd_display_string("1111111", 1)
sleep(5)
lcd.lcd_strobe(0x80)
lcd.lcd_write(0x08 | 0x00)
