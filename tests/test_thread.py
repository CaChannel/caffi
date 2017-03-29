from __future__ import print_function
import datetime
import threading
import time
import caffi.ca as ca

def setup_module(module):
    # create explicitly a preemptive enabled context
    # so that it can attached in other threads
    status = ca.create_context(True)
    assert status == ca.ECA.NORMAL

    global ctx
    ctx = ca.current_context()

    # create channel
    global chid
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
        print(datetime.datetime.fromtimestamp(epics_arg['value']['stamp']['timestamp']), epics_arg['value']['value'])

    global evid
    status, evid = ca.create_subscription(chid, monitor, chtype=ca.DBR.TIME_DOUBLE)


def thread_even():
    status = ca.attach_context(ctx)
    assert status == ca.ECA.NORMAL

    for i in range(0, 200, 2):
        ca.put(chid,  i)
        ca.flush_io()


def thread_odd():
    status = ca.attach_context(ctx)
    assert status == ca.ECA.NORMAL

    for i in range(1, 200, 2):
        ca.put(chid, i)
        ca.flush_io()


def test_thread():
    tid1 = threading.Thread(target=thread_odd)
    tid2 = threading.Thread(target=thread_even)
    tid1.start()
    tid2.start()
    tid1.join()
    tid2.join()

    # wait for the last monitor to arrive
    time.sleep(2)

    # the value should be either 199 or 198, depending on which thread ends last
    status, value = ca.get(chid)
    assert status == ca.ECA.NORMAL

    status = ca.pend_io(3)
    assert status == ca.ECA.NORMAL

    assert value.get() in [198, 199]


def teardown_module(module):
    # clear subscription
    ca.clear_subscription(evid)

    # clear channel
    ca.clear_channel(chid)

    ca.flush_io()

    # destroy context
    ca.destroy_context()
