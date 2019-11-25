import logging


logging.basicConfig(filename='HCS.log', format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p',level=DEBUG)

  
logging.debug('This message should appear on the console')