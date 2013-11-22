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
    globals.init(args)

    getApps()
    installApps()
    print checkApps()
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


    
    


if __name__ == '__main__':
    testMatrix(sys.argv[1:])
