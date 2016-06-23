from __future__ import print_function
import random

import caffi.ca as ca

# create context
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

# create one subscription
def event1(epics_arg):
    print('event1')
    print('    ', epics_arg)

status, evid1 = ca.create_subscription(chid, event1)
assert status == ca.ECA.NORMAL

# create another subscription
def event2(epics_arg):
    print('event2')
    print('    ', epics_arg)

status, evid2 = ca.create_subscription(chid, event2)
assert status == ca.ECA.NORMAL


#
ca.flush_io()

#
ca.pend(1, False)

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

# show the context
ca.show_context(level=1)

# clear the subscription
ca.clear_channel(chid)

#
ca.flush_io()

# destroy context
ca.destroy_context()
