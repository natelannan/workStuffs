#! /bin/python
'''
**************************************************************************
iniCreator.py



For questions or concerns, contact Nate Lannan (nlannan@lexmark.com) 

Copyright (c) 2013 Lexmark International, Inc.
All rights reserved
**************************************************************************
'''


import subprocess
import sys
import string
import math
from random import choice


class bitField:
	def __init__(self, name='blank', startbit=0, length = 0, decValue = 0, binValue = '0'):
		self.name = name		
		self.startbit = startbit
		self.length = length
		self.endbit = self.startbit+self.length-1
		self.decValue = decValue
		self.binValue = binValue
	        self.digits = len(str(2**self.length -1))
	def padZeros(self):
		for x in range(0, self.length-len(self.binValue)):
			self.binValue = '0'+self.binValue

def iniCreator(argv):
    if ((len(argv)< 6)or (len(argv)>7)):
        usage()

    writeFile(argv)


    
def writeFile(args):
    outFileName = args[5]
    cardDataFormat = args[2]
    if (len(args) == 7):
        customFields = args[6]
    else:
        customFields = [(0,0),(0,0),(0,0),(0,0)]
        
    file = open(outFileName, "w+")
    
    #write standard fields
    file.write("[CardTracking]\nISO14443A = 1\nISO14443B = 1\nICLASS15693 = 1\n")
    file.write("ISO15693 = 1\nSTM14443B = 1\nICODE1 = 1\nICODEEPC = 1\n\n")
    file.write("[BaudRates]\nISO14443ABaudRate = 1\nISO14443BBaudRate = 1\n\n")
    file.write("[076B_5121]\n632_ISO14443A = 123f_133f_1513_163f_1ba9_1cff\n")
    file.write("632_ISO14443B = 123f_1303_153f_163f_1bad_1c88\n")
    file.write("632_ISO15693  = 123f_1311_153f_163f_1be0_1cff\n")
    file.write("632_ICLASS    = 123f_1311_153f_163f_1be0_1cff\n\n")
    file.write("[076B_5321]\n632_ISO14443A = 123f_133f_1513_163f_1ba9_1cff\n")
    file.write("632_ISO14443B = 123f_1306_153F_163F_1bAC_1cff\n")
    file.write("632_ISO15693  = 123f_1321_153f_163f_1bD0_1ced\n")
    file.write("632_ICLASS    = 123f_1302_153f_163f_1be0_1ced\n\n")

    #write card data formats
    filteredList = filter(lambda x: 'iClass' in x, cardDataFormat)
    if filteredList:    
	file.write("[iClassOptions]\n")
	file.write(filteredList[0]+'\n\n')
    filteredList = filter(lambda x: 'Mifare' in x, cardDataFormat)
    if filteredList:
        file.write("[MifareOptions]\n")
        file.write(filteredList[0]+'\n\n')
    filteredList = filter(lambda x: 'Prox' in x, cardDataFormat)
    if filteredList:
        file.write("[ProximityOptions]\n")
        file.write(filteredList[0]+'\n\n')
    filteredList = filter(lambda x: 'Seos' in x, cardDataFormat)
    if filteredList:
        file.write("[SeosOptions]\n")
        file.write(filteredList[0]+'\n\n')


    #write custom fields
    #A
    file.write("[CustomProxFormat-A]\n")
    file.write("StartBit = "+str(hex(customFields[0][0]).lstrip("0x") or '0')+"\n")
    file.write("BitLength = "+str(hex(customFields[0][1]).lstrip("0x") or '0')+"\n")
    #B
    file.write("[CustomProxFormat-B]\n")
    file.write("StartBit = "+str(hex(customFields[1][0]).lstrip("0x") or '0')+"\n")
    file.write("BitLength = "+str(hex(customFields[1][1]).lstrip("0x") or '0')+"\n")
    #C
    file.write("[CustomProxFormat-C]\n")
    file.write("StartBit = "+str(hex(customFields[2][0]).lstrip("0x") or '0')+"\n")
    file.write("BitLength = "+str(hex(customFields[2][1]).lstrip("0x") or '0')+"\n")
    #D
    file.write("[CustomProxFormat-D]\n")
    file.write("StartBit = "+str(hex(customFields[3][0]).lstrip("0x") or '0')+"\n")
    file.write("BitLength = "+str(hex(customFields[3][1]).lstrip("0x") or '0')+"\n\n")
    
    
    #create raw pacs bits
    PACS = createPACS(args)
    file.write("[RawPACSBits]\n")
    file.write("PACSBits = "+PACS+"\n\n")

    #create CSN bits if in CSN mode
    CSNbits = createCSN(args)
    file.write("[RawUIDBits]\n")
    file.write("UIDBits = "+CSNbits+"\n")
    file.close()


