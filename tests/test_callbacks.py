from __future__ import (print_function, absolute_import)
import sys
import caffi.ca as ca

# check for status code
def check_status(status):
    if status != ca.ECA.NORMAL:
        print(ca.message(status))
        sys.exit(1)

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


def accessCB(epicsArgs, userArgs):
    print('access rights callback')
    print(epicsArgs)


# exception callback
status = ca.add_exception_event(exceptionCB)
check_status(status)

# create channel
status, chid = ca.create_channel('cacalc', callback=connectCB)
check_status(status)

# since a callback is used, ca.pend_io will return immediately.
# ca.pend_event will process background activities
ca.pend_event(2)
if ca.state(chid) != ca.ChannelState.CONN:
    sys.exit(1)

# access rights callback
status = ca.replace_access_rights_event(chid, accessCB)
check_status(status)

# monitor callback
status, evid = ca.create_subscription(chid, monitorCB, (1, 2, 3))
check_status(status)

# push these requests to server
ca.flush_io()

# put callback
status = ca.put(chid, [60, 50, 40], callback=putCB, args=(1, 2, 3))
check_status(status)
ca.flush_io()

# get callback, the dbrvalue is dummy since callback is used
status, dbrvalue = ca.get(chid, callback=getCB, args=(1, 2, 3))
check_status(status)
ca.flush_io()

# dump out the ca context
print('='*80)
ca.show_context(level=2)
print('='*80)

# wait for callbacks to happen
ca.pend_event(5)

# clean up
ca.clear_subscription(evid)
ca.clear_channel(chid)
ca.flush_io()