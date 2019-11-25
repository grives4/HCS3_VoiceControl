#!/usr/bin/env python2.7
import mcp3008, time, os, subprocess, smtplib, string, cgi, RPi.GPIO as GPIO
from time import gmtime, strftime, sleep
from os import curdir, sep
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

# GPIO Setup 
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD) #Use physical pin numbers
relaybat1 = 11
relaybat2 = 13
GPIO.setup(relaybat1, GPIO.OUT)
GPIO.setup(relaybat2, GPIO.OUT)
GPIO.output(relaybat1, GPIO.HIGH) #Start with both relays off to allow program to choose which battery to move to #Low=Relay on High=Relay off
GPIO.output(relaybat2, GPIO.HIGH)

#Settings
time_between_readings = 5 # seconds between clusters of readings
batterycutoff1 = 11.80 # Battery 1 cutoff voltage. 11.58 is the recomended setpoint for 12V Battery
batterygood1 = 13.70 # Battery 1 Fully Charged voltage
batterycutoff2 = 11.80 # Battery 2 cutoff voltage. 11.58 is the recomended setpoint for 12V Battery
batterygood2 = 13.70 # Battery 2 Fully Charged voltage
previous_voltage1 = batterycutoff1 + 1 # initial value for software purposes
previous_voltage2 = batterycutoff2 + 1 # initial value for software purposes
batteryselect = 1
battery1avaliable = "Yes"
battery2avaliable = "No"
time_between_relay_switchover = 5
httpport = 1234

# email variables
fromaddr = 'MyFromAddress'  
toaddr  = 'MyToAddress'  
# Yahoomail login details
username = 'MyUsername'  
password = "'MyEmailPassword" 

def write_battery_log(batterylogline):
    batterylogfile = ("/var/log/batterylog.txt")
    batterylogfile = open(batterylogfile, "a")
    batterylogfile.write(batterylogline + '\n')
    batterylogfile.close()

class MyHandler(BaseHTTPRequestHandler):
    stopped = False
    allow_reuse_address = True

    def do_GET(self):
        try:
            if self.path.endswith("index.live"):   #our dynamic content
                self.send_response(200)
                self.send_header('Content-type',   'text/html')
                self.end_headers()
                datetime = time.strftime("%H:%M:%S, %d-%m-%Y")
                self.wfile.write ("<html><title>%s</title>" %datetime)
                self.wfile.write("<body><br> Battery 1 Voltage is: %.2f "%volts1)
                self.wfile.write("the cutoff voltage is: %.2f</br>"%batterycutoff1)
                self.wfile.write("<br>Battery 2 Voltage is: %.2f "%volts2)
                self.wfile.write("the cutoff voltage is: %.2f </br>"%batterycutoff2)
                self.wfile.write("<br>The Battery currently in service is battery %.0f </br>"%batteryselect)
                self.wfile.write("<br>Is battery 1 avaliable: " + battery1avaliable + "</br>")
                self.wfile.write("<br>Is battery 2 avaliable: " + battery2avaliable + "</br>")
                self.wfile.write("<br>Time Between Readings: %.0f </br>" %time_between_readings)
                server.server_close()
                return
                
            return
        except IOError:
            self.send_error(404,'File Not Found: %s' % self.path)


def get_up_stats():
      #  "Returns a tuple (uptime, 5 min load average)"
    try:
        s = subprocess.check_output(["uptime"])
        load_split = s.split('load average: ')
        load_five = float(load_split[1].split(',')[1])
        up = load_split[0]
        up_pos = up.rfind(',',0,len(up)-4)
        up = up[:up_pos].split('up ')[1]
        return ( up , load_five )       
    except:
        return 0

