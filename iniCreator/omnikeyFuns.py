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

def runTest(outFileStream, outSwapped=False, outInHex=False, noIni=False, failCase=False,
            minID = '0', customSettings = []):
#customSettings is a list of dictionaries containing: 
#'label': label for custom setup 
#'type': card format type - prox = 64, iclass = 10, mifare = 3, seos = 80
#'bitLength': bit length of card
#'fields: list of pairs for bit fields
#'adjust': set adjustment settings on or off 
#'belowThresh': set lower than threshold on or off
#'thresh': threshold value 
#'startBit': start bit value 
#'value': decimal adjustment value 
#'mask': bit mask value
#all values are strings 

    compare = globals.cardNumber
    inHexidecimal = 'false'
    outputSwap = 'false'
    isRaw = False
    isCSN = False
    
    if (globals.activeCard + 'Format = 0') in globals.cardDataFormat:
        isRaw = True
    if (globals.activeCard + 'Format = 253') in globals.cardDataFormat:
        isCSN = True
        
    rawHex = str("%x" % int(compare)).upper()
#    rawHex = str(hex(int(compare)).lstrip("0x") or '0').upper()
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
    if isRaw or isCSN:
        numBits = (len(rawHex)-1)*4 + bitsInNibble
        if numBits == 0:
            numBits = 1
    else:
        numBits = globals.bitLength

    paddedBytes = (numBits+globals.trailingZeros+7)/8 #number of bytes with trailing zeros
    dataBits = 8*paddedBytes - globals.trailingZeros #number of bits for PACS data
    PACSBytes = (dataBits+7)/8

    numChars = 2*PACSBytes - len(rawHex) #number of nibbles needed
    for x in range (0, numChars):
        rawHex = '0'+rawHex
        
    if isRaw:
        compare = rawHex
    if outInHex:
        inHexidecimal = 'true'
        if isCSN:
            compare = rawHex
                    
    if outSwapped:
        outputSwap = 'true'
        if isCSN:
            compare = rawHex
            compare = "".join(reversed([compare[i:i+2] for i in range(0, len(compare), 2)]))
            if outInHex == False:
                compare = str(int(compare, 16))
                outputSwap = 'true'

    if noIni == False:
        loadIni()

    
    if outInHex or outSwapped:
        setSettings(swap=outputSwap, inHex=inHexidecimal, minCardID = minID)
        #no need for custom settings only valid in CSN
    elif len(customSettings) != 0:
        setSettings(custom = customSettings, minCardID = minID)
        # no need for swap or hex, only valid for CSN mode
    elif int(minID) > 0:
        setSettings(minCardID = minID)

    
    if len(customSettings) != 0:
        adjustResult = adjustValue(compare, customSettings)
        print adjustResult
        if adjustResult != 'no adjustment':
            compare = adjustResult
            
    while len(compare) < int(minID):
        compare = '0'+compare

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
    iniArgs = [globals.cardNumber, globals.bitLength, globals.cardDataFormat, globals.activeCard, globals.trailingZeros, globals.outFileName, globals.customFields, globals.suppress]
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
    

def setSettings(swap='false', inHex='false', beep='false', iClass='254', mifare='254', prox='254', seos='254', minCardID = '0', 
                custom = []):
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

    writeUCF(omnikeyVersion, swap, inHex, beep, iClass, mifare, prox, seos, minCardID, custom)
    sendUCF()

    

