#! /bin/python

import subprocess
import shlex
import re
import telnetlib
from time import sleep
from iniCreator import *
import globals




def getApps():
    subprocess.call("smbclient -U autouser " + WINSHARE + " -c \"get nlannan\\5427ckApps.zip\" Fn4WNus2T", shell=True)
    subprocess.call("unzip -d 5427ckApps nlannan\\\\5427ckApps.zip", shell=True)
    subprocess.call("rm nlannan\\\\5427ckApps.zip", shell=True)

def installApps():
    subprocess.call (sendtcp+" " + globals.ipAddress +" "+ "5427ckApps/cardslotsim.fls", shell=True)
    subprocess.call (sendtcp+" " + globals.ipAddress +" "+ "5427ckApps/readertest.fls", shell=True)
    subprocess.call (sendtcp+" " + globals.ipAddress +" "+ "5427ckApps/omnikey5427ck.fls", shell=True)
    sleep(10)

def checkApps():
    curlSessionCmd = "curl http://"+globals.ipAddress+"/cgi-bin/dynamic/printer/config/reports/MenusPage.html"
    curlSessionArgs= shlex.split(curlSessionCmd)
    curlSession, err  = subprocess.Popen(curlSessionArgs,stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    print globals.ipAddress
    cardslotPattern = re.compile(r".*Card Slot Simulation.*")
    omnikeyPattern = re.compile(r".*Omnikey 5427ck Reader Driver.*")
    readerPattern = re.compile(r".*Reader Test.*")
    cardslotLine = cardslotPattern.search(curlSession)
    print cardslotLine
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

def runTest():
    loadIni()
    deleteEsfLog()
    swipeCard()
    userID = parseEsfLog()
    if int(userID) == cardNumber:
        print "cardNumber = \t"+ str(cardNumber)+"\nuserID = \t"+userID+"\n\nPASS"
    else:
        print "cardNumber = \t"+ str(cardNumber)+"\nuserID = \t"+userID+"\n\nFAIL"


def loadIni():
    iniArgs = [cardNumber, bitLength, cardDataFormat, activeCard, trailingZeros, outFileName, customFields]

    iniCreator(iniArgs)

    if (printerFamily == 'HS'):
        curlSessionCmd = "curl -D - \"http://"+ipAddress+"/cgi-bin/direct/printer/prtappauth/admin/adminservlet\""
    elif (printerFamily == 'WC'):
        curlSessionCmd = "curl -D - \"http://"+ipAddress+"/cgi-bin/direct/printer/prtappauth/admin/adminservlet" \
                         "?SelectedAppsNames=omnikey5427ckdriver\""
    else:
        print "Printer Family not recognized."
        sys.exit(1)
    curlSessionArgs= shlex.split(curlSessionCmd)
    curlSession, err  = subprocess.Popen(curlSessionArgs,stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    cookiePattern = re.compile(r"Set-Cookie: JSESSIONID=([^;]*).*")
    cookieLine = cookiePattern.search(curlSession)
    if cookieLine:
        sessionValue = cookieLine.group(1)
    else:
        print "could not find Cookie for session start"
        sys.exit(1)
    curlStartCmd = "curl \'http://"+ipAddress+"/cgi-bin/direct/printer/prtappauth/admin/appservlet?" \
                   "SelectedAppsNames=omnikey5427ckdriver\' -H \'Referer: http://"+ipAddress+ \
                   "/cgi-bin/direct/printer/prtappauth/admin/\' -H \'Cookie: JSESSIONID="+sessionValue+ \
                   "\' -H \'Connection: keep-alive\'"
    curlStartArgs=shlex.split(curlStartCmd)
    curlStart, err = subprocess.Popen(curlStartArgs, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()

    curlSendCmd = "curl -H \"Cookie: JSESSIONID="+sessionValue+"\" -F settings.inifile=@"+outFileName+" http://" \
    +ipAddress+"/cgi-bin/direct/printer/prtappauth/admin/configureokservlet"
    curlSendArgs= shlex.split(curlSendCmd)
    curlSend, err = subprocess.Popen(curlSendArgs, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()

def deleteEsfLog():
    curlDebugCmd = "curl \'http://"+ipAddress+"/cgi-bin/direct/printer/prtappse/semenu?loglevel=debug&page=setloglevel\'"
    curlDebugArgs = shlex.split(curlDebugCmd)
    curlDebug, err = subprocess.Popen(curlDebugArgs, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    curlClearCmd = "curl \'http://"+ipAddress+"/cgi-bin/direct/printer/prtappse/semenu?clearlogconfirmation=Yes&page=clearlog\'"
    curlClearArgs = shlex.split(curlClearCmd)
    curlClear, err = subprocess.Popen(curlClearArgs, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()

def swipeCard():
    tn =telnetlib.Telnet(ipAddress, telnetPort)
    tn.write('i')
    sleep(2)
    tn.write('o')
    tn.close()

def parseEsfLog():
    esfLog = "http://"+ipAddress+"/cgi-bin/script/printer/prtapplog"
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
    global cardNumber, bitLength, cardDataFormat
    global trailingZeros
    
    #RAW
    cardDataFormat = ['iClassFormat = 0', 'MifareFormat = 0', 'ProxFormat = 0', 'SeosFormat = 0']
    runTest()

    #H10301
    bitLength = 26
    trailingZeros = 6
    cardDataFormat = ['iClassFormat = 1', 'MifareFormat = 1', 'ProxFormat = 1', 'SeosFormat = 1']
    runTest()

    #H10302
    bitLength = 37
    trailingZeros = 3
    cardDataFormat = ['iClassFormat = 2', 'MifareFormat = 2', 'ProxFormat = 2', 'SeosFormat = 2']
    runTest()

    #H10304
    bitLength = 37
    trailingZeros = 3
    cardDataFormat = ['iClassFormat = 4', 'MifareFormat = 4', 'ProxFormat = 4', 'SeosFormat = 4']
    runTest()

    #H10320
    bitLength = 32
    trailingZeros = 0
    cardDataFormat = ['iClassFormat = 20', 'MifareFormat = 20', 'ProxFormat = 20', 'SeosFormat = 20']
    runTest()

    #Corp 1000
    bitLength = 35
    trailingZeros = 5
    cardDataFormat = ['iClassFormat = 100', 'MifareFormat = 100', 'ProxFormat = 100', 'SeosFormat = 100']
    cardNumber = 101234567
    runTest()

    #Auto
    cardDataFormat = ['iClassFormat = 254', 'MifareFormat = 254', 'ProxFormat = 254', 'SeosFormat = 254']
    runTest()

    #Customer Defined

    
    
    
    
    
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

