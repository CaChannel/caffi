from __future__ import print_function
import threading
import caffi.ca as ca


def setup_module(module):
    global chid
    # create preemptive enabled context
    status = ca.create_context(True)
    assert status == ca.ECA.NORMAL

    # create channel
    status, chid = ca.create_channel('cacalc')
    assert status == ca.ECA.NORMAL

    # wait for connection
    status = ca.pend_io(2)
    assert status == ca.ECA.NORMAL


def teardown_module(module):
    # clear channel
    ca.clear_channel(chid)
    ca.flush_io()

    # destroy context
    ca.destroy_context()


def test_preemptive():
    global chid

    monitor_event = threading.Event()

    def monitorCB(epics_arg):
        print(epics_arg['value'])
        monitor_event.set()

    status, evid = ca.create_subscription(chid, monitorCB)
    assert status == ca.ECA.NORMAL
    ca.flush_io()

    # wait for 5 times of monitor callbacks
    # because preemptive callback enabled, monitor callback happens
    # even if we are suspended
    for i in range(5):
        monitor_event.wait()
        monitor_event.clear()

    ca.clear_subscription(evid)
