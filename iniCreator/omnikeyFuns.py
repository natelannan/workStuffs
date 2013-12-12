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
    subprocess.call("unzip -d 5427ckApps nlannan\\\\5427ckApps.zip", shell=True)
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
    cardslotPattern = re.compile(r".*Card Slot Simulation.*")
    omnikeyPattern = re.compile(r".*Omnikey 5427ck Reader Driver.*")
    readerPattern = re.compile(r".*Reader Test.*")
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

def runTest(outSwapped=False, outInHex=False):
    compare = globals.cardNumber
    inHexidecimal = 'false'
    outputSwap = 'false'
    if outInHex:
        compare = str(hex(int(compare)).lstrip("0x") or '0').upper()
        inHexidecimal = 'true'
    if outSwapped:
        compare = 'stub'
        outputSwap = 'true'

    loadIni()
    if outInHex or outSwapped:
        setSettings(swap=outputSwap, inHex=inHexidecimal)
    deleteEsfLog()
    swipeCard()
    userID = parseEsfLog()


    if userID == compare:
        print "cardNumber = \t"+ compare+"\nuserID = \t"+userID+"\n\nPASS"
    else:
        print "cardNumber = \t"+ compare+"\nuserID = \t"+userID+"\n\nFAIL"
        #sys.exit(1)


def loadIni():
    iniArgs = [globals.cardNumber, globals.bitLength, globals.cardDataFormat, globals.activeCard, globals.trailingZeros, globals.outFileName, globals.customFields]

    iniCreator(iniArgs)

    sessionValue = getCurlSession()
    startCurlSession(sessionValue)

    curlSendCmd = "curl -H \"Cookie: JSESSIONID="+sessionValue+"\" -F settings.inifile=@"+globals.outFileName+" http://" \
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
    omnikeyPattern = re.compile(r".*Omnikey 5427ck Reader Driver.*=  (.*) <.*")
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
#    file.write("esf.omnikey5427ckdriver.settings.inifile \"\"\n")
#    file.write("esf.omnikey5427ckdriver.settings.inifile.#filename \"\"\n")
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
    sleep(2)
    tn.write('o')
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