###################################################################################################
#Email body starts hear.
###################################################################################################
# you can edit the text for the email to suit your requirements
#Send Email if battery 1 is low and battery 2 is charged and avaliable
def send_emailbat1():    
    BODY = string.join((
        "From: %s" % fromaddr,
        "To: %s" % toaddr,
        "Subject: Battery 1 Low on Shed Pi Switching to Battery 2",
        "",
        "Battery 1 voltage was just measured at %.2f" % Battery1 + " which is at or below the setpoint of %.2f" % batterycutoff1 + ".",
        "If it happens twice in a row the pi will move over to Battery No 2 the voltage on battery 2 is currentley at %.2f" % voltstring2 + " .",
        "The Up time is: "+get_up_stats()[0]

        ), "\r\n")
      
    # send the email  
    server = smtplib.SMTP('smtp.mail.yahoo.co.uk:587')
    server.login(username,password)  
    server.sendmail(fromaddr, toaddr, BODY)  
    server.quit()

#Send email if Battery 1 is depleated and battery 2 is not avaliable #tested and working
def send_emailbat1nobat2(): 
    BODY = string.join((
        "From: %s" % fromaddr,
        "To: %s" % toaddr,
        "Subject: Battery 1 Low on Shed Pi Battery 2 Not avaliable",
        "",
        "Battery 1 voltage was just measured at %.2f" % volts1 + " which is at or below the setpoint of %.2f" % batterycutoff1 + ".",
        "If it happens twice in a row the pi will shutdown. Battery No 2 voltage is at %.2f" % volts2 + "Which is at or below the setpoint of %.2f." % batterycutoff2 + ".",
        "The Up time is: "+get_up_stats()[0]

        ), "\r\n")
      
    #send the email  
    server = smtplib.SMTP('smtp.mail.yahoo.co.uk:587')  
    server.login(username,password)  
    server.sendmail(fromaddr, toaddr, BODY)  
    server.quit()

#Send email if Battery 1 is low and moving over to battery 2 #Tested and working
def send_emailbat1lobat2ok(): 
    BODY = string.join((
        "From: %s" % fromaddr,
        "To: %s" % toaddr,
        "Subject: Battery 1 Low on Shed Pi Moveing over to Battery 2",
        "",
        "Battery 1 voltage was just measured at %.2f" % volts1 + " which is at or below the setpoint of %.2f" % batterycutoff1 + ".",
        "Moveing over to Battery No.2 voltage is at %.2f" % volts2 + " .",
        "The Up time is: "+get_up_stats()[0]

        ), "\r\n")
      
    #send the email  
    server = smtplib.SMTP('smtp.mail.yahoo.co.uk:587')  
    server.login(username,password)  
    server.sendmail(fromaddr, toaddr, BODY)  
    server.quit()

#Send email when Battery 1 has charged back up again and back online
def send_emailbat1online(): 
    BODY = string.join((
        "From: %s" % fromaddr,
        "To: %s" % toaddr,
        "Subject: Battery 1 Back online",
        "",
        "Battery 1 voltage was just measured at %.2f" % volts1 + " which is at or above the setpoint of %.2f" % batterygood1 + ".",
        "Battery No 2 voltage is at %.2f" % volts2 + " Battery 2 cutoff setpoint is set to %.2f" % batterycutoff2 + ".",
        "The Up time is: "+get_up_stats()[0]

        ), "\r\n")
      
    #send the email  
    server = smtplib.SMTP('smtp.mail.yahoo.co.uk:587')  
    server.login(username,password)  
    server.sendmail(fromaddr, toaddr, BODY)  
    server.quit()

#Battery 2 low and battery 1 not fully charged moving back to battery 1
def send_emailbat2lowbat1notfull():
    BODY = string.join((
        "From: %s" % fromaddr,
        "To: %s" % toaddr,
        "Subject: Battery 1 Back online",
        "",
        "Battery 2 voltage low it was just measured at %.2f" % volts2 + " which is at or below the setpoint of %.2f" % batterycutoff2 + ".",
        "Battery No 1 voltage is at %.2f" % volts1 + " Battery 1 cutoff setpoint is set to %.2f" % batterycutoff1 + ".",
        "The Up time is: "+get_up_stats()[0]

        ), "\r\n")
      
    #send the email  
    server = smtplib.SMTP('smtp.mail.yahoo.co.uk:587')  
    server.login(username,password)  
    server.sendmail(fromaddr, toaddr, BODY)  
    server.quit()

