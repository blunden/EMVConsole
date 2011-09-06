from smartcard.util import *
from smartcard.CardType import AnyCardType
from smartcard.CardRequest import CardRequest
from smartcard.util import toHexString
from smartcard.Exceptions import CardRequestTimeoutException

from sys import stdin

from emvfunctions import *



def receiveCard():
	cardtype = AnyCardType()
	cardrequest = CardRequest(timeout = 120, cardType = cardtype)
	
	while (1):
		try:
			cardservice = cardrequest.waitforcard()
			
		except CardRequestTimeoutException:
			continue
			
			
		return cardservice.connection