def createPACS(args):
    trailingZeros = args[4]
    bitLength = args[1]
    activeCard = args[3]
    cardDataFormat = args[2]
    possibleFormats = {0   : raw,
                       1   : h01,
                       2   : h02,
                       4   : h04,
                       20  : h20,
                       100 : corp,
		       253 : csn,
                       255 : customer,
    }
                       

    filteredList = filter(lambda x: activeCard in x, cardDataFormat)
    if filteredList:
        formatValue = [int(s) for s in filteredList[0].split() if s.isdigit()]
    else:
        print "active card value not found."
        sys.exit(1)

    #if set to Auto, grab one of the other formats to create PACS bits.  if 36 bits use H10320 since it codes PACS in BCD
    if formatValue[0]==254:
	if bitLength == 36:
	    formatValue[0] = 20
	else:
	    formatValue[0] = 255
	    #if bitLength < 27:
		#    keys = [1]
	    #elif bitLength < 26 and bitLength <33:
		#    keys = [1,20]
	    #elif bitLength < 32 and bitLength < 35:
		#    keys = [1,20,100]
	    #else:
		#    keys = [1,20,100,2]
	    #formatValue[0]=choice(keys)
    
	    #if formatValue[0] != 0:
		#    if (bitLength+trailingZeros)%8 != 0:
		#	    trailingZeros = 8-(bitLength%8)
		#	    print "trailing zeros automatically corrected for random format used" 

    if formatValue[0] == 253:
	    PACS = '0000'
    else:
	    PACS = possibleFormats[formatValue[0]](args)
    return PACS

def createCSN(args):
    activeCard = args[3]
    cardDataFormat = args[2]

    filteredList = filter(lambda x: activeCard in x, cardDataFormat)
    if filteredList:
        formatValue = [int(s) for s in filteredList[0].split() if s.isdigit()]
    else:
        print "active card value not found."
        sys.exit(1)
    if formatValue[0] == 253:
        CSNbits = csn(args)
    else:
        CSNbits = '0000000000000000'
    return CSNbits

def raw(args):
    cardNumber = args[0]
    trailingZeros = args[4]
    addedZeros = str(hex(int(cardNumber) << trailingZeros).lstrip("0x") or '0')
    if (len(addedZeros) % 2) != 0:
        addedZeros = '0'+addedZeros
    if trailingZeros <16:
        tzField = '0'+(hex(trailingZeros).lstrip("0x") or '0')
    elif trailingZeros == 16:
        tzField = '10'
    else:
        print "Invalid trailing zeros value"
        sys.exit(1)
    PACS = tzField + addedZeros
    return PACS

def h01(args):
    cardNumber = args[0]
    trailingZeros = args[4]
    minDigits = 7
    if len(cardNumber) < minDigits:
        print "cardNumber is to short for H10301 Format.  No ini created"
        sys.exit (1) 

