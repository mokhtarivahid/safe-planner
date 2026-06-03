"""
functions to print colored text in terminal.

ANSI escapes are suppressed automatically when stdout is not a TTY (e.g. when
the output is being piped to a file), and can be force-enabled/disabled via
the ``SP_COLOR`` environment variable (``always`` / ``never`` / ``auto``).
Use :func:`set_enabled` from code to toggle at runtime.
"""

import os as _os
import sys as _sys


def _detect() -> bool:
    mode = _os.environ.get("SP_COLOR", "auto").lower()
    if mode in ("always", "1", "true", "yes"):
        return True
    if mode in ("never", "0", "false", "no"):
        return False
    # 'auto'
    if _os.environ.get("NO_COLOR"):
        return False
    try:
        return _sys.stdout.isatty()
    except Exception:
        return False


_ENABLED = _detect()


def set_enabled(value: bool) -> None:
    """Force-enable or disable ANSI colouring for the current process."""
    global _ENABLED
    _ENABLED = bool(value)


def enabled() -> bool:
    return _ENABLED


def _wrap(code: str, parts):
    text = ' '.join(parts)
    if not _ENABLED:
        return text
    return code + text + CEND


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

def fg_green(*s):    return _wrap(CGREEN,    s)
def fg_green2(*s):   return _wrap(CGREEN2,   s)
def fg_red(*s):      return _wrap(CRED,      s)
def fg_red2(*s):     return _wrap(CRED2,     s)
def fg_yellow(*s):   return _wrap(CYELLOW,   s)
def fg_yellow2(*s):  return _wrap(CYELLOW2,  s)
def fg_blue(*s):     return _wrap(CBLUE,     s)
def fg_voilet(*s):   return _wrap(CVIOLET,   s)
def fg_violet(*s):   return _wrap(CVIOLET,   s)  # alias for the correct spelling
def fg_beige(*s):    return _wrap(CBEIGE,    s)
def bg_green(*s):    return _wrap(CGREENBG,  s)
def bg_green2(*s):   return _wrap(CGREENBG2, s)
def bg_red(*s):      return _wrap(CREDBG,    s)
def bg_yellow(*s):   return _wrap(CYELLOWBG, s)
def bg_blue(*s):     return _wrap(CBLUEBG,   s)
def bg_voilet(*s):   return _wrap(CVIOLETBG, s)
def bg_violet(*s):   return _wrap(CVIOLETBG, s)
def bg_beige(*s):    return _wrap(CBEIGEBG,  s)
def bg_white(*s):    return _wrap(CWHITEBG,  s)

