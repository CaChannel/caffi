from __future__ import print_function
import threading
import time
import caffi.ca as ca


# create explicitly a preemptive enabled context
# so that it can attached in other threads
status = ca.create_context(True)
assert status == ca.ECA.NORMAL

ctx = ca.current_context()

# create channel
status, chid = ca.create_channel('catest')
assert status == ca.ECA.NORMAL

# wait for connections
status = ca.pend_io(3)
assert status == ca.ECA.NORMAL

# put
status = ca.put(chid, 0)
assert status == ca.ECA.NORMAL

ca.flush_io()

def monitor(epics_arg):
    print(epics_arg['value']['stamp'], epics_arg['value']['value'])

status, evid = ca.create_subscription(chid, monitor, chtype=ca.DBR.TIME_DOUBLE)

def thread_one():
    status = ca.attach_context(ctx)
    if status != ca.ECA.NORMAL:
        print(ca.message(status))
        return
    for i in range(0, 200, 2):
        ca.put(chid,  i)
        ca.flush_io()

def thread_two():
    status = ca.attach_context(ctx)
    if status != ca.ECA.NORMAL:
        print(ca.message(status))
        return
    for i in range(1, 200, 2):
        ca.put(chid, i)
        ca.flush_io()

# this thread is not necessary if preemptive is enabled
def thread_three():
    while True:
        ca.poll()

tid1 = threading.Thread(target=thread_one)
tid2 = threading.Thread(target=thread_two)
tid3 = threading.Thread(target=thread_three)
tid3.setDaemon(True)
tid1.start()
tid2.start()
tid3.start()
tid1.join()
tid2.join()

# wait for the last monitor to arrive
time.sleep(2)

# clear subscription
ca.clear_subscription(evid)

# clear channel
ca.clear_channel(chid)

ca.flush_io()

# destroy context
ca.destroy_context()
