

def init(args):
    global ipAddress, printerFamily, telnetPort
    global cardNumber, bitLength, cardDataFormat, activeCard, trailingZeros
    global outFileName, customFields, WINSHARE, sendtcp, suppress
    if (len(args)==1):
        ipAddress = args[0]
        printerFamily='HS'
        telnetPort='13002'
    if (len(args)==2):
        ipAddress = args[0]
        printerFamily = args[1]
        telnetPort='13002'
    if (len(args)==3):
        ipAddress = args[0]
        printerFamily = args[1]
        telnetPort = args[2]
    cardNumber = '1012345'
    bitLength = 26
    #H01 = 26
    #H02 = 37
    #H04 = 37
    #H20 = 32
    #100 = 35
    cardDataFormat = ['iClassFormat = 1', 'MifareFormat = 2', 'ProxFormat = 1', 'SeosFormat = 20']
    activeCard = 'Prox'
    trailingZeros = 6
    outFileName = 'omnikeyTest.ini'
    customFields = [(16,8),(0,16),(0,0),(0,0)]
    WINSHARE="\\\\\\\\germany.lxbp.ftlesx.rds.lexmark.com\\\\homefs"
    sendtcp="/users/nlannan/bin/sendtcp"
    suppress = False
