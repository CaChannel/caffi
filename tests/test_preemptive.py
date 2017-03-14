from __future__ import print_function
import time
import caffi.ca as ca

# enable preemptive callback
status = ca.create_context(True)
assert status == ca.ECA.NORMAL

# create channel
status, chid = ca.create_channel('cacalc')
assert status == ca.ECA.NORMAL

# wait for connection
status = ca.pend_io(2)
assert status == ca.ECA.NORMAL

def monitor(epics_arg):
    print(epics_arg['value'])

status, evid = ca.create_subscription(chid, monitor)
assert status == ca.ECA.NORMAL
ca.flush_io()

# with preemptive callback enabled, monitor callback happens even if we are sleeping
time.sleep(2)

ca.clear_subscription(evid)
ca.clear_channel(chid)
ca.flush_io()

# destroy context
ca.destroy_context()
