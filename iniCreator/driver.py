#! /bin/python


from iniCreator import iniCreator


cardNumber = 1012345
bitLength = 26
cardDataFormat = ['iClassFormat = 42', 'MifareFormat = 0', 'ProxFormat = 1', 'SeosFormat = 100']
activeCard = 'Prox'
trailingZeros = 6
outFileName = 'foo.ini'
customFields = [(0,8),(8,8),(16,8),(24,8)]

args = [cardNumber, bitLength, cardDataFormat, activeCard, trailingZeros, outFileName, customFields]
#args = []
iniCreator(args)

#print customFields[1][0]
#print customFields[1][1]