def writeUCF(version, dataswap, datahex, beep, iClass, mifare, prox, seos, minCardID, custom):
    tempCustom = custom  #shallow copy for .pop()
    file = open("omnikey5427.ucf", "w+")
    file.write("esf.version.omnikey5427ckdriver "+version+"\n")
    file.write("esf.omnikey5427ckdriver.settings.dataswap \""+dataswap+"\"\n")
    file.write("esf.omnikey5427ckdriver.settings.datahex \""+datahex+"\"\n")
    file.write("esf.omnikey5427ckdriver.settings.beep \""+beep+"\"\n")
    file.write("esf.omnikey5427ckdriver.settings.minCardIdResponseLength \""+minCardID+"\"\n")
    file.write("esf.omnikey5427ckdriver.settings.iClassformat \""+iClass+"\"\n")
    file.write("esf.omnikey5427ckdriver.settings.iClassMode \"1\"\n")
    file.write("esf.omnikey5427ckdriver.settings.miFareformat \""+mifare+"\"\n")
    file.write("esf.omnikey5427ckdriver.settings.miFareMode \"1\"\n")
    file.write("esf.omnikey5427ckdriver.settings.proxformat \""+prox+"\"\n")
    file.write("esf.omnikey5427ckdriver.settings.seosformat \""+seos+"\"\n")
    file.write("esf.omnikey5427ckdriver.settings.seosMode \"1\"\n")
    file.write("esf.omnikey5427ckdriver.settings.iso14443A.enable \"true\"\n")
    file.write("esf.omnikey5427ckdriver.settings.iso14443B.enable \"true\"\n")
    file.write("esf.omnikey5427ckdriver.settings.iso15693.enable \"true\"\n")
    file.write("esf.omnikey5427ckdriver.settings.felica.enable \"true\"\n")
    file.write("esf.omnikey5427ckdriver.settings.iClass14443.enable \"false\"\n")
    file.write("esf.omnikey5427ckdriver.settings.iClass15693.enable \"true\"\n")
    file.write("esf.omnikey5427ckdriver.settings.hidprox.enable \"true\"\n")
    i=1
    while tempCustom:
        temp = tempCustom.pop()
        file.write("esf.omnikey5427ckdriver.inst."+str(i)+".settings.customproxformat.label \""+temp['label']+"\"\n")
        file.write("esf.omnikey5427ckdriver.inst."+str(i)+".settings.customproxformat.type \""+temp['type']+"\"\n")
        file.write("esf.omnikey5427ckdriver.inst."+str(i)+".settings.customproxformat.bitlength \""+temp['bitLength']+"\"\n")
        file.write("esf.omnikey5427ckdriver.inst."+str(i)+".settings.customproxformat.startbitA \""+temp['fields'][0][0]+"\"\n")
        file.write("esf.omnikey5427ckdriver.inst."+str(i)+".settings.customproxformat.idbitlengthA \""+temp['fields'][0][1]+"\"\n")
        file.write("esf.omnikey5427ckdriver.inst."+str(i)+".settings.customproxformat.startbitB \""+temp['fields'][1][0]+"\"\n")
        file.write("esf.omnikey5427ckdriver.inst."+str(i)+".settings.customproxformat.idbitlengthB \""+temp['fields'][1][1]+"\"\n")
        file.write("esf.omnikey5427ckdriver.inst."+str(i)+".settings.customproxformat.startbitC \""+temp['fields'][2][0]+"\"\n")
        file.write("esf.omnikey5427ckdriver.inst."+str(i)+".settings.customproxformat.idbitlengthC \""+temp['fields'][2][1]+"\"\n")
        file.write("esf.omnikey5427ckdriver.inst."+str(i)+".settings.customproxformat.startbitD \""+temp['fields'][3][0]+"\"\n")
        file.write("esf.omnikey5427ckdriver.inst."+str(i)+".settings.customproxformat.idbitlengthD \""+temp['fields'][3][1]+"\"\n")
        file.write("esf.omnikey5427ckdriver.inst."+str(i)+".settings.customproxformat.adjust.enable \""+temp['adjust']+"\"\n")
        file.write("esf.omnikey5427ckdriver.inst."+str(i)+".settings.customproxformat.adjust.lower \""+temp['belowThresh']+"\"\n")
        file.write("esf.omnikey5427ckdriver.inst."+str(i)+".settings.customproxformat.adjust.threshold \""+temp['thresh']+"\"\n")
        file.write("esf.omnikey5427ckdriver.inst."+str(i)+".settings.customproxformat.adjust.startBit \""+temp['startBit']+"\"\n")
        file.write("esf.omnikey5427ckdriver.inst."+str(i)+".settings.customproxformat.adjust.value \""+temp['value']+"\"\n")
        file.write("esf.omnikey5427ckdriver.inst."+str(i)+".settings.customproxformat.adjust.mask \""+temp['mask']+"\"\n")
        i=i+1
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

