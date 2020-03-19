"""
functions to print colored text in terminal
"""

CEND      = '\33[0m'
CBOLD     = '\33[1m'
CITALIC   = '\33[3m'
CURL      = '\33[4m'
CBLINK    = '\33[5m'
CBLINK2   = '\33[6m'
CSELECTED = '\33[7m'

CBLACK  = '\33[30m'
CRED    = '\33[31m'
CGREEN  = '\33[32m'
CYELLOW = '\33[33m'
CBLUE   = '\33[34m'
CVIOLET = '\33[35m'
CBEIGE  = '\33[36m'
CWHITE  = '\33[37m'

CBLACKBG  = '\33[40m'
CREDBG    = '\33[41m'
CGREENBG  = '\33[42m'
CYELLOWBG = '\33[43m'
CBLUEBG   = '\33[44m'
CVIOLETBG = '\33[45m'
CBEIGEBG  = '\33[46m'
CWHITEBG  = '\33[47m'

CGREY    = '\33[90m'
CRED2    = '\33[91m'
CGREEN2  = '\33[92m'
CYELLOW2 = '\33[93m'
CBLUE2   = '\33[94m'
CVIOLET2 = '\33[95m'
CBEIGE2  = '\33[96m'
CWHITE2  = '\33[97m'

CGREYBG    = '\33[100m'
CREDBG2    = '\33[101m'
CGREENBG2  = '\33[102m'
CYELLOWBG2 = '\33[103m'
CBLUEBG2   = '\33[104m'
CVIOLETBG2 = '\33[105m'
CBEIGEBG2  = '\33[106m'
CWHITEBG2  = '\33[107m'

def fg_green(*str):
    return (CGREEN + ' '.join(str) + CEND)

def fg_red(*str):
    return (CRED + ' '.join(str) + CEND)

def fg_red2(*str):
    return (CRED2 + ' '.join(str) + CEND)

def fg_yellow(*str):
    return (CYELLOW + ' '.join(str) + CEND)

def fg_yellow2(*str):
    return (CYELLOW2 + ' '.join(str) + CEND)

def fg_blue(*str):
    return (CBLUE + ' '.join(str) + CEND)

def fg_voilet(*str):
    return (CVIOLET + ' '.join(str) + CEND)

def fg_beige(*str):
    return (CBEIGE + ' '.join(str) + CEND)

def bg_green(*str):
    return (CGREENBG + ' '.join(str) + CEND)

def bg_red(*str):
    return (CREDBG + ' '.join(str) + CEND)

def bg_yellow(*str):
    return (CYELLOWBG + ' '.join(str) + CEND)

def bg_blue(*str):
    return (CBLUEBG + ' '.join(str) + CEND)

def bg_voilet(*str):
    return (CVIOLETBG + ' '.join(str) + CEND)

def bg_beige(*str):
    return (CBEIGEBG + ' '.join(str) + CEND)

def bg_white(*str):
    return (CWHITEBG + ' '.join(str) + CEND)
