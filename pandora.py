import os
import re
import time
import threading
import elementtree.ElementTree as ET
import pdb
import subprocess
from pandora import *

class PandoraProcessor(threading.Thread):

   def __init__(self,PandoraRequestQueue,PandoraRequestReadyEvent,PandoraDataQueue,PandoraDataReadyEvent):
   
      super(PandoraProcessor, self).__init__()
      
      #Requests coming in to class.
      self.PandoraRequestQueue = PandoraRequestQueue
      self.PandoraRequestReadyEvent = PandoraRequestReadyEvent
      
      #Data coming from class.
      self.PandoraDataQueue = PandoraDataQueue
      self.PandoraDataReadyEvent = PandoraDataReadyEvent
      
      #Class specific variables.
      self.PandoraRunning = False
      self.PandoraStationList = []
      
   def run(self):
      self.PandoraStationList = self.get_pandora_data()['stationList']
      
      while 1 == 1:
      
         #Wait for a command
         self.PandoraRequestReadyEvent.wait()
         
         #There is something in the queue, process it.
         while not self.PandoraRequestQueue.empty():   
            
            #Get the request off the queue
            PandoraRequest = self.PandoraRequestQueue.get()
            
            #Put the station list in the queue
            if PandoraRequest == "StationList": 
               #self.send_song_information()
               self.PandoraDataQueue.put(self.PandoraStationList)      
               self.PandoraDataReadyEvent.set()
             
            #Put the current song and song information in the queue  
            elif PandoraRequest == "CurrentSong":
               if self.PandoraRunning == True:
                  self.send_song_information()
               else:
                  self.PandoraDataQueue.put('PandoraSong, ') 
                  self.PandoraDataQueue.put('PandoraSongTime,--') 
                  self.PandoraDataQueue.put('PandoraRemainingTime,--') 
                  self.PandoraDataReadyEvent.set()
               
            
            #If it is a single character, its a station change.
            #Change the station and put the new song in the queue.
            elif len(PandoraRequest) == 1:
               #print(PandoraRequest)
               self.send_command_to_pianobar('s')
               self.send_command_to_pianobar(PandoraRequest + '\r\n')
               time.sleep(3)
               self.send_song_information()
            
            #If its none of the above, then its a command request, process that request.
            elif len(PandoraRequest) > 1:
               
               #Get command list from XML file.
                commands = self.get_commands()
                tempActions = (item["actions"] for item in commands if item["name"].lower() == PandoraRequest.lower()).next()
                
                #Cycle through the actions from the command sent.
                for action in tempActions:   
                    
                    #Start Pandora and send the current song information.
                    if (action.get('data') == 'zzz'): 
                         
                        if self.PandoraRunning == False:       
                           #Start the subprocess up for pianobar.    
                           os.system('pianobar >/home/pi/.config/pianobar/out &')      

                           #What for start up.
                           time.sleep(3)
                           #self.send_command_to_pianobar('0\r\n')
                           #time.sleep(2)
                           self.PandoraRunning = True

                        #Put the info in the queue.
                        self.send_song_information()
                        
                    #Quit Pandora and null out the song information.
                    elif (action.get('data') == 'q'):
                        if self.PandoraRunning == True:
                           self.send_command_to_pianobar('q')
                           self.PandoraDataQueue.put('PandoraSong, ') 
                           self.PandoraDataQueue.put('PandoraSongTime,--') 
                           self.PandoraDataQueue.put('PandoraRemainingTime,--') 
                           self.PandoraDataReadyEvent.set()
                           self.PandoraRunning = False
                     
                    #Go to the next song and send the new song information.
                    elif (action.get('data') == 'n'):
                        if self.PandoraRunning == True:
                           self.send_command_to_pianobar('n')
                           time.sleep(3)
                           self.send_song_information()
                        
                    #Pause or play
                    elif (action.get('data') == 'p'): 
                        if self.PandoraRunning == True:
                           self.send_command_to_pianobar('p')

                    #Like the song                           
                    elif (action.get('data') == '+'):
                        if self.PandoraRunning == True:
                           self.send_command_to_pianobar('+')
                        
                    #Unlike the song and send the new song information   
                    elif (action.get('data') == '-'):
                        if self.PandoraRunning == True:
                           self.send_command_to_pianobar('-')
                           self.send_song_information()
                  
            #The queue has been processed, so mark it done and clear the event.         
            self.PandoraRequestQueue.task_done()
            self.PandoraRequestReadyEvent.clear()

   
   #Reads the command file.
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
   

   #Get the list of stations and process them.
   def get_pandora_data (self):

       receivePath = '/home/pi/.config/pianobar/out'
       clearFifo = open(receivePath, 'w').close() 
  
       tempStation = '0'
       tempSong = ''
       tempRemainingTime = '--'
       tempTotalTime = '--'
  
       try:
  
          if self.PandoraRunning == False:
            os.system('pianobar >/home/pi/.config/pianobar/out &')      
            time.sleep(3)
            self.send_command_to_pianobar('s\r\n')
            time.sleep(2)
            self.send_command_to_pianobar('q')
          else:
            self.send_command_to_pianobar('s\r\n')
            self.send_command_to_pianobar('i\r\n')
            time.sleep(2)
       
       
          fifo = open(receivePath, "r")
          temp = fifo.read()
          fifo.close()
          #print("-------------------------")
          #print(temp)
          #print("-------------------------")
          list_stations = []
          for stationlist in re.finditer (r'\t.[^ns]\)[ ][^U].*',temp,re.M):
             list_stations.append(stationlist.group())
          tempStationList = list_stations
          for i, _ in enumerate(list_stations):
               tempStation = tempStationList[i][4:]
               if tempStation[:3] == " q ":
                  tempStationList[i] = '<b>' + tempStation[3:] + '</b>'        
               else:
                  tempStationList[i] = tempStation[3:]  
       
          tempStation = ''
          tempSong = ''
          tempRemainingTime = '--'
          tempTotalTime = '--'
       
          if self.PandoraRunning == True:    
             #Get selected station
             for stationinfo in re.finditer (r'STATION: .*',temp,re.M):
                 pass   
             if stationinfo:
                 tempStationName=str(stationinfo.group()[10:20]) 
             for i, _ in enumerate(tempStationList):
               if tempStationList[i].find(tempStationName) > 0:
                  tempStation = str(i)
       
             #Get Song Name
             tempSong = ''
             for songName in re.finditer (r'SONG:.*',temp,re.M):
                 pass   
             if songName:
                 tempSong=str(songName.group()[5:])  
       
             #Get the time
             tempTime = ''
             for times in re.finditer (r'TIME: -.*',temp,re.M):
                 pass   
             if times:
                 tempTime = times.group()[7:]

                 #Get time remaining till next song
                 tempRemainingTime = str(int(tempTime[0:2])*60 + int(tempTime[3:5]))
       
                 #Get total song time 
                 tempTotalTime = str(int(tempTime[6:8])*60 + int(tempTime[9:11]))

       
          return { 'stationList': tempStationList,
                   'station': tempStation,
                   'song': tempSong,
                   'remainingTime': tempRemainingTime,
                   'totalTime': tempTotalTime }
       
       except:
          return { 'stationList': tempStationList,
                   'station': tempStation,
                   'song': tempSong,
                   'remainingTime': tempRemainingTime,
                   'totalTime': tempTotalTime }
       

   def send_song_information(self):
      tempPandoraInformation = self.get_pandora_data()
      self.PandoraStationList = tempPandoraInformation['stationList']      
      self.PandoraDataQueue.put('PandoraStation,' + tempPandoraInformation['station']) 
      self.PandoraDataQueue.put('PandoraSong,' + tempPandoraInformation['song']) 
      self.PandoraDataQueue.put('PandoraSongTime,' + tempPandoraInformation['totalTime']) 
      self.PandoraDataQueue.put('PandoraRemainingTime,' + tempPandoraInformation['remainingTime'])       
      self.PandoraDataReadyEvent.set()
     
   #Send a command to pianobar 
   def send_command_to_pianobar(self,command):
      controlPath = '/home/pi/.config/pianobar/ctl'
      fifo = open(controlPath, "w")
      fifo.write(command)
      #print(command)
      fifo.close()
