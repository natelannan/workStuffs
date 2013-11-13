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


#Globals
cardNumber = 0
bitLength = 0
cardDataFormat = ['iClass = 254', 'Mifare = 254', 'Prox = 254', 'Seos = 254']
activeCard = 'Prox'
trailingZeros = 6
outFileName = "default.ini"
customFields = [(0,0),(0,0),(0,0),(0,0)]

def iniCreator(argv):
    # Usage
    if ((len(argv)< 6)or (len(argv)>7)):
        print "usage:  iniCreator.py <cardNumber> <bitLength> <cardDataFormat> <activeCard> <trailingZeros> <outFileName> [customFields]\n"
        print "CARD NUMBER:"
        print ("\tCard ID number that will be translated to PACS bits based on bit length and card data format.\n"
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
        print "\tExample Array:  ['iClassFormat = 42', 'MifareFormat = 4', 'ProxFormat = 254', 'SeosFormat = 100']\n"
        print "ACTIVE CARD:"
        print "\tCard type that is going to be used while testing."
        print "\tExample:  iClass\n"
        print "TRAILING ZEROS:"
        print "\tNumber of zeros added to PACS bits.  Valid input range is [0,9]\n"
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

    #Globals
    global cardNumber
    global bitLength
    global cardDataFormat
    global activeCard
    global trailingZeros
    global outFileName
    global customFields
    cardNumber = argv[0]
    bitLength = argv[1]
    cardDataFormat = argv[2]
    activeCard = argv[3]
    trailingZeros = argv[4]
    outFileName = argv[5]
    if (len(argv) == 7):
        customFields = argv[6]

    writeFile()


    
def writeFile():
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
    PACS = createPACS()
    file.write("[RawPACSBits]\n")
    file.write("PACSBits = "+PACS+"\n")
    file.close()


def createPACS():
    possibleFormats = {0   : raw,
                       1   : h01,
                       2   : h02,
                       4   : h04,
                       20  : h20,
                       42  : csn,
                       100 : corp,
                       255 : customer,
    }
                       

    filteredList = filter(lambda x: activeCard in x, cardDataFormat)
    if filteredList:
        formatValue = [int(s) for s in filteredList[0].split() if s.isdigit()]
    else:
        print "active card value not found."
        sys.exit(1)

    #if set to Auto, grab one of the other formats to create PACS bits.
    if formatValue[0]==254:
        keys = possibleFormats.keys()
        formatValue[0]=choice(keys)

    PACS = possibleFormats[formatValue[0]]()
    return PACS

def raw():
    print "raw"
    addedZeros = str(hex(cardNumber << trailingZeros).lstrip("0x") or '0')
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

def h01():
    print "h01"
    if len(str(cardNumber)) < 7:
        print "cardNumber is to short for H10301 Format.  No ini created"
        sys.exit (1) 
    CN = int(str(cardNumber)[len(str(cardNumber))-6:])
    FAC = int(str(cardNumber)[:len(str(cardNumber))-6])
    CN_bin = bin(CN)
    for x in range(0, 16-len(CN_bin)):
        CN_bin = '0'+CN_bin
    FAC_bin = bin(FAC)
    for x in range(0, 8-len(FAC_bin)):
        FAC_bin = '0'+FAC_bin
    precedingZeros = x+2  # add 1 for parity
    parity = CN_bin + '0'
    for x in range (0, trailingZeros):
        parity = parity+'0'
    PACS_bin = '0'+FAC_bin+parity
    print PACS_bin

    if (trailingZeros != 6) and (trailingZeros != 14):
        print ("Warning:  Number of trailing zeros will not generate a bit length that is a multiple of 8.\n"
               "Errors in calculating user's card number from PACS bits will occur.") 

    if trailingZeros <16:
        tzField = '0'+(hex(trailingZeros).lstrip("0x") or '0')
    elif trailingZeros == 16:
        tzField = '10'
    else:
        print "Invalid trailing zeros value"
        sys.exit(1)

    PACS = "%x" % int(PACS_bin, 2)
    for x in range (0,int(math.ceil(float(precedingZeros)/float(4)))):
        PACS = '0'+PACS
    
    return tzField+PACS

def h02():
    print "h02"
    #if len(str(cardNumber)) < 7:
    #    print "cardNumber is to short for H10301 Format.  No ini created"
    #    exit (1)
    #CN = int(str(cardNumber)[len(str(cardNumber))-6:])
    #FAC = int(str(cardNumber)[:len(str(cardNumber))-6])
    CN_bin = bin(cardNumber)
    for x in range(0, 35-len(CN_bin)):
        CN_bin = '0'+CN_bin
    precedingZeros = x+2      #1 for parity
    #FAC_bin = bin(FAC)
    #for x in range(0, 8-len(FAC_bin)):
    #    FAC_bin = '0'+FAC_bin
    parity = CN_bin + '0'
    for x in range (0, trailingZeros+1):
        CN_bin = CN_bin+'0'
    PACS_bin = '0'+CN_bin
    tzField = '0'+str(trailingZeros)
    PACS = "%x" % int(PACS_bin, 2)
    #for x in range (0,8-len(PACS)):
    #    PACS = '0'+PACS
    if (trailingZeros != 3) and (trailingZeros != 11):
        print ("Warning:  Number of trailing zeros will not generate a bit length that is a multiple of 8.\n"
               "Errors in calculating user's card number from PACS bits will occur.") 

    if trailingZeros <16:
        tzField = '0'+(hex(trailingZeros).lstrip("0x") or '0')
    elif trailingZeros == 16:
        tzField = '10'
    else:
        print "Invalid trailing zeros value"
        sys.exit(1)

    PACS = "%x" % int(PACS_bin, 2)
    for x in range (0,int(math.ceil(float(precedingZeros)/float(4)))):
        PACS = '0'+PACS
    
    return tzField+PACS

def h04():
    print "h04"
    return '0'

def h20():
    print "h20"
    return '0'

def csn():
    print "csn"
    return '0'

def corp():
    print "corp"
    return '0'

def customer():
    print "customer"
    return '0'

def bin(s):
    return str(s) if s<=1 else bin(s>>1) + str(s&1)
    
        
    
if __name__ == '__main__':
    iniCreator(sys.argv[1:])