def adjustValue(compare, customSettings):
    #customSettings is a list of dictionaries containing: 
    #'label': label for custom setup 
    #'type': card format type - prox = 64, iclass = 10, mifare = 3, seos = 80
    #'bitLength': bit length of card
    #'fields: list of pairs for bit fields
    #'adjust': set adjustment settings on or off 
    #'belowThresh': set lower than threshold on or off
    #'thresh': threshold value 
    #'startBit': start bit value 
    #'value': decimal adjustment value 
    #'mask': bit mask value
    #all values are strings
    if globals.activeCard == 'Prox':
        activeNum = '64'
    elif globals.activeCard =='iClass':
        activeNum = '10'
    elif globals.activeCard =='Mifare':
        activeNum = '3'
    elif globals.activeCard == 'Seos':
        activeNum = '80'
    
    tempCustom = customSettings # shallow copy for .pop()
    while tempCustom:
        temp = tempCustom.pop()
        if temp['type'] == activeNum:
            if int(temp['bitLength']) == globals.bitLength:
                print "Custom setup matched."
                break
    else:
        print "No matching custom setup found."
        return 'no adjustment'

    if temp['adjust'] == 'false':
        print "Adjustment not enabled."
    else:
        if (temp['belowThresh'] == 'true') and (int(compare) >= int(temp['thresh'])):
            print "Card value is above threshold.  No additional processing."
        elif (temp['belowThresh'] == 'false') and (int(compare) < int(temp['thresh'])):
             print "Card value below threshold and adjustment below threshold is turned off.  No additional processing."           
        else:
            intCompare = int(compare) >> int(temp['startBit']) #make new start bit for card number
            intCompare = intCompare + int(temp['value']) #add adjustment value to card number
            intCompare = intCompare & int(temp['mask'], 16) #bit mask card number
            compare = str(intCompare)
            return compare
            


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
    print "\n\nLess than minimum ID length:"
    outFileStream.write("\n\nLess than minimum ID length:")
    globals.cardNumber = '1012345'
    runTest(outFileStream, minID = '9')
                      
    
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
    print "\n\nLess than minimum ID length:"
    outFileStream.write("\n\nLess than minimum ID length:")
    globals.cardNumber = '1012345'
    runTest(outFileStream, minID = '9')
    
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
    print "\n\nLess than minimum ID length:"
    outFileStream.write("\n\nLess than minimum ID length:")
    globals.cardNumber = '1012345'
    runTest(outFileStream, minID = '9')

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
    print "\n\nLess than minimum ID length:"
    outFileStream.write("\n\nLess than minimum ID length:")
    globals.cardNumber = '1012345'
    runTest(outFileStream, minID = '9')

   
    
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
    print "\n\nLess than minimum ID length:"
    outFileStream.write("\n\nLess than minimum ID length:")
    globals.cardNumber = '1012345'
    runTest(outFileStream, minID = '9')

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
    print "\n\nLess than minimum ID length:"
    outFileStream.write("\n\nLess than minimum ID length:")
    globals.cardNumber = '100012345'
    runTest(outFileStream, minID = '11')
    
    #CSN 
    print "\n\nCSN"
    outFileStream.write("\n\nCSN\n")
    globals.trailingZeros = 0   
    globals.cardDataFormat = ['iClassFormat = 253 ', 'MifareFormat = 253', 'ProxFormat = 253', 'SeosFormat = 253']
    print "Normal Case:"
    outFileStream.write("Normal Case:\n")
    globals.cardNumber = '1012345'
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
    globals.cardNumber = str((2**63)-1)
    print "\n\nMax Value:"
    outFileStream.write("\n\nMax Value:\n")
    runTest(outFileStream)
    print "\n\nMin Value:"
    outFileStream.write("\n\nMin Value:\n")
    globals.cardNumber = '0'
    runTest(outFileStream)
    print "\n\nLess than minimum ID length:"
    outFileStream.write("\n\nLess than minimum ID length:\n")
    globals.cardNumber = '1012345'
    runTest(outFileStream, minID = '9')
    print "\n\nLess than minimum ID length (hex and swapped):"
    outFileStream.write("\n\nLess than minimum ID length (hex and swapped):\n")
    globals.cardNumber = '1012345'
    runTest(outFileStream, outInHex=True, outSwapped=True, minID = '9')
    
    
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
    print "\n\nLess than minimum ID length:"
    outFileStream.write("\n\nLess than minimum ID length:")
    runTest(outFileStream, minID = '9')
    
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
    print "\n\nLess than minimum ID length:"
    outFileStream.write("\n\nLess than minimum ID length:")
    runTest(outFileStream, minID = '9')
    
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
    print "\n\nLess than minimum ID length:"
    outFileStream.write("\n\nLess than minimum ID length:")
    runTest(outFileStream, minID = '11')
    
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
    print "\n\nLess than minimum ID length:"
    outFileStream.write("\n\nLess than minimum ID length:")
    runTest(outFileStream, minID = '9')
    
    
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
    print "\n\nLess than minimum ID length:"
    outFileStream.write("\n\nLess than minimum ID length:")
    runTest(outFileStream, minID = '9')
    
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
    print "\n\nLess than minimum ID length:"
    outFileStream.write("\n\nLess than minimum ID length:")
    runTest(outFileStream, minID = '9')

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
    print "\n\nLess than minimum ID length:"
    outFileStream.write("\n\nLess than minimum ID length:")
    runTest(outFileStream, minID = '9')

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
    print "\n\nLess than minimum ID length:"
    outFileStream.write("\n\nLess than minimum ID length:")
    runTest(outFileStream, minID = '9')
    
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

