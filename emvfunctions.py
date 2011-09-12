from constants import *
from smartcard.util import toHexString
from smartfunctions import *
from tlvparser import *
from time import sleep

class EmvFunctions(SmartFunctions):
	
	def getRecords(self, afl):
		answers = []
		
		offset = 0
		while (offset+4 <= len(afl)):
			
			[b1, b2, b3, b4] = afl[offset:offset+4]
			for i in range(b2, b3+1):
				answers += [[i, (b1 | 4)]]
				
			offset += 4

		return answers
		
		
		
	def getRecordsForOffline(self, afl):
		answers = []
		
		offset = 0
		while (offset+4 <= len(afl)):
			
			[b1, b2, b3, b4] = afl[offset:offset+4]
			for i in range(b2, b2+b4):
				answers += [i, (b1<<3) | 4]
				
			offset += 4

		return answers
		

	def getPdol(self, id):
		return []
	
	def selectPaymentApplication(self, id):
		response, sw1, sw2 = self.selectApplication(id)
	
		return uglyParse(TAG_PDOL, response)

	
	def selectApplication(self, id):
		response, sw1, sw2 = self.select(id)
		
		#print "Response: ", toHexString(response), "status words: ", "%.2x %.2x" % (sw1, sw2)
		if (sw1 == 0x61):
			
			response, sw1, sw2 = self.getResponse(sw2)
			
			
			#print "Response: ", toHexString(response), "status words: ", "%.2x %.2x" % (sw1, sw2)
			
			
			while (sw1 == 0x69 and sw2 == 0x85):
				# damn card ain't initialized yet, bitch!
				sleep(0.1)
				response, sw1, sw2 = self.select(id)
				#print "Response: ", toHexString(response), "status words: ", "%.2x %.2x" % (sw1, sw2)
				response, sw1, sw2 = self.getResponse(sw2)
				#print "Response: ", toHexString(response), "status words: ", "%.2x %.2x" % (sw1, sw2)

			return response, sw1, sw2
				
		
	
	def getApplications(self):
		# Select IPAY-application, find out what is listed.
		#response, sw1, sw2 = self.connection.transmit(SELECT + [len(IPAY)] + IPAY)
		

		response, sw1, sw2 = self.selectApplication(IPAY)
		
		print toHexString(response)
		if ((sw1 == 0x90) and (sw2 == 0x00)):
			
			# Find SFI (0x88)
			firstPSE = uglyParse(TAG_SFI, response)

			print "[!] First PSE Record at: ", toHexString(firstPSE)
			
			SFI = [((firstPSE[0] << 3) | 4)]
			print "SFI: ", SFI
			#record #1, for some "apparant"
 			response, sw1, sw2 = self.readRecord([0x01] + SFI)
			
			
			offset = 0
			answers = []
			
			aid = uglyParse(TAG_AID, response, offset)
			al = uglyParse(TAG_AL, response, offset)
			
			while (len(aid) > 1):
				answers += [[aid, al]]
				offset += 1
				aid = uglyParse(TAG_AID, response, offset)
				al = uglyParse(TAG_AL, response, offset)
				
			return answers
				
		return []
		
	def getPinRetriesLeft(self):
		response, sw1, sw2 = self.getData(TAG_PIN_TRIES)
		if (sw1 == 0x90 and sw2 == 0x00):
			return uglyParse(TAG_PIN_TRIES, response)[0]
	
	def getATCCounter(self):
		response, sw1, sw2 = self.getData(TAG_ATC)
		return response[3:]
		
	def getATCLastOnline(self):
		response, sw1, sw2 =  self.getData(TAG_LAST_ONLINE)
		return response[3:]
		
	def getData(self, tag):
		# Find out length and get data
		#response, sw1, sw2 = card.connection.transmit(GET_DATA + DATA_LAST_ONLINE)
		
		response, sw1, sw2 = self.connection.transmit(GET_DATA + tag + [0x00])
		if (sw1 == 0x6c):
			response, sw1, sw2 = self.connection.transmit(GET_DATA + tag + [sw2])
			return response, sw1, sw2
		return response, sw1, sw2
		
		
	def getProcessingOptions(self, pdol = [0x83, 0x00]):
		response, sw1, sw2 = self.connection.transmit(GET_PROCESSING_OPTIONS + [0x00, 0x00] + [len(pdol)] + pdol)
		if (sw1 == 0x61):
			response, sw1, sw2 = self.getResponse(sw2)
			return response, sw1, sw2
			
	
	def getAIP(self, data):
		response, sw1, sw2 = self.getProcessingOptions(data)
		aip = response[2:4]
		return aip
	
	def getAFL(self, data):
		response, sw1, sw2 = self.getProcessingOptions(data)
		afl = response[4:]
		return afl
		
		
	def generateTC(self, amount, terminalcc, tvr, transactioncc, date, ttype, unpredictable):
		dol = amount + [0x00, 0x00, 0x00, 0x00, 0x00, 0x00] + terminalcc + tvr + transactioncc + date + ttype + unpredictable
		response, sw1, sw2 = self.connection.transmit(GENERATE_AC + [0x40, 0x00] + [len(dol)] + dol)
		if (sw1 == 0x61):
			response, sw1, sw2 = self.getResponse(sw2)
		
		return response, sw1, sw2

	def getVISACardinfo(self, aid):
		response, sw1, sw2 = self.select(VISA_AID)
		response, sw1, sw2 = self.getResponse(sw2)
		response, sw1, sw2 = self.readRecord(VISA1)

		name = ""
		for letter in response[51:]:
			name = name + chr(letter)

		number = toHexString(response[31:39])
		expires_short = toHexString([(response[40]<<4)+(response[41]>>4), (response[39]<<4)+(response[40]>>4)])
		sc = toHexString([response[41]&0x0f, response[42]])

		response, sw1, sw2 = self.readRecord(VISA2)

		created = "20" + toHexString([response[11]]) + "-" +toHexString([response[12]]) + "-" + toHexString([response[13]])
		expires_actual = "20" + toHexString([response[5]]) + "-" +toHexString([response[6]]) + "-" + toHexString([response[7]])

		return name, number, expires_short, created, expires_actual, sc 
