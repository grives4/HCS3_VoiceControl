from awake import wol
import sys
import elementtree.ElementTree as ET
from controllers import *
import pdb
from pandora import *

class requestprocessor(object):

   def keypress(self,key):
      controllers().write_to_computer(key)
      
   def change_radio_station(self,station):
      station.replace(".","")
      controllers().write_to_serial_port('&AH66,R1,TUNE,' + station.replace(".","") + '0',"1")
      controllers().write_to_serial_port('&AH66,R1,TUNE,' + station.replace(".","") + '0',"2")
      
   def change_source(self,source,location,chassis="1"):
      controllers().write_to_serial_port('&AH66,AUD,' + location + ',' + zone,chassis)      
      
   def change_volume(self,volume,location,chassis="1"):
      print(chassis)
      controllers().write_to_serial_port('&AH66,VOL,' + location + ',' + volume,chassis)

   def change_treble(self,treble,location,chassis="1"):
      if treble < 0:
         treble = treble * -1
         controllers().write_to_serial_port('&AH66,TRE,' + location + ',-,' + str(treble),chassis)
      else:
         controllers().write_to_serial_port('&AH66,TRE,' + location + ',+,' + str(treble),chassis)

   def change_base(self,base,location,chassis="1"):
      if base < 0:
         base = base * -1
         controllers().write_to_serial_port('&AH66,BAS,' + location + ',-,' + str(base),chassis)
      else:
         controllers().write_to_serial_port('&AH66,BAS,' + location + ',+,' + str(base),chassis)
      
   def get_version(self):
      try:
          version = controllers().write_to_serial_port('&AH66,VER,1,?')
      except:
          version = ""
      return version  
      
   def get_radio_station(self):
      try:
          tempdata = controllers().write_to_serial_port('&AH66,R1,TUNE,?')
          tempstation = tempdata.split(",")[2]
          tempstation = tempstation[:-2] + '.' + tempstation[-2:]
      except:
          tempstation = ""
      return tempstation.strip()

   def get_volume(self, zone,chassis="1"):
      try:
         volume = controllers().write_to_serial_port('&AH66,VOL,' + zone + ',?',chassis)
         volume = volume.split(',')[2]
      except:
         #print "Vol not found"
         #pdb.set_trace()
         try:
         	volume = controllers().write_to_serial_port('&AH66,VOL,' + zone + ',?',chassis)
         	volume = volume.split(',')[2]
         except:
         	#print "Vol not found"
         	pass
         	#pdb.set_trace()
         return 	
         volume = 0
      return volume
      
   def get_base(self,zone,location="1"):
      try:
          base = controllers().write_to_serial_port('&AH66,BAS,' + zone + ',?',location)
          if base.split(",")[2] == '-':
            base = -1 * int(base.split(",")[3])
          elif base.split(",")[2] == '0':
            base = 0
          else:
            base = int(base.split(",")[3])
      except:
           #print "Base not found"
           try:
               base = controllers().write_to_serial_port('&AH66,BAS,' + zone + ',?',location)
               if base.split(",")[2] == '-':
                 base = -1 * int(base.split(",")[3])
               elif base.split(",")[2] == '0':
                 base = 0
               else:
                 base = int(base.split(",")[3])
           except:
                 #print "Base not found"
                 try:
                     base = controllers().write_to_serial_port('&AH66,BAS,' + zone + ',?',location)
                     if base.split(",")[2] == '-':
                       base = -1 * int(base.split(",")[3])
                     elif base.split(",")[2] == '0':
                       base = 0
                     else:
                       base = int(base.split(",")[3])
                 except:
                       #print "Base not found"
                       pass
                 return
           return      
           base = -1
      return base
         
      
   def get_treble(self,zone,location="1"):
      try:
          treble = controllers().write_to_serial_port('&AH66,TRE,' + zone + ',?',location)
          if treble.split(",")[2] == '-':
            treble = -1 * int(treble.split(",")[3])
          elif treble.split(",")[2] == '0':
            treble = 0
          else:
            treble = int(treble.split(",")[3])
      except:
          #print "Treble not found"
          try:
              treble = controllers().write_to_serial_port('&AH66,TRE,' + zone + ',?',location)
              if treble.split(",")[2] == '-':
                treble = -1 * int(treble.split(",")[3])
              elif treble.split(",")[2] == '0':
                treble = 0
              else:
                 treble = int(treble.split(",")[3])
          except:
              #print "Treble not found"
              try:
                  treble = controllers().write_to_serial_port('&AH66,TRE,' + zone + ',?',location)
                  if treble.split(",")[2] == '-':
                    treble = -1 * int(treble.split(",")[3])
                  elif treble.split(",")[2] == '0':
                    treble = 0
                  else:
                    treble = int(treble.split(",")[3])
              except:
                  #print "Treble not found"
                  pass
              return
          return
          treble = -1
      return treble

   def get_source(self,zone,location="1"):
      try:
          input = controllers().write_to_serial_port('&AH66,AUD,' + zone + ',?',location)
          input = input.split(",")[2]
      except:
          #print "Input not found."
          try:
              input = controllers().write_to_serial_port('&AH66,AUD,' + zone + ',?',location)
              input = input.split(",")[2]
          except:
              #print "Input not found."
              pass
          return    
          input = 0
      return input   

   def handle_command(self,command):

      commands = self.get_commands()
      response = []    
      
      try:
         tempActions = (item["actions"] for item in commands if item["name"].lower() == command.lower()).next()

         for action in tempActions:   
            #print("----------")
            #print(action)
            #print("----------")
            
            #Stereo
            if (action.get('type') == 'serial'):
               response = controllers().write_to_serial_port(action.get('data'),action.get('location'))
               time.sleep(float(action.get('delay')))               
            #Volume control
            if (action.get('type') == 'volume'):
               zone = action.get('data').split(',')[0]
               volume = int(self.get_volume(zone,action.get('location')))
               if action.get('data').split(',')[1] == "up":
                  volume += 5
               else:
                  volume -= 5
               data = "&AH66,VOL," + zone + "," + str(volume)
               controllers().write_to_serial_port(data,action.get('location'))
               location = self.zone_name(zone,action.get('location'))
               response.append('volume,' + location + ',' + str(volume))
            if (action.get('type') == 'source'):
               zone = action.get('data').split(',')[0]
               source = action.get('data').split(',')[1]
               data = "&AH66,AUD," + zone + "," + source
               controllers().write_to_serial_port(data,action.get('location'))
               location = self.zone_name(zone,action.get('location'))
               source = self.source_name(source)
               response.append('source,' + location + ',' + source)
            #Wake Computer
            if (action.get('type') == 'wake'):
               wol.send_magic_packet(action.get('data'))
            #IR transmission
            if (action.get('type') == 'ir'):
               controllers().write_to_ir(action.get('data'),action.get('location'))
               time.sleep(float(action.get('delay')))
            #Press keys on computer
            if (action.get('type') == 'key press'):
               controllers().write_to_computer(action.get('data'))
            #Run another command
            if (action.get('type') == 'command'):
               results = self.handle_command(action.get('data'), status)
               #print ('sending keypress from type = command')
                 
      except:
         print("Error occurred in requestprocessor handle_command.")
         print(sys.exc_info()[0])

      return response
      
   def get_commands(self):
      try:
         XMLtree = ET.parse("Configuration/commands.xml")
         doc = XMLtree.getroot()
         commands = []
         for elem in doc.findall('command'):
            actions = []
            for action in elem.findall('action'):
               tempAction = {'type' : action.get('type'), 'data': action.get('data'), 'delay' : action.get('delay') , 'location' : action.get('location')}
               actions.append(tempAction)
            commands.append({ 'name' : elem.get('name'), 'actions' : actions })
      except:
         commands = ""
      return commands
   
   def zone_name(self,zone,chassis):
      XMLtree = ET.parse("Configuration/config.xml")
      doc = XMLtree.getroot()
      for elem in doc.findall('config'): 
         if elem.get('name') == 'locations': 
            for item in elem.findall('item'):
               if item.get('zone') == zone and item.get('chassis') == chassis:
                  return item.get('name')

   
   def source_name(self,source):
      XMLtree = ET.parse("Configuration/config.xml")
      doc = XMLtree.getroot()
      for elem in doc.findall('config'): 
         if elem.get('name') == 'options': 
            for item in elem.findall('item'):
               if item.get('source') == source:
                  return item.get('name')
                  
    

  