###################################################################################################
#Program Variables start hear
###################################################################################################
try:
    while True:
        # Variables
        battery1 = mcp3008.readadc(0)
        battery2 = mcp3008.readadc(2)
        minute = time.strftime("%M")
        volts1 = battery1 * ( 15 / 1024.0)
        voltstring1 = str(volts1)[0:5]
        volts2 = battery2 * ( 15 / 1024.0)
        voltstring2 = str(volts2)[0:5]
        # Check Battery 2 avalibilty  
        if volts2 > batterycutoff2:
            battery2avaliable = "Yes"
        else:
            battery2avaliable = "No"

        
        
#1. Battery 1 Low voltage and Battery 2 Not avaliable
        if batteryselect == 1:
            if volts1 <= batterycutoff1:
                if previous_voltage1 <= batterycutoff1:
                    if battery2avaliable == "No":
                        try:
                            send_emailbat1nobat2()
                        except:
                            print "email failed"
                        battery1avaliable = "No"
                        batterylogline = time.strftime("%d-%m-%Y,%H:%M:%S")
                        batterylogline += ' Shutting down due to Battery 2 not avaliable and Battery 1 low Voltage at '
                        batterylogline += voltstring1
                        batterylogline += ' Battery 2 voltage at '
                        batterylogline += voltstring2
                        write_battery_log(batterylogline)
                        #initiate shutdown process
                        command = os.system("sync")
                        command = 0
                        if command == 0:
                            command = "/usr/bin/sudo /sbin/shutdown -h now"
                            process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
                            output = process.communicate()[0]

#2. Battery 1 Low voltage and Battery 2 is avaliable
        if batteryselect == 1:
            if volts1 <= batterycutoff1:
                if previous_voltage1 <= batterycutoff1:
                    if battery2avaliable == "Yes":
                        try:
                            send_emailbat1lobat2ok()
                        except:
                            print "email failed"
                        batteryselect = 2
                        battery1avaliable = "No"
                        batterylog = time.strftime("%d-%m-%Y,%H:%M:%S")
                        batterylog += ' Battery 1 Low voltage moveing over to battery 2 battery 1 voltage is '
                        batterylog += voltstring1
                        batterylog += ' Battery 2 voltage is at '
                        batterylog += voltstring2
                        write_battery_log(batterylog)

#3. Battery 1 Charged back up whilest on Battery 2
        if batteryselect == 2:
            if volts1 > batterygood1:
                if previous_voltage1 >= batterygood1:
                    batteryselect = 1
                    battery1avaliable = "Yes"
                    try:
                        send_emailbat1online()
                    except:
                        print "email failed"
                    batterylog = time.strftime("%d-%m-%Y,%H:%M:%S")
                    batterylog += ' Battery 1 charged back up and its voltage is '
                    batterylog += voltstring1
                    batterylog += ' Battery 2 voltage at '
                    batterylog += voltstring2
                    write_battery_log(batterylog)

#4. Battery 2 Low when Battery 1 is not fully Charged up
        if batteryselect ==2:
            if volts2 <= batterycutoff2:
                if previous_voltage2 <= batterycutoff2:
                    if volts1 > batterycutoff1:
                        try:
                            send_emailbat2lowbat1notfull
                        except:
                            print "email failed"
                        batterylog = time.strftime("%d-%m-%Y,%H:%M:%S")
                        batterylog += ' Battery 2 Low and Battery 1 not fully charged but moving over to Battery 1 voltage at '
                        batterylog += voltstring1
                        batterylog += ' Battery 2 voltage at '
                        batterylog += voltstring2
                        write_battery_log(batterylog)
                        battery1avaliable = "Yes"
                        batteryselect = 1


