from __future__ import print_function
import time
from caffi.ca import *

# enable preemptive callback
create_context(True)

chid = create_channel('cacalc')
pend_io(2)

def monitor(epics_arg, user_arg):
    print(epics_arg['value'])

evid = create_subscription(chid, monitor)
flush_io()

# with preemptive callback enabled, monitor callback happens even if we are sleeping
time.sleep(5)

clear_subscription(evid)
clear_channel(chid)
flush_io()
