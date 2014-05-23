from __future__ import print_function
import threading
from caffi.ca import *
import time

create_context(True)
ctx = current_context()

chid = create_channel('catest')
pend_io(3)

put(chid, 0)
flush_io()

def monitor(epics_arg, user_arg):
    print(epics_arg['value']['stamp'], epics_arg['value']['value'])

create_subscription(chid, monitor, dbrtype=DBR_TIME_DOUBLE)

def thread_one():
    status = attach_context(ctx)
    for i in range(100):
        time.sleep(0.01)
        put(chid,  2 * i)
        flush_io()

    show_context(current_context(),1)

def thread_two():
    status = attach_context(ctx)
    for i in range(100):
        time.sleep(0.01)
        put(chid, 2 * i + 1)
        flush_io()

    show_context(current_context(), 1)

def thread_three():
    while True:
        poll()

tid1 = threading.Thread(target=thread_one)
tid2 = threading.Thread(target=thread_two)
tid3 = threading.Thread(target=thread_three)
tid3.setDaemon(True)
tid1.start()
tid2.start()
tid3.start()
tid1.join()
tid2.join()
