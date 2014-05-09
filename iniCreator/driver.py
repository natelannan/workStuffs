#! /bin/python


from iniCreator import iniCreator
import sys, re


cardNumber = '1012345'
bitLength = 26
cardDataFormat = ['iClassFormat = 0', 'MifareFormat = 0', 'ProxFormat = 0', 'SeosFormat = 0']
activeCard = 'Prox'
trailingZeros = 6
outFileName = 'foo.ini'
customFields = [(3,1),(2,1),(1,1),(0,1)]

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