def multipleCustomTests(outFileStream):
    print "\n\nMultiple Custom and Adjustment tests:"
    outFileStream.write("\n\nMultiple Custom and Adjustment tests:\n")
    globals.cardDataFormat = ['iClassFormat = 255', 'MifareFormat = 255', 'ProxFormat = 255', 'SeosFormat = 255']
    globals.cardNumber = '1012345'
    globals.bitLength=26
    globals.trailingZeros = 6
    globals.customFields = [(17,8),(1,16),(0,0),(0,0)]
    globals.suppress = True
    if globals.activeCard == 'Prox':
        cardType = '64'
    elif globals.activeCard == 'iClass':
        cardType = '10'
    elif globals.activeCard == 'Mifare':
        cardType = '3'
    elif globals.activeCard == 'Seos':
        cardType = '80'
    else:
        cardType = '64'
    
    customSuccess = {'label': 'customSuccess', 'type': cardType, 'bitLength':'26','fields':[('11','08'),('01','10'),('00','00'),('00','00')],
                     'adjust': 'false', 'belowThresh': 'true', 'thresh': '95', 'startBit': '19', 'value': '132', 'mask': 'fffffffffffffff0'}
    customProx = {'label': 'customProx', 'type': '64', 'bitLength':'19','fields':[('08','0B'),('00','08'),('00','00'),('00','00')],
                     'adjust': 'false', 'belowThresh': 'true', 'thresh': '95', 'startBit': '19', 'value': '132', 'mask': 'fffffffffffffff0'}
    customIClass = {'label': 'customIClass', 'type': '10', 'bitLength':'19','fields':[('08','0B'),('00','08'),('00','00'),('00','00')],
                     'adjust': 'false', 'belowThresh': 'true', 'thresh': '95', 'startBit': '19', 'value': '132', 'mask': 'fffffffffffffff0'}
    customMifare = {'label': 'customMifare', 'type': '3', 'bitLength':'19','fields':[('08','0B'),('00','08'),('00','00'),('00','00')],
                     'adjust': 'false', 'belowThresh': 'true', 'thresh': '95', 'startBit': '19', 'value': '132', 'mask': 'fffffffffffffff0'}
    customSeos = {'label': 'customSeos', 'type': '80', 'bitLength':'19','fields':[('08','0B'),('00','08'),('00','00'),('00','00')],
                     'adjust': 'false', 'belowThresh': 'true', 'thresh': '95', 'startBit': '19', 'value': '132', 'mask': 'fffffffffffffff0'}
    customList = [customSeos, customMifare, customIClass, customProx, customSuccess]
    print "\n5 custom setups, 1 with correct bit length:"
    outFileStream.write("\5 custom setups, 1 with correct bit length\n")
    runTest (outFileStream, customSettings = customList)

    customSuccess = {'label': 'customSuccess', 'type': cardType, 'bitLength':'26','fields':[('11','08'),('01','10'),('00','00'),('00','00')],
                     'adjust': 'false', 'belowThresh': 'true', 'thresh': '95', 'startBit': '19', 'value': '132', 'mask': 'fffffffffffffff0'}
    customFail1 = {'label': 'customFail1', 'type': cardType, 'bitLength':'19','fields':[('08','0B'),('00','08'),('00','00'),('00','00')],
                     'adjust': 'false', 'belowThresh': 'true', 'thresh': '95', 'startBit': '19', 'value': '132', 'mask': 'fffffffffffffff0'}
    customFail2 = {'label': 'customFail2', 'type': cardType, 'bitLength':'32','fields':[('18','08'),('10','08'),('08','08'),('00','08')],
                   'adjust': 'false', 'belowThresh': 'true', 'thresh': '95', 'startBit': '19', 'value': '132', 'mask': 'fffffffffffffff0'}
    customList = [customSuccess, customFail2, customFail1]
    print "\n3 custom setups, all same type with different bit lengths.  Correct bit length setup should be used:"
    outFileStream.write("\n3 custom setups, all same type with different bit lengths.  Correct bit length setup should be used:\n")
    runTest (outFileStream, customSettings = customList)

    customSuccess = {'label': 'customSuccess', 'type': cardType, 'bitLength':'26','fields':[('11','08'),('01','10'),('00','00'),('00','00')],
                     'adjust': 'false', 'belowThresh': 'true', 'thresh': '95', 'startBit': '19', 'value': '132', 'mask': 'fffffffffffffff0'}
    customFail1 = {'label': 'customFail1', 'type': cardType, 'bitLength':'26','fields':[('10','08'),('00','10'),('00','00'),('00','00')],
                     'adjust': 'false', 'belowThresh': 'true', 'thresh': '95', 'startBit': '19', 'value': '132', 'mask': 'fffffffffffffff0'}
    customFail2 = {'label': 'customFail2', 'type': cardType, 'bitLength':'26','fields':[('12','08'),('10','02'),('00','00'),('00','00')],
                   'adjust': 'false', 'belowThresh': 'true', 'thresh': '95', 'startBit': '19', 'value': '132', 'mask': 'fffffffffffffff0'}
    customList = [customSuccess, customFail2, customFail1]
    print "\n3 custom setups, all same type with same bit lengths.  Last correct bit length setup should be used:"
    outFileStream.write("\n3 custom setups, all same type with same bit lengths.  Last correct bit length setup should be used:\n")
    runTest (outFileStream, customSettings = customList)
    
    customSuccess = {'label': 'customSuccess', 'type': cardType, 'bitLength':'26','fields':[('11','08'),('01','10'),('00','00'),('00','00')],
                     'adjust': 'true', 'belowThresh': 'true', 'thresh': '100', 'startBit': '2', 'value': '100', 'mask': 'ffffff0'}
    customList = [customSuccess]
    print "\nAdjustment and threshold set.  Card Number above threshold, no adjustments made:"
    outFileStream.write("\nAdjustment set.  Threshold set.  Card Number above threshold, no adjustments made:\n")
    runTest (outFileStream, customSettings = customList)
    
    customSuccess = {'label': 'customSuccess', 'type': cardType, 'bitLength':'26','fields':[('11','08'),('01','10'),('00','00'),('00','00')],
                     'adjust': 'true', 'belowThresh': 'true', 'thresh': '5000000', 'startBit': '2', 'value': '100', 'mask': 'ffffff0'}
    customList = [customSuccess]
    print "\nAdjustment and threshold set.  Card Number below threshold, adjustments made:"
    outFileStream.write("\nAdjustment and threshold set.  Card Number below threshold, adjustments made:\n")
    runTest (outFileStream, customSettings = customList)

    customSuccess = {'label': 'customSuccess', 'type': cardType, 'bitLength':'26','fields':[('11','08'),('01','10'),('00','00'),('00','00')],
                     'adjust': 'true', 'belowThresh': 'false', 'thresh': '5000000', 'startBit': '2', 'value': '100', 'mask': 'ffffff0'}
    customList = [customSuccess]
    print "\nAdjustment set.  Below threshold not set, adjustments not made:"
    outFileStream.write("\nAdjustment set.  Threshold not set, adjustments made:\n")
    runTest (outFileStream, customSettings = customList)

    customSuccess = {'label': 'customSuccess', 'type': cardType, 'bitLength':'26','fields':[('11','08'),('01','10'),('00','00'),('00','00')],
                     'adjust': 'true', 'belowThresh': 'false', 'thresh': '0', 'startBit': '2', 'value': '100', 'mask': 'ffffff0'}
    customList = [customSuccess]
    print "\nAdjustment set.  Below threshold not set, adjustments made:"
    outFileStream.write("\nAdjustment set.  Threshold not set, adjustments made:\n")
    runTest (outFileStream, customSettings = customList)
    
    customSuccess = {'label': 'customSuccess', 'type': cardType, 'bitLength':'26','fields':[('11','08'),('01','10'),('00','00'),('00','00')],
                     'adjust': 'true', 'belowThresh': 'false', 'thresh': '5000000', 'startBit': '1', 'value': '2147483647', 'mask': 'ffffffffffffffff'}
    customList = [customSuccess]
    print "\nMax Adjustment Value:"  #max value is 0x7fffffff 
    outFileStream.write("\nMax Adjustment Value:\n")
    runTest (outFileStream, customSettings = customList)

    customSuccess = {'label': 'customSuccess', 'type': cardType, 'bitLength':'26','fields':[('11','08'),('01','10'),('00','00'),('00','00')],
                     'adjust': 'true', 'belowThresh': 'false', 'thresh': '5000000', 'startBit': '2147483647', 'value': '0', 'mask': 'ffffffffffffffff'}
    customList = [customSuccess]
    print "\nMax Start Bit:"  #max value is 0x7fffffff 
    outFileStream.write("\nMax Start Bit:\n")
    runTest (outFileStream, customSettings = customList)

    customSuccess = {'label': 'customSuccess', 'type': cardType, 'bitLength':'26','fields':[('11','08'),('01','10'),('00','00'),('00','00')],
                     'adjust': 'true', 'belowThresh': 'true', 'thresh': '2147483647', 'startBit': '2', 'value': '0', 'mask': 'ffffffffffffffff'}
    customList = [customSuccess]
    print "\nMax threshold:"  #max value is 0x7fffffff 
    outFileStream.write("\nMax threshold:\n")
    runTest (outFileStream, customSettings = customList)

    customFail = {'label': 'customFail', 'type': cardType, 'bitLength':'26','fields':[('11','08'),('01','10'),('00','00'),('00','00')],
                     'adjust': 'true', 'belowThresh': 'true', 'thresh': '2147483648', 'startBit': '1', 'value': '0', 'mask': 'fffffffffffffff'}
    customList = [customFail]
    print "\nOver Max threshold:"
    outFileStream.write("\nOver Max threshold:\n")
    runTest (outFileStream, failCase = True, customSettings = customList)
    

    customFail1 = {'label': 'customSuccess', 'type': cardType, 'bitLength':'19','fields':[('00','13'),('00','00'),('00','00'),('00','00')],
                     'adjust': 'false', 'belowThresh': 'true', 'thresh': '5000000', 'startBit': '2', 'value': '100', 'mask': 'ffffff0'}
    customFail2 = {'label': 'customSuccess', 'type': cardType, 'bitLength':'24','fields':[('00','18'),('00','00'),('00','00'),('00','00')],
                     'adjust': 'false', 'belowThresh': 'true', 'thresh': '5000000', 'startBit': '2', 'value': '100', 'mask': 'ffffff0'}
    customFail3 = {'label': 'customSuccess', 'type': cardType, 'bitLength':'27','fields':[('00','1B'),('00','00'),('00','00'),('00','00')],
                     'adjust': 'false', 'belowThresh': 'true', 'thresh': '5000000', 'startBit': '2', 'value': '100', 'mask': 'ffffff0'}
    customList = [customFail3, customFail2, customFail1 ]
    print "\nFail Case - 3 setups of wrong bit length:"
    outFileStream.write("\nFail Case - 3 setups of wrong bit length:\n")
    runTest (outFileStream, failCase = True, customSettings = customList)

    customFail = {'label': 'customFail', 'type': cardType, 'bitLength':'26','fields':[('15','08'),('01','14'),('00','00'),('00','00')],
                     'adjust': 'false', 'belowThresh': 'false', 'thresh': '5000000', 'startBit': '2', 'value': '100', 'mask': 'ffffff0'}
    customList = [customFail]
    print "\nFail Case - mismatched bit length and field boundaries:"
    outFileStream.write("\nFail Case - mismatched bit length and field boundaries:\n")
    runTest (outFileStream, failCase = True, customSettings = customList)
    
    customFail = {'label': 'customFail', 'type': cardType, 'bitLength':'26','fields':[('11','08'),('01','10'),('00','00'),('00','00')],
                     'adjust': 'true', 'belowThresh': 'false', 'thresh': '5000000', 'startBit': '1', 'value': '2147483648', 'mask': 'fffffffffffffff'}
    customList = [customFail]
    print "\nOver Max adjustment value:"
    outFileStream.write("\nOver Max adjustment Value:\n")
    runTest (outFileStream, failCase = True, customSettings = customList)

    customFail = {'label': 'customFail', 'type': cardType, 'bitLength':'26','fields':[('11','08'),('01','10'),('00','00'),('00','00')],
                     'adjust': 'true', 'belowThresh': 'false', 'thresh': '5000000', 'startBit': '2147483648', 'value': '0', 'mask': 'fffffffffffffff'}
    customList = [customFail]
    print "\nOver Max start bit:"
    outFileStream.write("\nOver Max start bit:\n")
    runTest (outFileStream, failCase = True, customSettings = customList)
    






    