#def fac_cn_formats(CNdigits, CNlength, FAClength, cardNumber, trailingZeros, parityChange = False):
#   return [PACS_bin, noLeadingZeros, precedingZeros]
    [PACS_bin, noLeadingZeros, precedingZeros] = fac_cn_formats(6, 16, 8, cardNumber, trailingZeros = args[4] )

    #def calculateTZField(PACS_bin, trailingZeros):
    tzField = calculateTZField(PACS_bin,trailingZeros)

#def leadingZeros(PACS_bin, noLeadingZeros, precedingZeros):
    PACS = leadingZeros(PACS_bin, noLeadingZeros, precedingZeros)
   
    return tzField+PACS

def h02(args):
    cardNumber = args[0]
    trailingZeros = args[4]
    CN_bin = bin(int(cardNumber))
    parity = CN_bin + '0'
    for x in range (0, trailingZeros):
        parity = parity+'0'

    noLeadingZeros = parity

    for x in range(0, 35-len(CN_bin)):
        parity = '0'+parity
    precedingZeros = x+2      #1 for parity

    PACS_bin = '0'+parity

    #def calculateTZField(PACS_bin, trailingZeros):
    tzField = calculateTZField(PACS_bin,trailingZeros)

#def leadingZeros(PACS_bin, noLeadingZeros, precedingZeros):
    PACS = leadingZeros(PACS_bin, noLeadingZeros, precedingZeros)
   
    return tzField+PACS

def h04(args):
    cardNumber = args[0]
    trailingZeros = args[4]
    minDigits = 7
    if len(cardNumber) < minDigits:
        print "cardNumber is to short for H10304 Format.  No ini created"
        sys.exit (1) 

#def fac_cn_formats(CNdigits, CNlength, FAClength, cardNumber, trailingZeros, parityChange = False):
#   return [PACS_bin, noLeadingZeros, precedingZeros]
    [PACS_bin, noLeadingZeros, precedingZeros] = fac_cn_formats(6, 19, 16, cardNumber, trailingZeros = args[4])

    #def calculateTZField(PACS_bin, trailingZeros):
    tzField = calculateTZField(PACS_bin,trailingZeros)

#def leadingZeros(PACS_bin, noLeadingZeros, precedingZeros):
    PACS = leadingZeros(PACS_bin, noLeadingZeros, precedingZeros)
   
    return tzField+PACS

def h20(args):
    cardNumber = args[0]
    bitLength = args[1]
    trailingZeros = args[4]


    BCDdecimal =""
    ones = [0]*4
    parity = ''
    for char in cardNumber:
        binDec = bin(int(char))
	for x in range(0,4-len(binDec)):
		binDec = '0'+binDec
	ones[0] = ones[0] + binDec[1:4].count('1')
	ones[1] = ones[1] + (binDec[0]+binDec[2:4]).count('1')
	ones[2] = ones[2] + (binDec[0:2]+binDec[3]).count('1')
	ones[3] = ones[3] + binDec[0:3].count('1')
	BCDdecimal = BCDdecimal+binDec
    for x in range(0,4):
        if x == 1:
		parity = parity+'1' if ones[x] % 2 == 0 else parity+'0'
	else:
		parity = parity+'0' if ones[x] % 2 == 0 else parity+'1'
    parity = BCDdecimal + parity

    noLeadingZeros = parity    
    for x in range (0, trailingZeros):
        noLeadingZeros = noLeadingZeros+'0'

    flag = False
    for y in range(0, bitLength-len(parity)):
        noLeadingZeros = '0'+noLeadingZeros
	flag = True
    if(flag):
    	precedingZeros = y+1
    else:
	precedingZeros = 0


    PACS_bin = noLeadingZeros
    #def calculateTZField(PACS_bin, trailingZeros):
    tzField = calculateTZField(PACS_bin, trailingZeros)

#def leadingZeros(PACS_bin, noLeadingZeros, precedingZeros):
    PACS = leadingZeros(PACS_bin, noLeadingZeros, precedingZeros)
    
    return tzField+PACS

