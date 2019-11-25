import re
#import serial
import time
#import urllib
#import urllib2
import elementtree.ElementTree as ET
from awake import wol
#import socket
from WolframAlpha import *
#from time import gmtime, strftime
#import json
import sys
import pyttsx
from controllers import *
from radioprocessor import *
from commandprocessor import *

#TODO:  This is a mess.  Clean it up.
class voiceprocessor(object):

   def handle_command(self,command,status):      
      command = command.lower()
      words = command.split()
      questionList = self.voiceconfig('questions')
      
      if 'station' in command:
            phraseToSpeak = radioprocessor().getradiostationdetails()
            self.speak_to_user(phraseToSpeak,status)
      elif words[0] in questionList:
            phraseToSpeak = wolframalpha().get_answer_from_wolfram_alpha(command.replace('question',''))
            self.speak_to_user(phraseToSpeak,status)
      else:
            command, amount = self.clean_up_phrase(command)
            print command
            for i in range(0,amount):
                  phraseToSpeak = commandprocessor().handle_command(command,status)
      return phraseToSpeak
   
   def clean_up_phrase(self,command):
      words = command.split(' ')
      action = ""
      location = ""
      amount = 1
      setting = ""
      
      locations = self.voiceconfig('locations')
      settings = self.voiceconfig('settings')
      amounts = self.voiceconfig('amounts')

      
      #Clean up phrase.
      replacements = self.wordreplacements()
      for index in range(len(words)): 
          if words[index] in replacements:
             words[index] = replacements[words[index]]
      print words
                          
      #Translate command.
      for word in words:
          #If its a radio station, translate it.
          if re.match("^\d+?\.\d+?$",word) is not None:
             if (float(word) > 87 and float(word) < 108):
                radioprocessor.tune_radio(str(int(float(word) * 100)))
                return "" , 1
          #Commands are in the form of location + setting.
          #ex. porch + radio = porchradio.  In the commands file, porchradio
          #    turns on the radio on the porch
          if word in locations:
             location = word
          if word in settings:
             setting = word
         #Amount determine how often the command is repeated.
         #ex. porchup and the amount of 5 presses the volume up 5 times.
          if word in amounts:
             amount = int(word)
      translatedCommand = location + setting
      if translatedCommand == "":
          translatedCommand = "I didn't understand you"
      with open("phrases.txt","a") as myFile:
           myFile.write("Heard: " + command + "     Translated: " + translatedCommand + "\r")
      return translatedCommand, amount

   def speak_to_user(self,phraseToSpeak,status):
      #Save current state.
      if status["Quiet"] == "Off":
            status = self.togglequiet(status)
      #Switch state of Den and Kitchen and mute Theater.
      controllers().write_to_serial_port('&AH66,AUD,2,1')
      controllers().write_to_serial_port('&AH66,AUD,3,1')
      controllers().write_to_serial_port('&AH66,VOL,2,90')
      controllers().write_to_serial_port('&AH66,VOL,3,90')
      speechEngine = pyttsx.init()
      #rate = speechEngine.getProperty('rate')
      #speechEngine.setProperty('rate',80)
      speechEngine.say(phraseToSpeak)
      speechEngine.runAndWait()
      speechEngine.stop()
      #Switch back to previous state and unmute theater.
      status = self.togglequiet(status)
      return
   
   def togglequiet(self, status):

      if status["Quiet"] == "Off":
         status["Quiet"] = "On"      
         status["Z2Vol"] = controllers().write_to_serial_port('&AH66,VOL,2,?').split(",")[3]
         status["Z3Vol"] = controllers().write_to_serial_port('&AH66,VOL,3,?').split(",")[3]
         status["Z1"] = controllers().write_to_serial_port('&AH66,AUD,1,?').split(",")[3]
         status["Z2"] = controllers().write_to_serial_port('&AH66,AUD,2,?').split(",")[3]
         status["Z3"] = controllers().write_to_serial_port('&AH66,AUD,3,?').split(",")[3]
         status["Z4"] = controllers().write_to_serial_port('&AH66,AUD,4,?').split(",")[3]
         status["Z5"] = controllers().write_to_serial_port('&AH66,AUD,5,?').split(",")[3]
         status["Z6"] = controllers().write_to_serial_port('&AH66,AUD,6,?').split(",")[3]
         controllers().write_to_serial_port('&AH66,SysOff')
      else:
         status["Quiet"] = "Off"
         controllers().write_to_serial_port('&AH66,AUD,1,' + status["Z1"])
         controllers().write_to_serial_port('&AH66,VOL,2,' + status["Z2Vol"])
         controllers().write_to_serial_port('&AH66,AUD,2,' + status["Z2"])
         controllers().write_to_serial_port('&AH66,VOL,3,' + status["Z3Vol"])
         controllers().write_to_serial_port('&AH66,AUD,3,' + status["Z3"])
         controllers().write_to_serial_port('&AH66,AUD,4,' + status["Z4"])
         controllers().write_to_serial_port('&AH66,AUD,5,' + status["Z5"])
         controllers().write_to_serial_port('&AH66,AUD,6,' + status["Z6"])
      return status
      
         
   def voiceconfig(self,item):
      XMLtree = ET.parse("voiceconfig.xml")
      doc = XMLtree.getroot()
      voiceconfig = []
      for elem in doc.findall('config'):
         if elem.get('name') == item:     
            for item in elem.findall('item'):
               voiceconfig.append(item.get('name'))
      return voiceconfig
   
      
   def wordreplacements(self):
      XMLtree = ET.parse("voiceconfig.xml")
      doc = XMLtree.getroot()
      wordreplacements = {}
      for elem in doc.findall('config'):
         if elem.get('name') == 'substitutes':     
            for item in elem.findall('item'):
               for substitute in item.findall('substitute'):
                  tempItem = {'name' : item.get('name')}
                  wordreplacements.update( { substitute.get('name') : item.get('name') } )
      return wordreplacements
      
      