from constants import *

class SmartFunctions:
	def __init__(self, connection):
		self.connection = connection
        
	def readRecord(self, record):
		response, sw1, sw2 = self.connection.transmit(READ_RECORD + record + [0x00])
		if (sw1 == 0x6c):
			response, sw1, sw2 = self.connection.transmit(READ_RECORD + record + [sw2])
			return response, sw1, sw2
		return response, sw1, sw2
		
		
	def select(self, application):
		return self.connection.transmit(SELECT + [len(application)] + application)
		
	def getResponse(self, bytes):
		return self.connection.transmit(GET_RESPONSE + [bytes])	
		
		
	def verify(self, pin):
		return self.connection.transmit(VERIFY + [0x00] + [0x80] + [0x08] + [0x24] + pin + [0xff, 0xff, 0xff, 0xff, 0xff])