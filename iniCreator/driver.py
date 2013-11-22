#! /bin/python


from iniCreator import iniCreator


cardNumber = 1012345
bitLength = 24
cardDataFormat = ['iClassFormat = 42', 'MifareFormat = 0', 'ProxFormat = 255', 'SeosFormat = 100']
activeCard = 'Prox'
trailingZeros = 0
outFileName = 'foo.ini'
customFields = [(16,8),(0,16),(0,0),(0,0)]

args = [cardNumber, bitLength, cardDataFormat, activeCard, trailingZeros, outFileName, customFields]
#args = []
iniCreator(args)

#print customFields[1][0]
#print customFields[1][1]



