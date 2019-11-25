import wap
import re
#import serial
import time
#import urllib
#import urllib2
import elementtree.ElementTree as ET
import sys
from time import gmtime, strftime

class wolframalpha(object):

   def get_answer_from_wolfram_alpha(self,command):

      #url = 'http://preview.wolframalpha.com/api/v1/query.jsp'
      #url = 'http://preview.wolframalpha.com/api/v1/validatequery.jsp'
      #url = 'http://api.wolframalpha.com/v1/query.jsp'
      #url = 'http://api.wolframalpha.com/v1/validatequery.jsp'

      server = 'http://api.wolframalpha.com/v1/query.jsp'
      appid = 'PGRY4P-6AGPPP4TXE'

      scantimeout = '3.0'
      podtimeout = '4.0'
      formattimeout = '8.0'
      async = 'False'

      waeq = wap.WolframAlphaEngine(appid, server)
      waeq.ScanTimeout = scantimeout
      waeq.PodTimeout = podtimeout
      waeq.FormatTimeout = formattimeout
      waeq.Async = async
      waeq.AddPodFormat = 'plaintext'

      query = waeq.CreateQuery(command)
      result = waeq.PerformQuery(query)
      waeqr = wap.WolframAlphaQueryResult(result)
      jsonresult = waeqr.JsonResult()
      xmlresult = waeqr.XmlResult

      filename =  'WolframAlphaFiles\\' + strftime("%Y-%m-%d %H:%M:%S", gmtime()).replace(':','') + '.xml'
      text_file = open(filename, "w")
      text_file.write(xmlresult)
      text_file.close()

      try:
          xmldoc = ET.parse(filename)
          root = xmldoc.getroot()
          #print secondPod
          secondPod = root.findall('pod')[1]
          #print secondPod.get('title')
          #print " is: "
          firstSubPod = secondPod.findall('subpod')[0]
          firstPlainText = firstSubPod.find('plaintext')
          initialResult = firstPlainText.text.replace('|',' is ')
          initialResult = initialResult.replace('\n', ',')	  
          print initialResult
          return initialResult
      except:
      	  with open("WolframAlphaIssues.txt","a") as myFile:
              myFile.write("File caused exeption: " + filename + "\r")
          print "WolframAlpha couldn't figure it out. Sent to: " + filename 
          return "I have no clue, try Google."
