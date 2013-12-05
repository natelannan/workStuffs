#! /bin/python
'''
**************************************************************************
omnikey5427test.py



For questions or concerns, contact Nate Lannan (nlannan@lexmark.com) 

Copyright (c) 2013 Lexmark International, Inc.
All rights reserved
**************************************************************************
'''

import sys, os
from omnikeyFuns import *
import globals


#args = ipAddress, printerFamily, telnetPort
def testMatrix(args):
    if(len(args)< 1 or len(args) > 3):
       usage() 

    globals.init(args)

    getApps()
    installApps()
    if (not(checkApps())):
       print "Required apps are not present. \nPlease install readertest.fls, " \
             "omnikey5427ck.fls, and cardslotsim.fls.  "
       cleanUp()
       sys.exit(0)
    
    
    os.system('read -s -n 1 -p "Connect Omnikey 5427ck reader if not connected ' +
              'and place a HID Prox card on top of the reader.  Press any key to continue..."')
    print
    
    #Prox
    globals.activeCard = 'Prox'
    successCases()
    failCases()
    proxSpecificCases()
    sys.exit(0)

    os.system('read -s -n 1 -p "Place a Mifare card on top of the reader.  ' \
              'Press any key to continue..."')
    print

    #Mifare
    globals.activeCard = 'Mifare'
    successCases()
    failCases()
    proxSpecificCases()

    os.system('read -s -n 1 -p "Place a iClass card on top of the reader.  ' \
              'Press any key to continue..."')
    print

    #iClass
    globals.activeCard = 'iClass'
    successCases()
    failCases()
    proxSpecificCases()

    os.system('read -s -n 1 -p "Place a Seos card on top of the reader.  ' \
              'Press any key to continue..."')
    print

    #Seos
    globals.activeCard = 'Seos'
    successCases()
    failCases()
    proxSpecificCases()

    cleanUp()


def usage():
    print "usage:  omnikey5427test.py <ipaddress> <printer family> <telnet port>"
    print "IPADDRESS:"
    print "\tipaddress of device under test"
    print "PRINTER FAMILY:"
    print "\tprinter family of device under test.  Valid input - "
    print "\t\tHS - Homestretch (default)"
    print "\t\tWC - Winner's Circle"
    print "TELNET PORT:"
    print "\tport to communicate with cardslotsim and trigger a card event. default port is 13002\n"
    print ("This program will test a matrix of success cases and failure cases for the Omnikey5427ck \n" \
           "driver.  The program will prompt the user to place and remove the following card types from \n" \
           "on top of the omnikey 5427ck reader: Prox, Seos, iClass, and Mifare.  The program installs \n" \
           "the omnikey5427ck reader as well as the cardslotsim app to trigger card events and \n" \
           "readertest.fls to check card values.  The only necessary argument is an ipaddress.  If only \n" \
           "an ipaddress is given the defaults will be used.  This program must be run from a linux machine \n" \
           "with python 2.7.3 installed.\n")
    sys.exit(0)
    
    


if __name__ == '__main__':
    testMatrix(sys.argv[1:])