def csn(args):
    cardNumber = args[0]
    addedZeros = str(hex(int(cardNumber)).lstrip("0x") or '0')
    CSNbits = addedZeros
    return CSNbits

def corp(args):
    cardNumber = args[0]
    trailingZeros = args[4]
    minDigits = 9
    if len(cardNumber) < minDigits:
        print "cardNumber is to short for Corp1000 Format. No ini File Created."
	sys.exit(1)
#	for x in range(0,(9-len(str(cardNumber)))):
#		cardNumber = int('1'+str(cardNumber))
#	print "New Card Number is: " + str(cardNumber)
         

#def fac_cn_formats(CNdigits, CNlength, FAClength, cardNumber, trailingZeros, parityChange = False):
#   return [PACS_bin, noLeadingZeros, precedingZeros]
    [PACS_bin, noLeadingZeros, precedingZeros] = fac_cn_formats(8, 20, 12, cardNumber, trailingZeros = args[4], parityChange = True)


    #def calculateTZField(PACS_bin, trailingZeros):
    tzField = calculateTZField(PACS_bin,trailingZeros)


#def leadingZeros(PACS_bin, noLeadingZeros, precedingZeros):
    PACS = leadingZeros(PACS_bin, noLeadingZeros, precedingZeros)
    return tzField+PACS

def customer(args):
    cardNumber = args[0]
    bitLength = args[1]
    trailingZeros = args[4]
    if (len(args) == 7):
        customFields = args[6]
    else:
        customFields = [(0,0),(0,0),(0,0),(0,0)]

    bitFields = []
    for x in range(0,4):
        if customFields[x][1]!=0:
            if x==0:
                A = bitField('A',customFields[0][0],customFields[0][1])
                if (A.digits % 2 != 0):
                    A.digits = A.digits +1
                bitFields.append(A)
            elif x==1:
                B = bitField('B',customFields[1][0],customFields[1][1])
                if (B.digits % 2 != 0):
                    B.digits = B.digits +1
                bitFields.append(B)
            elif x==2:
                C = bitField('C',customFields[2][0],customFields[2][1])
                if (C.digits % 2 != 0):
                    C.digits = C.digits +1
                bitFields.append(C)
            else:
                D = bitField('D',customFields[3][0],customFields[3][1])
                if (D.digits % 2 != 0):
                    D.digits = D.digits +1
                bitFields.append(D)

    sortedFields = sorted(bitFields, key=lambda field: field.startbit)

    minDigits=0
    for x in sortedFields[:-1]:  #all but top most field which can be padded with zeros so all it needs to be is 1 digit
            minDigits = minDigits + x.digits
    minDigits = minDigits +1  #add one for last field.  This is the smallest value that cardNumber can have 

    if (len(cardNumber) < minDigits):
        print "Card number is not large enough for bit fields"
        sys.exit(1)
    

    tempFields = sortedFields[:]  #shallow copy
    indexAddition = 0 #make sure index is incremented when blank inserted in tempFields

    for x in range(0,len(sortedFields)-1):
	if sortedFields[x].endbit+1 != sortedFields[x+1].startbit:
		if sortedFields[x].endbit >= sortedFields[x+1].startbit:
			print "bit fields overlap.  We have issues!"
			sys.exit(1)
		else:	
			print "need a blank space between "+sortedFields[x].name+" and "+sortedFields[x+1].name
			blankStartbit  = sortedFields[x].endbit+1
			blankLength = (sortedFields[x+1].startbit) - blankStartbit
			blankBinValue = ''
			for y in range(0,blankLength):
				blankBinValue = '0'+blankBinValue
			tempFields.insert(x+1+indexAddition, bitField(startbit=blankStartbit, length=blankLength, binValue = blankBinValue))
			print "Inserted blank field starting at bit "+str(blankStartbit)+" of length "+str(blankLength)
			indexAddition = indexAddition+1
    sortedFields = tempFields

    maxDigits=0
    for x in sortedFields:
        maxDigits = maxDigits + x.digits


    cardNumWithZeros = cardNumber
    for x in range(0,maxDigits-len(cardNumber)):
        cardNumWithZeros = '0'+cardNumWithZeros


    nextField = 0
    if contains(bitFields, lambda x: x.name == 'A'):
	    A.decValue = int(cardNumWithZeros[nextField:A.digits])
	    nextField = nextField + A.digits
    if contains(bitFields, lambda x: x.name == 'B'):
	    B.decValue = int(cardNumWithZeros[nextField:nextField+B.digits])
	    nextField = nextField + B.digits
    if contains(bitFields, lambda x: x.name == 'C'):
	    C.decValue = int(cardNumWithZeros[nextField:nextField+C.digits])
	    nextField = nextField + C.digits
    if contains(bitFields, lambda x: x.name == 'D'):
	    D.decValue = int(cardNumWithZeros[nextField:nextField+D.digits])
	    nextField = nextField + D.digits



    for x in sortedFields:
        x.binValue=bin(x.decValue)
        x.padZeros()

    noLeadingZeros = ''
    for x in reversed(sortedFields):
	noLeadingZeros = noLeadingZeros + x.binValue
    for x in range(0, sortedFields[0].startbit):
        noLeadingZeros = noLeadingZeros+'0'
    binaryString = noLeadingZeros
    flag = False
    for x in range(0, bitLength-len(binaryString)):
	binaryString = '0'+binaryString
	flag = True
    if(flag):
    	    precedingZeros = x+1 
    else:
	precedingZeros = 0

    for x in range (0, trailingZeros):
        binaryString = binaryString+'0'
        noLeadingZeros = noLeadingZeros +'0'

    PACS_bin = binaryString

    #def calculateTZField(PACS_bin, trailingZeros):
    tzField = calculateTZField(PACS_bin,trailingZeros)

    #def leadingZeros(PACS_bin, noLeadingZeros, precedingZeros):
    PACS = leadingZeros(PACS_bin, noLeadingZeros, precedingZeros)
   
    return tzField+PACS

