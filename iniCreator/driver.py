#! /bin/python


from iniCreator import iniCreator
import sys, re


cardNumber = '1012345'
bitLength = 36
cardDataFormat = ['iClassFormat = 42', 'MifareFormat = 0', 'ProxFormat = 254', 'SeosFormat = 100']
activeCard = 'Prox'
trailingZeros = 4
outFileName = 'foo.ini'
customFields = [(21,12),(1,20),(0,0),(0,0)]

args = [cardNumber, bitLength, cardDataFormat, activeCard, trailingZeros, outFileName, customFields]
#args = []
iniCreator(args)
pacsPattern = re.compile(r"PACSBits = (.*)")
buff = open(outFileName)
pacsLine = pacsPattern.search(buff.read())
if pacsLine:
  pacs =  pacsLine.group(1)
else:
  print "could not find PACS"
  sys.exit(1)

pacs = pacs[2:]
print pacs



