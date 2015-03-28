from connect import *
from emvfunctions import *
from smartfunctions import *
from constants import *
import getpass
from random import randint

print "[ ] Waiting for card..."

connection = receiveCard()
connection.connect()

print "[+] Found card: ", toHexString(connection.getATR())

func = EmvFunctions(connection)


applications = func.getApplications()


index = 1
for app in applications:
	print "[ ]", str(index) + ".", "".join(map(unichr, app[1])), "(" + toHexString(app[0]) + ")"
	index += 1
	
print "[?] Which application? ",
a = int(stdin.readline())

response, sw1, sw2 = func.selectApplication(applications[a-1][0])

# Attempt to read VISA card info if VISA card detected

if ("".join(map(chr, app[1])) == VISA_APPL_LABEL):
	print "Card information:"

	name, number, expires_short, created, expires_actual, sc = func.getVISACardinfo(VISA_AID)

	print "Name: ", name
	print "Number: ", number
	print "Expires (front):", expires_short
	print "Created: ", created
	print "Expires (actual): ", expires_actual
	print "Service code: ", sc


print "Pin tries left:", func.getPinRetriesLeft()


pdol = func.selectPaymentApplication(applications[a-1][0])


#print "PDOL: ", toHexString(pdol)

pdol_enc = COUNTRY_CODE_SWEDEN + CURRENCY_CODE_SWEDEN

afl = func.getAFL([0x83, 0x04] + pdol_enc)



#aip = func.getAIP([0x83, 0x04] + pdol_enc)

records = func.getRecords(afl)

records = []
for record in records:
	#print toHexString(record)
	func.readRecord(record)
	#print "Response: ", toHexString(response), "status words: ", "%.2x %.2x" % (sw1, sw2)                 


atcres = func.getATCCounter()
lastonlineres = func.getATCLastOnline()
print "  ATC count: ", toHexString(atcres)
print "Last online: ", toHexString(lastonlineres)


pin = getpass.getpass('Enter PIN: ')


p1 = (int(pin[0])<<4) + int(pin[1])
p2 = (int(pin[2])<<4) + int(pin[3])

pin = [p1, p2]


response, sw1, sw2 = func.verify(pin)
print "Response: ", toHexString(response), "status words: ", "%.2x %.2x" % (sw1, sw2)

if (sw1 == 0x90 and sw2 == 0x00):
	print "Pin verification succeeded!"
else:
	print "Pin verification failed!"
	print "Response: ", toHexString(response), "status words: ", "%.2x %.2x" % (sw1, sw2)
	exit()

print "Do you want to do a transaction? (y/n)"
proceed = stdin.readline()
if proceed == "y\n":

	amount = [0x00, 0x00, 0x00, 0x00, 0x10, 0x00]
	terminalcc = COUNTRY_CODE_SWEDEN
	tvr = [0x00, 0x80, 0x00, 0x00, 0x00]
	transactioncc = CURRENCY_CODE_SWEDEN

	# 2011-01-26
	date = [0x11, 0x01, 0x26]
	ttype = [0x00]
	unpredictable = [randint(0, 0xFF), randint(0, 0xFF), randint(0, 0xFF), randint(0, 0xFF)]

	print "Generating TC..."

	response, sw1, sw2 = func.generateTC(amount, terminalcc, tvr, transactioncc, date, ttype, unpredictable)

	print "Response: ", toHexString(response), "status words: ", "%.2x %.2x" % (sw1, sw2)
