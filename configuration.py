import elementtree.ElementTree as ET
from controllers import *
from requestprocessor import *
import pdb

class configuration(object):

   def get_system_configuration(self):
      systemConfiguration = {
        "locations": self.config('locations'),
        "blinds": ['Den','Kitchen','Theater'], 
        "options": self.config('options'),
        "radiostations": self.config('radiostations')}
      #print systemConfiguration
      return systemConfiguration
      
   def get_mce_configuration(self):
      XMLtree = ET.parse("Configuration/config.xml")
      doc = XMLtree.getroot()
      for elem in doc.findall('config'): 
         if elem.get('name') == 'MCE': 
            mceConfig = {}
            for item in elem.findall('item'):
               mceConfig[item.get('name')] = { "Title": item.get('Title'),
                                               "On": item.get('On'),
                                               "Off": item.get('Off'),
                                               "Up": item.get('Up'),
                                               "Down": item.get('Down')
                                               }
            return mceConfig
      return mceConfig      
      
   def get_system_status(self): 
      systemStatus = []
      locations = self.config('locations')
      #So request some dummy data.
      #Now request the data that we want.
      for location in locations:
         zone,chassis = self.zone_location(location)         
         systemStatus.append('volume,' + location + ',' + str(requestprocessor().get_volume(zone,chassis)))
         systemStatus.append('treble,' + location + ',' + str(requestprocessor().get_treble(zone,chassis)))
         systemStatus.append('base,' + location + ',' + str(requestprocessor().get_base(zone,chassis)))
         systemStatus.append('source,' + location + ',' + self.source_location(requestprocessor().get_source(zone, chassis)))

      return systemStatus

   def get_system_status_template(self): 
      systemStatus = {}
      locations = self.config('locations')
      #So request some dummy data.
      #Now request the data that we want.
      for location in locations:
         zone = self.zone_location(location)
         #print location + "  " + zone
         systemStatus[location] = { "Volume": '',
                                    "Treble": '',
                                    "Base": '',
                                    "Input": 'Off' }
         #print(systemStatus[location])
      systemStatus['RadioStation'] = requestprocessor().get_radio_station()
      systemStatus['PandoraStation'] = ""
      return systemStatus


   def config_exists(self,name):
      XMLtree = ET.parse("Configuration/config.xml")
      doc = XMLtree.getroot()
      for elem in doc.findall('config'): 
         if elem.get('name') == name: 
            return True
      return False
      
   def config(self,setting):
      XMLtree = ET.parse("Configuration/config.xml")
      doc = XMLtree.getroot()
      for elem in doc.findall('config'): 
         if elem.get('name') == setting: 
            items = []       
            for item in elem.findall('item'):
               items.append(item.get('name'))
            return items
            
   def zone_location(self,location):
      XMLtree = ET.parse("Configuration/config.xml")
      doc = XMLtree.getroot()
      for elem in doc.findall('config'): 
         if elem.get('name') == 'locations': 
            for item in elem.findall('item'):
               if item.get('name') == location:
                  return item.get('zone'),item.get('chassis')
                  
   def source_location(self,option):
      XMLtree = ET.parse("Configuration/config.xml")
      doc = XMLtree.getroot()
      for elem in doc.findall('config'): 
         if elem.get('name') == 'options': 
            for item in elem.findall('item'):
               if item.get('source') == option:
                  return item.get('name')