def bin(s):
    return str(s) if s<=1 else bin(s>>1) + str(s&1)

def leadingZeros(PACS_bin, noLeadingZeros, precedingZeros):
    numChars = (len(PACS_bin)+3)/4
    insertZeros = "%%0%dx" %numChars
    PACS = insertZeros % int(PACS_bin, 2)
    '''
    print PACS
    PACSbitPos = len(PACS_bin)%4
    if (PACSbitPos == 0):
	PACSbitPos = 4
    cardNumberBitPos = len(noLeadingZeros)%4
    if (cardNumberBitPos == 0):
	cardNumberBitPos = 4
    if (PACSbitPos - cardNumberBitPos > 0):
	for x in range (0,int(math.floor(float(precedingZeros)/float(4)))):
            PACS = '0'+PACS
    else:
    	for x in range (0,int(math.ceil(float(precedingZeros)/float(4)))):
            PACS = '0'+PACS
    print PACS
    '''
    return PACS
    
    
def calculateTZField(PACS_bin, trailingZeros):
    if (len(PACS_bin)%8 !=0):
	print ("Warning:  Number of trailing zeros will not generate a bit length that is a multiple of 8.\n"
               "Errors in calculating user's card number from PACS bits will occur.")

    if trailingZeros <16:
        tzField = '0'+(hex(trailingZeros).lstrip("0x") or '0')
    elif trailingZeros == 16:
        tzField = '10'
    else:
        print "Invalid trailing zeros value"
        sys.exit(1)
    return tzField

