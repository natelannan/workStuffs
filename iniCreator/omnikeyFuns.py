#! /bin/python

import subprocess
import shlex
import re
import telnetlib
from time import sleep
from iniCreator import *
import globals




def getApps():
    subprocess.call("smbclient -U autouser " + globals.WINSHARE + " -c \"get nlannan\\5427ckApps.zip\" Fn4WNus2T", shell=True)
    subprocess.call("unzip nlannan\\\\5427ckApps.zip", shell=True)
    subprocess.call("rm nlannan\\\\5427ckApps.zip", shell=True)

def installApps():
    subprocess.call (globals.sendtcp+" " + globals.ipAddress +" "+ "5427ckApps/cardslotsim.fls", shell=True)
    subprocess.call (globals.sendtcp+" " + globals.ipAddress +" "+ "5427ckApps/readertest.fls", shell=True)
    subprocess.call (globals.sendtcp+" " + globals.ipAddress +" "+ "5427ckApps/omnikey5427ck.fls", shell=True)
    sleep(10)

def checkApps():
    curlSessionCmd = "curl http://"+globals.ipAddress+"/cgi-bin/dynamic/printer/config/reports/MenusPage.html"
    curlSessionArgs= shlex.split(curlSessionCmd)
    curlSession, err  = subprocess.Popen(curlSessionArgs,stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    if globals.printerFamily == 'HS':
        cardslotPattern = re.compile(r".*Card Slot Simulation.*")
        omnikeyPattern = re.compile(r".*Omnikey 5427ck Reader Driver.*")
        readerPattern = re.compile(r".*Reader Test.*")
    else:
        cardslotPattern = re.compile(r".*Card&nbsp;Slot&nbsp;Simulation.*")
        omnikeyPattern = re.compile(r".*Omnikey&nbsp;5427ck&nbsp;Reader&nbsp;Driver.*")
        readerPattern = re.compile(r".*Reader&nbsp;Test.*")
        
    cardslotLine = cardslotPattern.search(curlSession)
    if cardslotLine:
        omnikeyLine = omnikeyPattern.search(curlSession)
        if omnikeyLine:
            readerLine = readerPattern.search(curlSession)
            if readerLine:
                print "Apps successfully installed on printer."
                return True
            else:
                print "readertest.fls failed to install on device."
                return False
        else:
            print "omnikey5427ck.fls failed to install on device."
            return False
    else:
        print "cardslotsim.fls failed to install on device."
        return False

def runTest(outFileStream, outSwapped=False, outInHex=False, noIni=False, failCase=False):
    compare = globals.cardNumber
    inHexidecimal = 'false'
    outputSwap = 'false'
    isRaw = False
    
    if (globals.activeCard + 'Format = 0') in globals.cardDataFormat:
        isRaw = True


    rawHex = str(hex(int(compare)).lstrip("0x") or '0').upper()
    firstNibble = int(rawHex[0],16) # decimal value of first nibble
    if firstNibble > 7:
        bitsInNibble = 4
    elif (firstNibble > 3) and (firstNibble < 8):
        bitsInNibble = 3
    elif (firstNibble > 1) and (firstNibble < 4):
        bitsInNibble = 2
    elif (firstNibble == 1) or (firstNibble == 0):
        bitsInNibble = firstNibble
    else:
        print "Problem calculating Hex value for Card Number"
        sys.exit(1)
    numBits = (len(rawHex)-1)*4 + bitsInNibble
    paddedBytes = (numBits+globals.trailingZeros+7)/8 #number of bytes with trailing zeros
    dataBits = 8*paddedBytes - globals.trailingZeros #number of bits for PACS data
    PACSBytes = (dataBits+7)/8

    numChars = 2*PACSBytes - len(rawHex) #number of nibbles needed
    for x in range (0, numChars):
        rawHex = '0'+rawHex
        
    if outInHex:
        inHexidecimal = 'true'
        if isRaw:
            compare = rawHex
                    
    if outSwapped:
        compare = rawHex
        compare = "".join(reversed([compare[i:i+2] for i in range(0, len(compare), 2)]))
        if outInHex == False:
            compare = str(int(compare, 16))
        outputSwap = 'true'

    if noIni == False:
        loadIni()
    if outInHex or outSwapped:
        setSettings(swap=outputSwap, inHex=inHexidecimal)
    deleteEsfLog()
    swipeCard()
    
    userID = parseEsfLog()

    if failCase == False:
        if userID == compare:
            print "cardNumber = \t"+ compare+"\nuserID = \t"+userID+"\n\nPASS"
            outFileStream.write("cardNumber = \t"+ compare+"\nuserID = \t"+userID+"\n\nPASS\n")
        else:
            print "cardNumber = \t"+ compare+"\nuserID = \t"+userID+"\n\nFAIL"
            outFileStream.write("cardNumber = \t"+ compare+"\nuserID = \t"+userID+"\n\nFAIL\n")
            #sys.exit(1)
    else:
        if userID == compare:
            print "cardNumber = \t"+ compare+"\nuserID = \t"+userID+"\n\nFAIL"
            outFileStream.write("cardNumber = \t"+ compare+"\nuserID = \t"+userID+"\n\nFAIL\n")
        else:
            print "cardNumber = \t"+ compare+"\nuserID = \t"+userID+"\n\nPASS"
            outFileStream.write("cardNumber = \t"+ compare+"\nuserID = \t"+userID+"\n\nPASS\n")


def loadIni():
    iniArgs = [globals.cardNumber, globals.bitLength, globals.cardDataFormat, globals.activeCard, globals.trailingZeros, globals.outFileName, globals.customFields]
    iniCreator(iniArgs)

    sessionValue = getCurlSession()
    startCurlSession(sessionValue)

    curlSendCmd = "curl -H \"Cookie: JSESSIONID="+sessionValue+"\" -F settings.inifile=@"+globals.outFileName+" http://" \
        +globals.ipAddress+"/cgi-bin/direct/printer/prtappauth/admin/configureokservlet"
    curlSendArgs= shlex.split(curlSendCmd)
    curlSend, err = subprocess.Popen(curlSendArgs, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()

def loadPreExistIni(iniFileName):

    sessionValue = getCurlSession()
    startCurlSession(sessionValue)

    curlSendCmd = "curl -H \"Cookie: JSESSIONID="+sessionValue+"\" -F settings.inifile=@"+iniFileName+" http://" \
        +globals.ipAddress+"/cgi-bin/direct/printer/prtappauth/admin/configureokservlet"
    curlSendArgs= shlex.split(curlSendCmd)
    curlSend, err = subprocess.Popen(curlSendArgs, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()

def getCurlSession():
    if (globals.printerFamily == 'HS'):
        curlSessionCmd = "curl -D - \"http://"+globals.ipAddress+"/cgi-bin/direct/printer/prtappauth/admin/adminservlet\""
    elif (globals.printerFamily == 'WC'):
        curlSessionCmd = "curl -D - \"http://"+globals.ipAddress+"/cgi-bin/direct/printer/prtappauth/admin/adminservlet" \
                         "?SelectedAppsNames=omnikey5427ckdriver\""
    else:
        print "Printer Family not recognized."
        sys.exit(1)
    curlSessionArgs= shlex.split(curlSessionCmd)
    curlSession, err  = subprocess.Popen(curlSessionArgs,stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    cookiePattern = re.compile(r"Set-Cookie: JSESSIONID=([^;]*).*")
    cookieLine = cookiePattern.search(curlSession)
    if cookieLine:
        return cookieLine.group(1)
    else:
        print "could not find Cookie for session start"
        sys.exit(1)

def startCurlSession(sessionValue):
    curlStartCmd = "curl \'http://"+globals.ipAddress+"/cgi-bin/direct/printer/prtappauth/admin/appservlet?" \
                   "SelectedAppsNames=omnikey5427ckdriver\' -H \'Referer: http://"+globals.ipAddress+ \
                   "/cgi-bin/direct/printer/prtappauth/admin/\' -H \'Cookie: JSESSIONID="+sessionValue+ \
                   "\' -H \'Connection: keep-alive\'"
    curlStartArgs=shlex.split(curlStartCmd)
    curlStart, err = subprocess.Popen(curlStartArgs, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    

def setSettings(swap='false', inHex='false', beep='false', iClass='254', mifare='254', prox='254', seos='254'):
    sessionValue = getCurlSession()
    startCurlSession(sessionValue)
    
    curlSessionCmd = "curl http://"+globals.ipAddress+"/cgi-bin/dynamic/printer/config/reports/MenusPage.html"
    curlSessionArgs= shlex.split(curlSessionCmd)
    curlSession, err  = subprocess.Popen(curlSessionArgs,stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    if globals.printerFamily == 'HS':
        omnikeyPattern = re.compile(r".*Omnikey 5427ck Reader Driver.*=  (.*) <.*")
    else:
        omnikeyPattern = re.compile(r".*Omnikey&nbsp;5427ck&nbsp;Reader&nbsp;Driver.*=  (.*) <.*")
    omnikeyLine = omnikeyPattern.search(curlSession)
    omnikeyVersion = omnikeyLine.group(1)

    writeUCF(omnikeyVersion, swap, inHex, beep, iClass, mifare, prox, seos)
    sendUCF()

    

def writeUCF(version, dataswap, datahex, beep, iClass, mifare, prox, seos):
    file = open("omnikey5427.ucf", "w+")
    file.write("esf.version.omnikey5427ckdriver "+version+"\n")
    file.write("esf.omnikey5427ckdriver.settings.dataswap \""+dataswap+"\"\n")
    file.write("esf.omnikey5427ckdriver.settings.datahex \""+datahex+"\"\n")
    file.write("esf.omnikey5427ckdriver.settings.beep \""+beep+"\"\n")
    file.write("esf.omnikey5427ckdriver.settings.iClassformat \""+iClass+"\"\n")
    file.write("esf.omnikey5427ckdriver.settings.miFareformat \""+mifare+"\"\n")
    file.write("esf.omnikey5427ckdriver.settings.proxformat \""+prox+"\"\n")
    file.write("esf.omnikey5427ckdriver.settings.seosformat \""+seos+"\"\n")
    file.close()

def sendUCF():
    curlSendCmd = "curl -F \"input_file=@omnikey5427.ucf\" http://"+globals.ipAddress+"/cgi-bin/dynamic/printer/config/secure/importsettings.html"
    curlSendArgs= shlex.split(curlSendCmd)
    curlSend, err  = subprocess.Popen(curlSendArgs,stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()

    
    

def deleteEsfLog():
    curlDebugCmd = "curl \'http://"+globals.ipAddress+"/cgi-bin/direct/printer/prtappse/semenu?loglevel=debug&page=setloglevel\'"
    curlDebugArgs = shlex.split(curlDebugCmd)
    curlDebug, err = subprocess.Popen(curlDebugArgs, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    curlClearCmd = "curl \'http://"+globals.ipAddress+"/cgi-bin/direct/printer/prtappse/semenu?clearlogconfirmation=Yes&page=clearlog\'"
    curlClearArgs = shlex.split(curlClearCmd)
    curlClear, err = subprocess.Popen(curlClearArgs, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()

def swipeCard():
    tn =telnetlib.Telnet(globals.ipAddress, globals.telnetPort)
    tn.write('i')
    sleep(4)
    tn.write('o')
    sleep(6)
    tn.close()

def parseEsfLog():
    esfLog = "http://"+globals.ipAddress+"/cgi-bin/script/printer/prtapplog"
    userID = parser(esfLog)
    return userID

def parser (searchFile):
    pattern  = re.compile(r"readertest - Data: (.*)")
    log, err = subprocess.Popen(['curl', searchFile], stdout=subprocess.PIPE).communicate()
    userIDline = pattern.search(log)
    if userIDline:
        userID = userIDline.group(1)
    else:
        print "No ID value found in log."
        userID = '0'
    return userID

def successCases(outFileStream):
    
    #RAW
    print "\n\nRaw Format"
    outFileStream.write("\n\nRaw Format\n")
    globals.cardDataFormat = ['iClassFormat = 0', 'MifareFormat = 0', 'ProxFormat = 0', 'SeosFormat = 0']
    globals.cardNumber = '1012345'
    globals.trailingZeros = 0
    print "\n\nNormal Case:"
    outFileStream.write("\n\nNormal Case:\n")
    runTest(outFileStream)
    print "\n\nOutput in Hex:"
    outFileStream.write("\n\nOutput in Hex:\n")
    runTest(outFileStream, outInHex=True)
    print "\n\nOutput swapped:"
    outFileStream.write("\n\nOutput swapped:\n")
    runTest(outFileStream, outSwapped=True)
    print "\n\nOutput in Hex and swapped:"
    outFileStream.write("\n\nOutput in Hex and swapped:\n")
    runTest(outFileStream, outInHex=True, outSwapped=True)
    print "\n\nLarge Value (Max value depedent on system memory):"
    outFileStream.write("\n\nLarge Value (Max value depedent on system memory):\n")
    globals.cardNumber = str((2**2008)-1) 
    runTest(outFileStream)
    print "\n\nMin Value:"
    outFileStream.write("\n\nMin Value:\n")
    globals.cardNumber = '0'
    runTest(outFileStream)
                      
    
    #H10301
    print "\n\nH10301"
    outFileStream.write("\n\nH10301\n")
    globals.bitLength = 26
    globals.trailingZeros = 6
    globals.cardDataFormat = ['iClassFormat = 1', 'MifareFormat = 1', 'ProxFormat = 1', 'SeosFormat = 1']
    globals.cardNumber = '1012345'
    print "Normal Case:"
    outFileStream.write("Normal Case:\n")
    runTest(outFileStream)
    print "\n\nOutput in Hex:"
    outFileStream.write("\n\nOutput in Hex:\n")
    runTest(outFileStream, outInHex=True)
    print "\n\nOutput swapped:"
    outFileStream.write("\n\nOutput swapped:\n")
    runTest(outFileStream, outSwapped=True)
    print "\n\nOutput in Hex and swapped:"
    outFileStream.write("\n\nOutput in Hex and swapped:\n")
    runTest(outFileStream, outInHex=True, outSwapped=True)
    print "\n\nMax Value:"
    outFileStream.write("\n\nMax Value:\n")
    globals.cardNumber = '255065535'
    runTest(outFileStream)
    print "\n\nMin Value:"
    outFileStream.write("\n\nMin Value:\n")
    globals.cardNumber = '0000000'
    runTest(outFileStream)
    
    #H10302
    print "\n\nH10302"
    outFileStream.write("\n\nH10302\n")
    globals.bitLength = 37
    globals.trailingZeros = 3
    globals.cardDataFormat = ['iClassFormat = 2', 'MifareFormat = 2', 'ProxFormat = 2', 'SeosFormat = 2']
    globals.cardNumber = '1012345'
    print "Normal Case:"
    outFileStream.write("Normal Case:\n")
    runTest(outFileStream)
    print "\n\nOutput in Hex:"
    outFileStream.write("\n\nOutput in Hex:\n")
    runTest(outFileStream, outInHex=True)
    print "\n\nOutput swapped:"
    outFileStream.write("\n\nOutput swapped:\n")
    runTest(outFileStream, outSwapped=True)
    print "\n\nOutput in Hex and swapped:"
    outFileStream.write("\n\nOutput in Hex and swapped:\n")
    runTest(outFileStream, outInHex=True, outSwapped=True)
    print "\n\nMax Value:"
    outFileStream.write("\n\nMax Value:\n")
    globals.cardNumber = '34359738367'
    runTest(outFileStream)
    print "\n\nMin Value:"
    outFileStream.write("\n\nMin Value:\n")
    globals.cardNumber = '0'
    runTest(outFileStream)

    #H10304
    print "\n\nH10304"
    outFileStream.write("\n\nH10304\n")
    globals.bitLength = 37
    globals.trailingZeros = 3
    globals.cardDataFormat = ['iClassFormat = 4', 'MifareFormat = 4', 'ProxFormat = 4', 'SeosFormat = 4']
    globals.cardNumber = '1012345'
    print "Normal Case:"
    outFileStream.write("Normal Case:\n")
    runTest(outFileStream)
    print "\n\nOutput in Hex:"
    outFileStream.write("\n\nOutput in Hex:\n")
    runTest(outFileStream, outInHex=True)
    print "\n\nOutput swapped:"
    outFileStream.write("\n\nOutput swapped:\n")
    runTest(outFileStream, outSwapped=True)
    print "\n\nOutput in Hex and swapped:"
    outFileStream.write("\n\nOutput in Hex and swapped:\n")
    runTest(outFileStream, outInHex=True, outSwapped=True)
    print "\n\nMax Value:"
    outFileStream.write("\n\nMax Value:\n")
    globals.cardNumber = '65535524287' 
    runTest(outFileStream)
    print "\n\nMin Value:"
    outFileStream.write("\n\nMin Value:\n")
    globals.cardNumber = '0000000'
    runTest(outFileStream)

   
    
    #H10320
    print "\n\nH10320"
    outFileStream.write("\n\nH10320\n")
    globals.bitLength = 36
    globals.trailingZeros = 4
    globals.cardDataFormat = ['iClassFormat = 20', 'MifareFormat = 20', 'ProxFormat = 20', 'SeosFormat = 20']
    globals.cardNumber = '1012345'
    
    print "Normal Case:"
    outFileStream.write("Normal Case:\n")
    runTest(outFileStream)
    print "\n\nOutput in Hex:"
    outFileStream.write("\n\nOutput in Hex:\n")
    runTest(outFileStream, outInHex=True)
    print "\n\nOutput swapped:"
    outFileStream.write("\n\nOutput swapped:\n")
    runTest(outFileStream, outSwapped=True)
    print "\n\nOutput in Hex and swapped:"
    outFileStream.write("\n\nOutput in Hex and swapped:\n")
    runTest(outFileStream, outInHex=True, outSwapped=True)
    print "\n\nMax Value:"
    outFileStream.write("\n\nMax Value:\n")
    globals.cardNumber = '99999999'
    runTest(outFileStream)
    print "\n\nMin Value:"
    outFileStream.write("\n\nMin Value:\n")
    globals.cardNumber = '0'
    runTest(outFileStream)

    #Corp 1000
    print "\n\nCorp 1000"
    outFileStream.write("\n\nCorp 1000\n")
    globals.bitLength = 35
    globals.trailingZeros = 5
    globals.cardDataFormat = ['iClassFormat = 100', 'MifareFormat = 100', 'ProxFormat = 100', 'SeosFormat = 100']
    globals.cardNumber = '100012345'
    print "Normal Case:"
    outFileStream.write("Normal Case:\n")
    runTest(outFileStream)
    print "\n\nOutput in Hex:"
    outFileStream.write("\n\nOutput in Hex:\n")
    runTest(outFileStream, outInHex=True)
    print "\n\nOutput swapped:"
    outFileStream.write("\n\nOutput swapped:\n")
    runTest(outFileStream, outSwapped=True)
    print "\n\nOutput in Hex and swapped:"
    outFileStream.write("\n\nOutput in Hex and swapped:\n")
    runTest(outFileStream, outInHex=True, outSwapped=True)
    print "\n\nMax Value:"
    outFileStream.write("\n\nMax Value:\n")
    globals.cardNumber = '409501048575'
    runTest(outFileStream)
    print "\n\nMin Value:"
    outFileStream.write("\n\nMin Value:\n")
    globals.cardNumber = '000000000'
    runTest(outFileStream)
    
    #CSN
    print "\n\nCSN"
    outFileStream.write("\n\nCSN\n")
    globals.cardDataFormat = ['iClassFormat = 253 ', 'MifareFormat = 253', 'ProxFormat = 253', 'SeosFormat = 253']
    print "Normal Case:"
    outFileStream.write("Normal Case:\n")
    globals.cardNumber = '1012345'
    runTest(outFileStream)
    globals.cardNumber = str((2**63)-1)
    print "\n\nMax Value:"
    outFileStream.write("\n\nMax Value:\n")
    runTest(outFileStream)
    print "\n\nMin Value:"
    outFileStream.write("\n\nMin Value:\n")
    globals.cardNumber = '0'
    runTest(outFileStream)
    
    #Auto
    print "\n\nAuto Mode"
    outFileStream.write("\n\nAuto Mode\n")
    globals.cardDataFormat = ['iClassFormat = 254', 'MifareFormat = 254', 'ProxFormat = 254', 'SeosFormat = 254']
    globals.cardNumber = '1012345'
    globals.bitLength=26
    globals.trailingZeros = 6
    globals.customFields = [(17,8),(1,16),(0,0),(0,0)]
    print "\n\nH10301 Format:"
    outFileStream.write("\n\nH10301 Format:\n")
    runTest(outFileStream)
    print "\n\nOutput in Hex:"
    outFileStream.write("\n\nOutput in Hex:\n")
    runTest(outFileStream, outInHex=True)
    print "\n\nOutput swapped:"
    outFileStream.write("\n\nOutput swapped:\n")
    runTest(outFileStream, outSwapped=True)
    print "\n\nOutput in Hex and swapped:"
    outFileStream.write("\n\nOutput in Hex and swapped:\n")
    runTest (outFileStream, outInHex=True, outSwapped=True)
    
    globals.bitLength=37
    globals.trailingZeros = 3
    globals.customFields = [(1,35),(0,0),(0,0),(0,0)]
    print "\n\nH10302 Format:"
    outFileStream.write("\n\nH10302 Format:\n")
    runTest(outFileStream)
    print "\n\nOutput in Hex:"
    outFileStream.write("\n\nOutput in Hex:\n")
    runTest(outFileStream, outInHex=True)
    print "\n\nOutput swapped:"
    outFileStream.write("\n\nOutput swapped:\n")
    runTest(outFileStream, outSwapped=True)
    print "\n\nOutput in Hex and swapped:"
    outFileStream.write("\n\nOutput in Hex and swapped:\n")
    runTest (outFileStream, outInHex=True, outSwapped=True)
    
    globals.cardNumber = '100012345'    
    globals.bitLength=35
    globals.trailingZeros = 5
    globals.customFields = [(21,12),(1,20),(0,0),(0,0)]
    print "\n\nCorp 1000 Format:"
    outFileStream.write("\n\nCorp 1000 Format:\n")
    runTest(outFileStream)
    print "\n\nOutput in Hex:"
    outFileStream.write("\n\nOutput in Hex:\n")
    runTest(outFileStream, outInHex=True)
    print "\n\nOutput swapped:"
    outFileStream.write("\n\nOutput swapped:\n")
    runTest(outFileStream, outSwapped=True)
    print "\n\nOutput in Hex and swapped:"
    outFileStream.write("\n\nOutput in Hex and swapped:\n")
    runTest (outFileStream, outInHex=True, outSwapped=True)
    
    globals.cardNumber = '1012345'    
    globals.bitLength=36
    globals.trailingZeros = 4
    print "\n\nH10320 Format:"
    outFileStream.write("\n\nH10320 Format:\n")
    runTest(outFileStream)
    print "\n\nOutput in Hex:"
    outFileStream.write("\n\nOutput in Hex:\n")
    runTest(outFileStream, outInHex=True)
    print "\n\nOutput swapped:"
    outFileStream.write("\n\nOutput swapped:\n")
    runTest(outFileStream, outSwapped=True)
    print "\n\nOutput in Hex and swapped:"
    outFileStream.write("\n\nOutput in Hex and swapped:\n")
    runTest (outFileStream, outInHex=True, outSwapped=True)

    
    #Customer Defined
    print "\n\nCustomer Defined Mode"
    outFileStream.write("\n\nCustomer Defined Mode\n")
    globals.cardDataFormat = ['iClassFormat = 255', 'MifareFormat = 255', 'ProxFormat = 255', 'SeosFormat = 255']
    globals.cardNumber = '1012345'
    globals.customFields = [(0,20),(0,0),(0,0),(0,0)]
    globals.trailingZeros = 4
    globals.bitLength = 20

    print "Normal Case, 1 field:"
    print "A field"
    outFileStream.write("Normal Case, 1 field\nA field\n")
    runTest(outFileStream)
    globals.customFields = [(0,0),(0,20),(0,0),(0,0)]
    print "\n\nB field"
    outFileStream.write("\n\nNormal Case, 1 field\nB field\n")
    runTest(outFileStream)
    globals.customFields = [(0,0),(0,0),(0,20),(0,0)]
    print "\n\nC field"
    outFileStream.write("\n\nNormal Case, 1 field\nC field\n")
    runTest(outFileStream)
    globals.customFields = [(0,0),(0,0),(0,0),(0,20)]
    print "\n\nD field"
    outFileStream.write("\n\nNormal Case, 1 field\nD fieldt\n")
    runTest(outFileStream)
    print "\n\nOutput in Hex:"
    outFileStream.write("\n\nOutput in Hex:\n")
    runTest(outFileStream, outInHex=True)
    print "\n\nOutput swapped:"
    outFileStream.write("\n\nOutput swapped:\n")
    runTest(outFileStream, outSwapped=True)
    print "\n\nOutput in Hex and swapped:"
    outFileStream.write("\n\nOutput in Hex and swapped:\n")
    runTest (outFileStream, outInHex=True, outSwapped=True)
    
    globals.customFields = [(16,8),(0,16),(0,0),(0,0)]
    globals.trailingZeros = 0
    globals.bitLength = 24
    print "\n\nNormal Case, 2 fields:"
    outFileStream.write("\n\nNormal Case, 2 fields:\n")
    runTest(outFileStream)
    print "\n\nOutput in Hex:"
    outFileStream.write("\n\nOutput in Hex:\n")
    runTest(outFileStream, outInHex=True)
    print "\n\nOutput swapped:"
    outFileStream.write("\n\nOutput swapped:\n")
    runTest(outFileStream, outSwapped=True)
    print "\n\nOutput in Hex and swapped:"
    outFileStream.write("\n\nOutput in Hex and swapped:\n")
    runTest (outFileStream, outInHex=True, outSwapped=True)

    globals.customFields = [(12,7),(6,6),(0,6),(0,0)]
    globals.trailingZeros = 5
    globals.bitLength = 19
    print "\n\nNormal Case, 3 fields:"
    outFileStream.write("\n\nNormal Case, 3 fields:\n")
    runTest(outFileStream)
    print "\n\nOutput in Hex:"
    outFileStream.write("\n\nOutput in Hex:\n")
    runTest(outFileStream, outInHex=True)
    print "\n\nOutput swapped:"
    outFileStream.write("\n\nOutput swapped:\n")
    runTest(outFileStream, outSwapped=True)
    print "\n\nOutput in Hex and swapped:"
    outFileStream.write("\n\nOutput in Hex and swapped:\n")
    runTest (outFileStream, outInHex=True, outSwapped=True)

    globals.customFields = [(18,6),(12,6),(6,6),(0,6)]
    globals.trailingZeros = 0
    globals.bitLength = 24
    print "\n\nNormal Case, 4 fields:"
    outFileStream.write("\n\nNormal Case, 4 fields:\n")
    runTest(outFileStream)
    print "\n\nOutput in Hex:"
    outFileStream.write("\n\nOutput in Hex:\n")
    runTest(outFileStream, outInHex=True)
    print "\n\nOutput swapped:"
    outFileStream.write("\n\nOutput swapped:\n")
    runTest(outFileStream, outSwapped=True)
    print "\n\nOutput in Hex and swapped:"
    outFileStream.write("\n\nOutput in Hex and swapped:\n")
    runTest (outFileStream, outInHex=True, outSwapped=True)
    
    print "\n\nMaximum allowable bit length:"
    print "One Field:"
    outFileStream.write("\n\nMaximum Allowable bit length\nOne Field:\n")
    globals.cardNumber = '1012345'
    globals.customFields = [(0,64),(0,0),(0,0),(0,0)]
    globals.trailingZeros = 0
    globals.bitLength = 64
    runTest(outFileStream)
    
    print "\n\nFour Fields:"
    outFileStream.write("\n\nFour Fields:\n")
    #largest positive number for a signed 64 bit field is 9223372036854775807
    globals.cardNumber = '9223372036854775807092233720368547758070922337203685477580709223372036854775807' 
    globals.customFields = [(192,64),(128,64),(64,64),(0,64)]
    globals.bitLength = 256
    runTest(outFileStream)   
    
   
    print "\n\nOne Field of 1 bit filled with 255 bits that are ignored:"
    outFileStream.write("\n\nOne Field of 1 bit filled with 255 bits that are ignored:\n")
    globals.cardNumber = '01'
    globals.customFields = [(0,0),(0,0),(0,0),(91,1)]
    runTest(outFileStream)

    print "\n\nMinimum Allowable Bit Length:"
    print "One Field Of One Bit:"
    outFileStream.write("\n\nMinimum Allowable Bit Length:\nOne Field Of One Bit:\n")
    globals.cardNumber = '01'
    globals.customFields =  [(0,0),(0,0),(0,0),(0,1)]
    globals.trailingZeros = 7
    globals.bitLeangth = 1
    runTest(outFileStream)
    
    print "\n\nFour Fields Of One Bit:"
    outFileStream.write("\n\nFour Fields Of One Bit:\n")
    globals.cardNumber = '1010101'
    globals.customFields =  [(3,1),(2,1),(1,1),(0,1)]
    globals.trailingZeros = 4
    globals.bitLength = 4
    runTest(outFileStream)
    
    print "\n\nSpace between specified fields:"
    print "Two Fields:"
    outFileStream.write("\n\nSpace between specified fields:\nTwo Fields:")
    globals.cardNumber = '1012345'
    globals.customFields =  [(24,8),(2,16),(0,0),(0,0)]
    globals.trailingZeros = 5
    globals.bitLength = 35
    runTest(outFileStream)    
    
    print "\n\nThree Fields:"
    outFileStream.write("\n\nThree Fields:\n")
    globals.customFields =  [(22,7),(12,6),(1,6),(0,0)]
    runTest(outFileStream)

    print "\n\nFour Fields:"
    outFileStream.write("\nFour Fields:\n")
    globals.customFields =  [(30,6),(21,6),(12,6),(3,6)]
    globals.trailingZeros = 1
    globals.bitLength = 39
    runTest(outFileStream)   
    

    
    
    
    
    
def failCases(outFileStream):
    print "\n\nFailure cases:"
    outFileStream.write("\n\nFailure cases:\n")

    #RAW
    print "Raw Format"
    outFileStream.write("Raw Format\n")
    globals.cardDataFormat = ['iClassFormat = 0', 'MifareFormat = 0', 'ProxFormat = 0', 'SeosFormat = 0']
    print "Out of Bounds for Card Number:"
    print "Beyond Max Value:"
    outFileStream.write("Out of Bounds for Card Number:\nBeyond Max Value\n")
    globals.trailingZeros = 0
    globals.cardNumber = str(2**2008)
    runTest(outFileStream, failCase=True)

    #H10301
    print "\n\nH10301"
    outFileStream.write("\n\nH10301\n")
    globals.bitLength = 26
    globals.trailingZeros = 6
    globals.cardDataFormat = ['iClassFormat = 1', 'MifareFormat = 1', 'ProxFormat = 1', 'SeosFormat = 1']
    globals.cardNumber = '256065535'
    print "Out of Bounds for FAC:"
    outFileStream.write("Out of Bounds for FAC:\n")
    runTest(outFileStream, failCase=True)
    print "\n\nOut of Bounds for CN:"
    outFileStream.write("\n\nOut of Bounds for CN:\n")
    globals.cardNumber = '255065536'
    runTest(outFileStream, failCase=True)
    print "\n\nWrong bit length (35 bits):"
    outFileStream.write("\n\nWrong bit length (35 bits):\n")
    globals.bitLength = 35
    globals.trailingZeros = 5
    globals.cardNumber = '1012345'
    runTest(outFileStream, failCase=True)
    
    #H10302
    print "\n\nH10302"
    outFileStream.write("\n\nH10302\n")
    globals.bitLength = 37
    globals.trailingZeros = 3
    globals.cardDataFormat = ['iClassFormat = 2', 'MifareFormat = 2', 'ProxFormat = 2', 'SeosFormat = 2']
    globals.cardNumber = '34359738368'
    print "Out of Bounds for CN (max):"
    outFileStream.write("Out of Bounds for CN (max):\n")
    runTest(outFileStream, failCase=True)
    print "\n\nWrong bit length (35 bits):"
    outFileStream.write("\n\nWrong bit length (35 bits):\n")
    globals.bitLength = 35
    globals.trailingZeros = 5
    globals.cardNumber = '1012345'
    runTest(outFileStream, failCase=True)

    #H10304
    print "\n\nH10304"
    outFileStream.write("\n\nH10304\n")
    globals.bitLength = 37
    globals.trailingZeros = 3
    globals.cardDataFormat = ['iClassFormat = 4', 'MifareFormat = 4', 'ProxFormat = 4', 'SeosFormat = 4']
    globals.cardNumber = '65536524287'
    print "Out of Bounds for FAC:"
    outFileStream.write("Out of Bounds for FAC:\n")
    runTest(outFileStream, failCase=True)
    print "\n\nOut of Bounds for CN:"
    outFileStream.write("\n\nOut of Bounds for CN:\n")
    globals.cardNumber = '65535524288'
    runTest(outFileStream, failCase=True)
    print "\n\nWrong bit length (35 bits):"
    outFileStream.write("\n\nWrong bit length (35 bits):\n")
    globals.bitLength = 35
    globals.trailingZeros = 5
    globals.cardNumber = '1012345'
    runTest(outFileStream, failCase=True)

    #H10320
    print "\n\nH10320"
    outFileStream.write("\n\nH10320\n")
    globals.bitLength = 36
    globals.trailingZeros = 4
    globals.cardDataFormat = ['iClassFormat = 20', 'MifareFormat = 20', 'ProxFormat = 20', 'SeosFormat = 20']
    globals.cardNumber = '100000000'
    print "Out of Bounds (max):"
    outFileStream.write("Out of Bounds (max):\n")
    runTest(outFileStream, failCase=True)
    print "\n\nWrong Bit Length (37)"
    outFileStream.write("\n\nWrong Bit Length (37)\n")
    globals.cardNumber = '10123456'
    globals.bitLength = 37
    globals.trailingZeros = 3
    runTest(outFileStream, failCase=True)

    #Corp 1000
    print "\n\nCorp 1000"
    outFileStream.write("\n\nCorp 1000\n")
    globals.bitLength = 35
    globals.trailingZeros = 5
    globals.cardDataFormat = ['iClassFormat = 100', 'MifareFormat = 100', 'ProxFormat = 100', 'SeosFormat = 100']
    print "Out of Bounds for FAC:"
    outFileStream.write("Out of Bounds for FAC:\n")
    globals.cardNumber = '409601048575'
    runTest(outFileStream, failCase=True)
    print "\n\nOut of Bounds for CN:"
    outFileStream.write("\n\nOut of Bounds for CN:\n")
    globals.cardNumber = '409601048576'
    runTest(outFileStream, failCase=True)
    print "\n\nWrong Bit Length (37):"
    outFileStream.write("\n\nWrong Bit Length (37):\n")
    globals.bitLength = 37
    globals.trailingZeros = 3
    globals.cardNumber = '100012345'
    runTest(outFileStream, failCase=True)
   
    #CSN
    print "\n\nCSN"
    outFileStream.write("\n\nCSN\n")
    globals.cardDataFormat = ['iClassFormat = 253 ', 'MifareFormat = 253', 'ProxFormat = 253', 'SeosFormat = 253']
    print "Out of Bounds (max):"
    outFileStream.write("Out of Bounds (max):\n")
    globals.cardNumber = str(2**63)
    runTest(outFileStream, failCase=True)
    
    #Auto
    print "\n\nAuto Mode"
    outFileStream.write("\n\nAuto Mode\n")
    globals.cardDataFormat = ['iClassFormat = 254', 'MifareFormat = 254', 'ProxFormat = 254', 'SeosFormat = 254']
    globals.cardNumber = '1012345'
    globals.bitLength=42
    globals.trailingZeros = 2
    globals.customFields = [(17,8),(1,16),(0,0),(0,0)]
    print "\n\nUnrecognizable Bit Length:"
    outFileStream.write("\n\nUnrecognizable Bit Length:\n")
    runTest(outFileStream, failCase=True)

    print "\n\nUnrecognizable Format:"
    outFileStream.write("\n\nUnrecognizable Format:\n")
    globals.customFields = [(18,7),(2,16),(0,0),(0,0)]
    globals.bitLength = 26
    globals.trailingZeros = 6
    runTest(outFileStream, failCase=True)
    
    
    print "\n\nCustom Setup:"
    print "Overlapping Fields:"
    outFileStream.write("\n\nCustom Setup:\nOverlapping Fields:\n")
    loadPreExistIni("overlap.ini")
    runTest(outFileStream, noIni=True, failCase=True)
    
    print "\n\nWrong Boundaries:"
    outFileStream.write("\n\nWrong Boundaries:\n")
    loadPreExistIni("wrongBoundaries.ini")
    runTest(outFileStream, noIni=True, failCase=True)
    
    print "\n\nBad PACS File:"
    outFileStream.write("\n\nBad PACS File:\n")
    loadPreExistIni("badPACS.ini")
    runTest(outFileStream, noIni=True, failCase=True)    

    print "\n\nBad Format File:"
    outFileStream.write("\n\nBad Format File:\n")
    loadPreExistIni("badFormat.ini")
    runTest(outFileStream, noIni=True, failCase=True) 

    print "\n\nBad Field File:"
    outFileStream.write("\n\nBad Field File:\n")
    loadPreExistIni("badFields.ini")
    runTest(outFileStream, noIni=True, failCase=True)  
    


def cleanUp():
    subprocess.call("rm -rf 5427ckApps", shell=True)

