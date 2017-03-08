from __future__ import print_function
import time
import sys
import caffi.ca as ca

# check for status code
def check_status(status):
    if status != ca.ECA.NORMAL:
        print(ca.message(status))
        sys.exit(1)

# enable preemptive callback
status = ca.create_context(True)
check_status(status)

# create channel
status, chid = ca.create_channel('cacalc')
check_status(status)

# wait for connection
status = ca.pend_io(2)
check_status(status)

def monitor(epics_arg):
    print(epics_arg['value'])

status, evid = ca.create_subscription(chid, monitor)
check_status(status)
ca.flush_io()

# with preemptive callback enabled, monitor callback happens even if we are sleeping
time.sleep(5)

ca.clear_subscription(evid)
ca.clear_channel(chid)
ca.flush_io()

# destroy context
ca.destroy_context()