def fac_cn_formats(CNdigits, CNlength, FAClength, cardNumber, trailingZeros, parityChange = False):
    CN = int(cardNumber[len(cardNumber)-CNdigits:])
    FAC = int(cardNumber[:len(cardNumber)-CNdigits])
    CN_bin = bin(CN)
    for x in range(0, CNlength-len(CN_bin)):
        CN_bin = '0'+CN_bin
    parity = CN_bin + '0'
    FAC_bin = bin(FAC)
    noLeadingZeros = FAC_bin
    flag = False
    for x in range(0, FAClength-len(FAC_bin)):
        FAC_bin = '0'+FAC_bin
	flag = True
    if(flag):
    	if(parityChange):
    	    precedingZeros = x+3  # add 2 for parity
    	else:
   	    precedingZeros = x+2
    else:
	precedingZeros = 0

    for x in range (0, trailingZeros):
        parity = parity+'0'
    if (parityChange):
	PACS_bin = '00'+FAC_bin+parity
    else:
    	PACS_bin = '0'+FAC_bin+parity
    noLeadingZeros = noLeadingZeros+parity
    return [PACS_bin, noLeadingZeros, precedingZeros]

def contains (list, filter):
	for x in list:
		if filter (x):
			return True
	return False

def usage():
	print "usage:  iniCreator.py <cardNumber> <bitLength> <cardDataFormat> <activeCard> <trailingZeros> <outFileName> [customFields]\n"
        print "CARD NUMBER:"
        print ("\tA string of the card ID number that will be translated to PACS bits based on bit length and card data format.\n"
	       "\tThis is the ID you expect to see when the card is scanned.  For formats that include FAC and CN\n"
               "\tthe FAC should be included in this number.\n")
        print "BIT LENGTH:"
        print "\tValue of number of bits on card.  Standard formats include - "
        print "\t\tH10301 (26 bit)"
        print "\t\tH10302 (37 bit)"
        print "\t\tH10304 (37 bit)"
        print "\t\tH10320 (32 bit)"
        print "\t\tCorp 1000 (35 bit)\n"
        print "CARD DATA FORMAT:"
        print "\tArray of strings associated with card format and value."
        print "\tCard format valid input:"
        print "\t\tiClassFormat\n\t\tMifareFormat\n\t\tProxFormat\n\t\tSeosFormat"
        print "\tvalue valid input:"
        print "\t\t42 - Card Serial Number"
        print "\t\t0 - Wiegand Raw"
        print "\t\t1 - H10301"
        print "\t\t2 - H10302"
        print "\t\t4 - H10304"
        print "\t\t20 - H10320"
        print "\t\t100 - Corp 1000"
        print "\t\t254 - Auto"
        print "\t\t255 - Custom"
	print "\tExample Array:  ['ProxFormat = 0', 'iClassFormat = 255']"
        print "\tExample Array:  ['iClassFormat = 42', 'MifareFormat = 4',"
	print "\t'ProxFormat = 254', 'SeosFormat = 100']\n"
        print "ACTIVE CARD:"
        print "\tCard type that is going to be used while testing."
        print "\tExample:  iClass\n"
        print "TRAILING ZEROS:"
        print "\tNumber of zeros added to PACS bits.  Valid input range is [0,16]\n"
        print "OUTFILE NAME:"
        print "\tini file name to be created.  Example:  foo.ini\n"
        print "CUSTOM FIELDS:"
        print ("\toptional array to set CustomCardDataFormat Settings.\n"
               "\tThe 4 fields include A,B,C,D which have a start bit value\n"
               "\tand a length value.  These values should be in decimal and\n"
               "\tare passed as a 2 item array of the form (start, length).\n"
               "\tThe aguement should be passed in the following order [A,B,C,D].\n"
               "\tThe bit fields are little Endian (start with right most bit).\n"
               "\tIf a field's length value is set to 0 this field will be ignored.\n"
               "\tDecimal values will be converted to hex to send to 5427ck driver."
               "\n\tExample array:  [(0,8), (8,8), (16,8), (24, 8)]")
	sys.exit(0)
     
if __name__ == '__main__':
    iniCreator(sys.argv[1:])
