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


pdol_enc = COUNTRY_CODE_SWEDEN + CURRENCY_CODE_SWEDEN

afl = func.getAFL([0x83, 0x04] + pdol_enc)

records = func.getRecords(afl)

records = []
for record in records:
	func.readRecord(record)


atcres = func.getATCCounter()
lastonlineres = func.getATCLastOnline()
print "  ATC count: ", toHexString(atcres)
print "Last online: ", toHexString(lastonlineres)

#----------------------------

print "[?] Specify desired ATC counter value (Example: 00 10): ",
input_str = stdin.readline().strip()
input_splitted = input_str.split(" ")

desired_atc = [int(input_splitted[0], 16), int(input_splitted[1], 16)]

print "[?] Print every n th value: ",
nth = int(stdin.readline())
counter = 0

print "Performing transactions until reaching desired value..."
while atcres < desired_atc:

	pdol = func.selectPaymentApplication(applications[a-1][0])

	afl = func.getAFL([0x83, 0x04] + pdol_enc)

	records = func.getRecords(afl)

	records = []
	for record in records:
		func.readRecord(record)

	atcres = func.getATCCounter()

	if (counter % nth == 0) or (atcres == desired_atc):
		print "  ATC count: ", toHexString(atcres)
	counter += 1

print "Desired ATC counter value reached!"
