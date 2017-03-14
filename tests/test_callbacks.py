from __future__ import (print_function, absolute_import)
from pprint import pprint
import caffi.ca as ca


def exceptionCB(epicsArgs):
    pprint('exception callback')
    pprint(epicsArgs, indent=4)


def connectCB(epicsArgs):
    pprint('connect callback')
    pprint(epicsArgs, indent=4)


def putCB(epicsArgs):
    pprint('put callback')
    pprint(epicsArgs, indent=4)


def getCB(epicsArgs):
    pprint('get callback')
    pprint(epicsArgs, indent=4)


def monitorCB(epicsArgs):
    pprint('monitor callback')
    pprint(epicsArgs, indent=4)


def accessCB(epicsArgs):
    pprint('access rights callback')
    pprint(epicsArgs, indent=4)


# exception callback
status = ca.add_exception_event(exceptionCB)
assert status == ca.ECA.NORMAL

# connection callback
status, chid = ca.create_channel('cawave', callback=connectCB)
assert status == ca.ECA.NORMAL

# since a callback is used, ca.pend_io will return immediately.
# ca.pend_event will process background activities
ca.pend_event(2)
assert ca.state(chid) == ca.ChannelState.CONN

# access rights callback
status = ca.replace_access_rights_event(chid, accessCB)
assert status == ca.ECA.NORMAL

# monitor callback
status, evid = ca.create_subscription(chid, monitorCB, count=3)
assert status == ca.ECA.NORMAL

# push request to server
ca.flush_io()

# put callback
status = ca.put(chid, [60, 50, 40], callback=putCB)
assert status == ca.ECA.NORMAL

# push these requests to server
ca.flush_io()

# get callback, the dbrvalue is None since callback is used
status, dbrvalue = ca.get(chid, callback=getCB, count=3)
assert status == ca.ECA.NORMAL

ca.flush_io()

# wait for callbacks to happen
ca.pend_event(2)

# clean up
ca.clear_subscription(evid)
ca.clear_channel(chid)
ca.flush_io()
ca.destroy_context()