def disabledCardTests(outFileStream): 
    #not currently possible to automate.  Disabled card types suppress card events, cardslotsim generates a card event 
    #regardless of disabled card type settings
    print "\n\nDisabled Card Tests:"
    outFileStream.write("\n\nDisabled Card Tests:\n")
    globals.cardDataFormat = ['iClassFormat = 254', 'MifareFormat = 254', 'ProxFormat = 254', 'SeosFormat = 254']
    globals.cardNumber = '1012345'
    globals.bitLength=26
    globals.trailingZeros = 6
    globals.customFields = [(17,8),(1,16),(0,0),(0,0)]
    print "\n\nProx Disabled:"
    outFileStream.write("\n\nProx Disabled:\n")
    globals.cardNumber = '1012345'
    runTest(outFileStream, disabledCard = 'Prox')
    print "\n\nMifare Disabled:"
    outFileStream.write("\n\nMifare Disabled:\n")
    globals.cardNumber = '1012345'
    runTest(outFileStream, disabledCard = 'Mifare')
    print "\n\niClass Disabled:"
    outFileStream.write("\n\niClass Disabled:\n")
    globals.cardNumber = '1012345'
    runTest(outFileStream, disabledCard = 'iClass')
    print "\n\nFelicia Disabled:"
    outFileStream.write("\n\nFelicia Disabled:\n")
    globals.cardNumber = '1012345'
    runTest(outFileStream, disabledCard = 'Felicia')
    print "\n\nAll Disabled:"
    outFileStream.write("\n\nAll Disabled:\n")
    globals.cardNumber = '1012345'
    runTest(outFileStream, disabledCard = 'All')

def cleanUp():
    subprocess.call("rm -rf 5427ckApps", shell=True)

