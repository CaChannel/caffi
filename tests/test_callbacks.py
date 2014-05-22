from __future__ import (print_function, absolute_import)

from caffi.ca import *

def exceptionCB(epicsArgs, userArgs):
    print('exception callback')
    print('    ', epicsArgs)
    print('    ', userArgs)


def connectCB(epicsArgs, userArgs):
    print('connect callback')
    print('    ', epicsArgs)
    print('    ', userArgs)


def putCB(epicsArgs, userArgs):
    print('put callback')
    print('    ', epicsArgs)
    print('    ', userArgs)


def getCB(epicsArgs, userArgs):
    print('get callback')
    print('    ', epicsArgs)
    print('    ', userArgs)


def monitorCB(epicsArgs, userArgs):
    print('monitor callback')
    print('    ', epicsArgs)
    print('    ', userArgs)

add_exception_event(exceptionCB)

chid = create_channel('cacalc', callback=connectCB)
status = pend_event(2)

evid = create_subscription(chid, monitorCB, (1, 2, 3))
pend_event(1)

put(chid, [60, 50, 40], callback=putCB, args=(1, 2, 3))
pend_event(2)

get(chid, callback=getCB, args=(1, 2, 3))
pend_event(2)

show_context(current_context(), level=2)

clear_subscription(evid)
status = clear_channel(chid)
