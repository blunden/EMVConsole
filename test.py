from smartcard.CardMonitoring import CardMonitor, CardObserver
from smartcard.CardConnection import CardConnection
from smartcard.util import *

from time import sleep
from sys import stdin, exc_info


# smart card commands
SELECT = [0x00, 0xA4, 0x04, 0x00]
GET_RESPONSE = [0x00, 0xC0, 0x00, 0x00]
READ_RECORD = [0x00, 0xB2]
VERIFY = [0x00, 0x20]

# emv commands
GET_PROCESSING_OPTIONS = [0x80, 0xA8]
GET_DATA = [0x80, 0xCA]

# p1 = 0x00, p2 = 0x80.... => offline pin
OFFLINE_PIN = [0x00, 0x80]

MAGIC_PIN = [0x08, 0x24]
PIN = [0x00, 0x00]
PIN_PADDING = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF]


# getters
DATA_ATC = [0x9F, 0x36, 0x05]
DATA_LAST_ONLINE = [0x9F, 0x13, 0x05]
DATA_PIN_TRIES = [0x9F, 0x17, 0x04]




MAGIC_PROCESSING = [0x00, 0x00, 0x83, 0x09, 0x9f, 0x38, 0x06, 0x9F, 0x1A, 0x02, 0x5F, 0x2A, 0x02]



# todo, fixa dynamisk langd

MAGIC_RECORD1 = [0x01, 0x0c, 0x43]






MAGIC_RECORD2 = [0x02, 0x0C, 0x52]






VISA_AID = [0xA0, 0x00, 0x00, 0x00, 0x03, 0x10, 0x10]
IPAY = [0x0E, 0x31, 0x50, 0x41, 0x59, 0x2E, 0x53, 0x59, 0x53, 0x2E, 0x44, 0x44, 0x46, 0x30, 0x31]
MAGIC_RECORD = [0x01, 0x14, 0x1D]


PROTOCOL = CardConnection.T0_protocol

class observer(CardObserver):

    def __init__(self):
        self.cards=[]

    def update(self, observable, (addedcards, removedcards)):
        for card in addedcards:
            if card not in self.cards:
                self.cards += [card]        	
                print "+Inserted: ", toHexString(card.atr)
                print "Try connect? (y/n)"
                a = stdin.readline()
                if a == "y\n":
                    print "Connecting..."
                    card.connection = card.createConnection()
                    card.connection.connect()
                    #response, sw1, sw2 = card.connection.transmit(SELECT + IPAY, PROTOCOL)
                    #print "Response: ", response, "status words: ", "%.2x %.2x" % (sw1, sw2)
                    #if (sw1 == 0x61):
                        #print "sw1 = 61, good."
                        #print "continue reading..."
                        #response, sw1, sw2 = card.connection.transmit(GET_RESPONSE + [sw2])
                        #print "Response: ", toHexString(response), "status words: ", "%.2x %.2x" % (sw1, sw2)
                        
                       # response, sw1, sw2 = card.connection.transmit(READ_RECORD + MAGIC_RECORD)
                        #print "Response: ", toHexString(response), "status words: ", "%.2x %.2x" % (sw1, sw2)
                        
                        # okay, now read VISA stuffs.
                    
                    response, sw1, sw2 = card.connection.transmit(SELECT + [len(VISA_AID)] + VISA_AID)
                    print "Response: ", toHexString(response), "status words: ", "%.2x %.2x" % (sw1, sw2)
                    
                    response, sw1, sw2 = card.connection.transmit(GET_RESPONSE + [sw2])
                    print "Response: ", toHexString(response), "status words: ", "%.2x %.2x" % (sw1, sw2)
                
                    response, sw1, sw2 = card.connection.transmit(READ_RECORD + MAGIC_RECORD1)
                    print "Response: ", toHexString(response), "status words: ", "%.2x %.2x" % (sw1, sw2)
                    
  
                    
                    s = ""
                    for letter in response[51:]:
                        s = s + chr(letter)
                        
                    print "Name: ", s
                    
                    print "Number: ", toHexString(response[31:39])
                               #print chr(response[39])
                               
                               
                   
                    print "Expires: ", toHexString([(response[40]<<4)+(response[41]>>4), (response[39]<<4)+(response[40]>>4)])
                        
                    print "Service code: ", toHexString([response[41]&0x0F, response[42]])
                        
                    #for record in [0, 1, 2, 3, 4, 5]:
                    #    for b1 in [0, 1, 2, 3, 4, 5]:
                    #        for b2 in [4, 12]:
                    #            
                    #            b = (b1<<4)+b2;
                    #            
                    #            #print "Trying: ", toHexString([b])
                    #            response, sw1, sw2 = card.connection.transmit(READ_RECORD + [record, b, 0x00])
                    #            if (sw1 == 0x6c):
                    #                response, sw1, sw2 = card.connection.transmit(READ_RECORD + [record, b, sw2])
                    #                print "Record: ", record, "File: ", toHexString([b]), "status: %.2x %.2x" % (sw1, sw2), "response: ", toHexString(response)
                    #            #print "Response: ", toHexString(response), "status words: ", "%.2x %.2x" % (sw1, sw2)
                        
                        
                        
                        
                    response, sw1, sw2 = card.connection.transmit(READ_RECORD + MAGIC_RECORD2)
                    print "Expires: 20" + toHexString([response[5]]) + "-" +toHexString([response[6]]) + "-" + toHexString([response[7]])
                    print "Created: 20" + toHexString([response[11]]) + "-" +toHexString([response[12]]) + "-" + toHexString([response[13]])
                    
                    #response, sw1, sw2 = card.connection.transmit(GET_PROCESSING_OPTIONS + MAGIC_PROCESSING)
                    #print "Response: ", toHexString(response), "status words: ", "%.2x %.2x" % (sw1, sw2)
                        
                    #response, sw1, sw2 = card.connection.transmit(GET_DATA + DATA_ATC)
                    #print "Response: ", toHexString(response), "status words: ", "%.2x %.2x" % (sw1, sw2)
                        
                    #response, sw1, sw2 = card.connection.transmit(GET_DATA + DATA_LAST_ONLINE)
                    #print "Response: ", toHexString(response), "status words: ", "%.2x %.2x" % (sw1, sw2)
                        
                    #response, sw1, sw2 = card.connection.transmit(GET_DATA + DATA_PIN_TRIES)
                    #print "Response: ", toHexString(response), "status words: ", "%.2x %.2x" % (sw1, sw2)
                        
                        #response, sw1, sw2 = card.connection.transmit(VERIFY + OFFLINE_PIN + MAGIC_PIN + PIN + PIN_PADDING)
                        #print "Response: ", toHexString(response), "status words: ", "%.2x %.2x" % (sw1, sw2)
                        
                        
                        
                        
                    
                    
        for card in removedcards:
            print "-Removed: ", toHexString( card.atr )
            if card in self.cards:
                self.cards.remove(card)

try:
    print "Insert or remove a smartcard in the system."
    print "This program will exit in 100 seconds"
    print ""
    cardmonitor = CardMonitor()
    cardobserver = observer()
    cardmonitor.addObserver(cardobserver)
    
    sleep(100)
    
    cardmonitor.deleteObserver(cardobserver)
    print "press Enter to continue"
    stdin.readline()

except:
	print exc_info()[0], ': ', exc_info()[1]
    