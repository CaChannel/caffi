from __future__ import (print_function, absolute_import)
import threading
from pprint import pprint
import caffi.ca as ca


def setup_module(module):
    # create context
    status = ca.create_context(True)
    assert status == ca.ECA.NORMAL


def teardown_module(module):
    # destroy context
    ca.destroy_context()


def exceptionCB(epicsArgs):
    pprint('exception callback')
    pprint(epicsArgs, indent=4)


def connectCB(epicsArgs, event):
    pprint('connect callback')
    pprint(epicsArgs, indent=4)
    event.set()


def putCB(epicsArgs, event):
    pprint('put callback')
    pprint(epicsArgs, indent=4)
    event.set()


def getCB(epicsArgs, event):
    pprint('get callback')
    pprint(epicsArgs, indent=4)
    event.set()


def monitorCB(epicsArgs, event):
    pprint('monitor callback')
    pprint(epicsArgs, indent=4)
    event.set()


def accessCB(epicsArgs, event):
    pprint('access rights callback')
    pprint(epicsArgs, indent=4)
    event.set()


def test_callbacks():
    # events to notify callback has be called
    connect_done = threading.Event()
    get_done = threading.Event()
    put_done = threading.Event()
    access_done = threading.Event()
    monitor_done = threading.Event()

    # exception callback
    status = ca.add_exception_event(exceptionCB)
    assert status == ca.ECA.NORMAL

    # connection callback
    status, chid = ca.create_channel('cawave', callback=lambda arg: connectCB(arg, connect_done))
    assert status == ca.ECA.NORMAL

    # access rights callback
    status = ca.replace_access_rights_event(chid, lambda arg: accessCB(arg, access_done))
    assert status == ca.ECA.NORMAL

    # since preemptive context is used, the background activities happen asynchronously
    connect_done.wait(5)
    assert ca.state(chid) == ca.ChannelState.CONN

    # access callback is called whenever connection changed
    access_done.wait(5)
    assert ca.read_access(chid)
    assert ca.write_access(chid)

    # monitor callback
    status, evid = ca.create_subscription(chid, callback=lambda arg: monitorCB(arg, monitor_done), count=3)
    assert status == ca.ECA.NORMAL

    # push request to server
    ca.flush_io()

    # access callback is called once it is registered
    monitor_done.wait(5)

    # put callback
    status = ca.put(chid, [60, 50, 40], callback=lambda arg: putCB(arg, put_done))
    assert status == ca.ECA.NORMAL

    # push these requests to server
    ca.flush_io()

    # wait for put callback
    put_done.wait(5)

    # get callback, the dbrvalue is None since callback is used
    status, dbrvalue = ca.get(chid, callback=lambda arg: getCB(arg, get_done), count=3)
    assert status == ca.ECA.NORMAL

    ca.flush_io()

    # wait for callbacks to happen
    get_done.wait(5)

    # exception callback
    status = ca.add_exception_event()
    assert status == ca.ECA.NORMAL

    # clean up
    ca.clear_subscription(evid)
    ca.clear_channel(chid)
    ca.flush_io()
