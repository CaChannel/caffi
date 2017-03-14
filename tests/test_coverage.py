from __future__ import print_function
import random
from pprint import pprint

import caffi.ca as ca

# create preemptive enabled context
ca.create_context(True)

# create channel
status, chid = ca.create_channel('catest')
assert status == ca.ECA.NORMAL

# wait for connections
status = ca.pend_io(2)
assert status == ca.ECA.NORMAL

# information
print("Information")
print("  name:", ca.name(chid))
print("  host:", ca.host_name(chid))
print("  type:", ca.field_type(chid))
print("  count:", ca.element_count(chid))
print("  readable:", ca.read_access(chid))
print("  writable:", ca.write_access(chid))


# create one subscription of plain type
def event1(epics_arg):
    pprint('event1 %s' % epics_arg['type'])
    pprint(epics_arg, indent=4)

status, evid1 = ca.create_subscription(chid, event1)
assert status == ca.ECA.NORMAL


# create another subscription if control type
def event2(epics_arg):
    pprint('event2 %s' % epics_arg['type'])
    pprint(epics_arg, indent=4)

status, evid2 = ca.create_subscription(chid, event2, chtype=ca.DBR_CTRL_DOUBLE)
assert status == ca.ECA.NORMAL


# flush those requests
ca.flush_io()

ca.pend_event(1)

valput = random.random()

# put
status = ca.put(chid, valput)
assert status == ca.ECA.NORMAL

ca.flush_io()

# get
status, value = ca.get(chid)
assert status == ca.ECA.NORMAL

status = ca.pend_io(1)
assert status == ca.ECA.NORMAL

valget = value.get()
assert(valget == valput)

# clear evid1
ca.clear_subscription(evid1)

# clear evid2
ca.clear_subscription(evid2)

# clear the channel
ca.clear_channel(chid)

# flush those requests
ca.flush_io()

# destroy context
ca.destroy_context()