def successCases():
    '''
    #RAW
    print "Raw Format"
    globals.cardDataFormat = ['iClassFormat = 0', 'MifareFormat = 0', 'ProxFormat = 0', 'SeosFormat = 0']
    globals.cardNumber = '1012345'
    print "Normal Case:"
    runTest()
    print "Output in Hex:"
    runTest(outInHex=True)
    #print "Output swapped:"
    #runTest(outSwapped=True)
    #print "Output in Hex and swapped:"
    #runTest(outInHex=True, outSwapped=True)
    print "Max Value:"
    globals.cardNumber = str((2**57)-1) 
    runTest()
    print "Min Value:"
    globals.cardNumber = '0'
    runTest()
                      
    
    #H10301
    print "H10301"
    globals.bitLength = 26
    globals.trailingZeros = 6
    globals.cardDataFormat = ['iClassFormat = 1', 'MifareFormat = 1', 'ProxFormat = 1', 'SeosFormat = 1']
    globals.cardNumber = '1012345'
    print "Normal Case:"
    runTest()
    print "Output in Hex:"
    runTest(outInHex=True)
    #print "Output swapped:"
    #runTest(outSwapped=True)
    #print "Output in Hex and swapped:"
    #runTest(outInHex=True, outSwapped=True)
    print "Max Value:"
    globals.cardNumber = '255065535'
    runTest()
    print "Min Value:"
    globals.cardNumber = '0000000'
    runTest()
    
    #H10302
    print "H10302"
    globals.bitLength = 37
    globals.trailingZeros = 3
    globals.cardDataFormat = ['iClassFormat = 2', 'MifareFormat = 2', 'ProxFormat = 2', 'SeosFormat = 2']
    globals.cardNumber = '1012345'
    print "Normal Case:"
    runTest()
    print "Output in Hex:"
    runTest(outInHex=True)
    #print "Output swapped:"
    #runTest(outSwapped=True)
    #print "Output in Hex and swapped:"
    #runTest(outInHex=True, outSwapped=True)
    print "Max Value:"
    globals.cardNumber = '34359738367'
    runTest()
    print "Min Value:"
    globals.cardNumber = '0'
    runTest()

    #H10304
    print "H10304"
    globals.bitLength = 37
    globals.trailingZeros = 3
    globals.cardDataFormat = ['iClassFormat = 4', 'MifareFormat = 4', 'ProxFormat = 4', 'SeosFormat = 4']
    globals.cardNumber = '1012345'
    print "Normal Case:"
    runTest()
    print "Output in Hex:"
    runTest(outInHex=True)
    #print "Output swapped:"
    #runTest(outSwapped=True)
    #print "Output in Hex and swapped:"
    #runTest(outInHex=True, outSwapped=True)
    print "Max Value:"
    globals.cardNumber = '65535524287' 
    runTest()
    print "Min Value:"
    globals.cardNumber = '0000000'
    runTest()

   

    #H10320
    print "H10320"
    globals.bitLength = 36
    globals.trailingZeros = 4
    globals.cardDataFormat = ['iClassFormat = 20', 'MifareFormat = 20', 'ProxFormat = 20', 'SeosFormat = 20']
    globals.cardNumber = '1012345'
    print "Normal Case:"
    runTest()
    print "Output in Hex:"
    runTest(outInHex=True)
    #print "Output swapped:"
    #runTest(outSwapped=True)
    #print "Output in Hex and swapped:"
    #runTest(outInHex=True, outSwapped=True)
    print "Max Value:"
    globals.cardNumber = '99999999'
    runTest()
    print "Min Value:"
    globals.cardNumber = '0'
    runTest()

    '''
    '''
    #Corp 1000
    print "Corp 1000"
    globals.bitLength = 35
    globals.trailingZeros = 5
    globals.cardDataFormat = ['iClassFormat = 100', 'MifareFormat = 100', 'ProxFormat = 100', 'SeosFormat = 100']
    globals.cardNumber = '100012345'
    print "Normal Case:"
    runTest()
    print "Output in Hex:"
    runTest(outInHex=True)
    #print "Output swapped:"
    #runTest(outSwapped=True)
    #print "Output in Hex and swapped:"
    #runTest(outInHex=True, outSwapped=True)
    print "Max Value:"
    globals.cardNumber = '409501048575'
    runTest()
    print "Min Value:"
    globals.cardNumber = '000000000'
    runTest()
    
    #CSN
    print "CSN"
    globals.cardDataFormat = ['iClassFormat = 253 ', 'MifareFormat = 253', 'ProxFormat = 253', 'SeosFormat = 253']
    print "Normal Case:"
    globals.cardNumber = '1012345'
    runTest()
    globals.cardNumber = str((2**63)-1)
    print "Max Value:"
    runTest()
    print "Min Value:"
    globals.cardNumber = '0'
    runTest()
    '''
    #Auto
    #print "Auto Mode"
    #globals.cardDataFormat = ['iClassFormat = 254', 'MifareFormat = 254', 'ProxFormat = 254', 'SeosFormat = 254']
    #globals.cardNumber = '1012345'
    #print "Normal Case:"
    #runTest()
    #print "Output in Hex:"
    #runTest(outInHex=True)
    #print "Output swapped:"
    #runTest(outSwapped=True)
    #print "Output in Hex and swapped:"
    #runTest (outInHex=True, outSwapped=True)

    
    #Currently causes crash - DE28378
    #Customer Defined
    print "Customer Defined Mode"
    globals.cardDataFormat = ['iClassFormat = 255', 'MifareFormat = 255', 'ProxFormat = 255', 'SeosFormat = 255']
    globals.cardNumber = '1012345'
    globals.customFields = [(0,20),(0,0),(0,0),(0,0)]
    globals.trailingZeros = 4
    globals.bitLength = 20
    print "Normal Case, 1 field:"
    print "A field"
    runTest()
    globals.customFields = [(0,0),(0,20),(0,0),(0,0)]
    print "B field"
    runTest()
    globals.customFields = [(0,0),(0,0),(0,20),(0,0)]
    print "C field"
    runTest()
    globals.customFields = [(0,0),(0,0),(0,0),(0,20)]
    print "D field"
    runTest()
    print "Output in Hex:"
    runTest(outInHex=True)
    #print "Output swapped:"
    #runTest(outSwapped=True)
    #print "Output in Hex and swapped:"
    #runTest (outInHex=True, outSwapped=True)

    globals.customFields = [(16,8),(0,16),(0,0),(0,0)]
    globals.trailingZeros = 0
    globals.bitLength = 24
    print "Normal Case, 2 fields:"
    runTest()
    print "Output in Hex:"
    runTest(outInHex=True)
    #print "Output swapped:"
    #runTest(outSwapped=True)
    #print "Output in Hex and swapped:"
    #runTest (outInHex=True, outSwapped=True)

    globals.customFields = [(12,7),(6,6),(0,6),(0,0)]
    globals.trailingZeros = 5
    globals.bitLength = 19
    print "Normal Case, 3 fields:"
    runTest()
    print "Output in Hex:"
    runTest(outInHex=True)
    #print "Output swapped:"
    #runTest(outSwapped=True)
    #print "Output in Hex and swapped:"
    #runTest (outInHex=True, outSwapped=True)

    globals.customFields = [(18,6),(12,6),(6,6),(0,6)]
    globals.trailingZeros = 0
    globals.bitLength = 24
    print "Normal Case, 4 fields:"
    runTest()
    print "Output in Hex:"
    runTest(outInHex=True)
    #print "Output swapped:"
    #runTest(outSwapped=True)
    #print "Output in Hex and swapped:"
    #runTest (outInHex=True, outSwapped=True)
    


    
    
    
    
    
def failCases():
    print "stub"

def proxSpecificCases():
    print "stub"

def mifareSpecificCases():
    print "stub"

def seosSpecificCases():
    print "stub"

def iClassSpecificCases():
    print "stub"


def cleanUp():
    subprocess.call("rm -rf 5427ckApps", shell=True)