#5. Battery 2 Low voltage and Battery 1 Not avaliable
        if batteryselect == 2:
            if volts2 <= batterycutoff2:
                if previous_voltage2 <= batterycutoff2:
                    if battery1avaliable == "No":
                        try:
                            send_emailbat1nobat2()
                        except:
                            print "email failed"
                        batterylog = time.strftime("%d-%m-%Y,%H:%M:%S")
                        batterylog += ' Shutting down due to Battery 2 Low and Battery 1 not abaliable Battery 2 voltage at '
                        batterylog += voltstring2
                        batterylog += ' Battery 1 voltage at '
                        batterylog += voltstring1
                        write_battery_log(batterylog)
                         #initiate shutdown process
                        command = os.system("sync")
                        #command = 0
                        if command == 0:
                            command = "/usr/bin/sudo /sbin/shutdown -h now"
                            process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
                            output = process.communicate()[0]

#Battery 1 is wired to the normaly closed contact and Battery 2 is wired to the normaly open contact this is so that when power is first applyed the Pi will boot up and then make the change over as and when requiered.
#Battery 1 Switch over to battery 2 there is a timer hear so that there is no loss of power whilest switching creating a make before break condition        
        if batteryselect == 1:
            GPIO.output(relaybat1, GPIO.HIGH) #Low=Relay on High=Relay off
            time.sleep(time_between_relay_switchover)
            GPIO.output(relaybat2, GPIO.HIGH)        

#Battery 2 Switch over to battery 1 there is a timer hear so that there is no loss of power whilest switching creating a make before break condition
        if batteryselect == 2:
            GPIO.output(relaybat2, GPIO.LOW) #Low=Relay on High=Relay off
            time.sleep(time_between_relay_switchover)
            GPIO.output(relaybat1, GPIO.LOW)

# Every 30 Minutes the battery values are logged to my other raspberry pi for displaying on the internet
#o'clock write to log
        if minute == "00":
            halfhourbatterylogline = time.strftime("%d-%m-%Y,%H:%M:%S")
            halfhourbatterylogline += ', Battery 1 ,'
            halfhourbatterylogline += voltstring1
            halfhourbatterylogline += ', Battery 2 ,'
            halfhourbatterylogline += voltstring2
            halfhourbatterylogdate = time.strftime("%d-%m-%Y")
            halfhourbatterylog = "".join(["/home/pi/logfiles/battery_log/battery_30minlog_", halfhourbatterylogdate, ".txt"])
            halfhourbatterylog = open(halfhourbatterylog, "a")
            halfhourbatterylog.write(halfhourbatterylogline + '\n')
            halfhourbatterylog.close()
            filename = "".join(["scp /home/pi/logfiles/battery_log/battery_30minlog_", halfhourbatterylogdate, ".txt" , " pi@175.52.104.124:/var/www/logfiles/battery_data/"])
            os.system (filename)


#half hour write to log
        if minute == "30":
            halfhourbatterylogline = time.strftime("%d-%m-%Y,%H:%M:%S")
            halfhourbatterylogline += ', Battery 1 ,'
            halfhourbatterylogline += voltstring1
            halfhourbatterylogline += ', Battery 2 ,'
            halfhourbatterylogline += voltstring2
            halfhourbatterylogdate = time.strftime("%d-%m-%Y")
            halfhourbatterylog = "".join(["/home/pi/logfiles/battery_log/battery_30minlog_", halfhourbatterylogdate, ".txt"])
            halfhourbatterylog = open(halfhourbatterylog, "a")
            halfhourbatterylog.write(halfhourbatterylogline + '\n')
            halfhourbatterylog.close()
            filename = "".join(["scp /home/pi/logfiles/battery_log/battery_30minlog_", halfhourbatterylogdate, ".txt" , " pi@175.52.104.124:/var/www/logfiles/battery_data/"])
            os.system (filename)

        previous_voltage1 = volts1
        previous_voltage2 = volts2
        server = HTTPServer(('', httpport), MyHandler)
        server.serve_forever()
        time.sleep(time_between_readings)

except KeyboardInterrupt:             # trap a CTRL+C keyboard interrupt
    GPIO.output(relaybat1, GPIO.HIGH) #Low=Relay on High=Relay off
    time.sleep(0.5)
    GPIO.output(relaybat2, GPIO.HIGH) 
    GPIO.Cleanup()
    server.socket.close()