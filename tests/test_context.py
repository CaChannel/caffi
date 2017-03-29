from __future__ import (print_function, absolute_import)
import threading
import caffi.ca as ca


# each thread creates its own context
def independent_context_thread(pv):
    status = ca.create_context(True)
    assert status == ca.ECA.NORMAL

    # exception callback
    status = ca.add_exception_event(lambda arg: print(arg['ctx']))
    assert status == ca.ECA.NORMAL

    # create channel
    status, chid = ca.create_channel(pv)
    assert status == ca.ECA.NORMAL

    status = ca.pend_io(5)
    assert status == ca.ECA.NORMAL

    ca.pend_event(1)

    ca.destroy_context()


def test_independent_contexts():
    # create a new thread for each PV
    tids = []
    for pv in ['catest', 'cawave', 'cabo', 'cawaves', 'cawavec']:
        tid = threading.Thread(target=independent_context_thread, args=(pv,))
        tids.append(tid)
        tid.start()

    for tid in tids:
        tid.join()


def shared_context_thread(context, pv):
    status = ca.attach_context(context)
    assert status == ca.ECA.NORMAL

    # create channel
    status, chid = ca.create_channel(pv)
    assert status == ca.ECA.NORMAL

    status = ca.pend_io(5)
    assert status == ca.ECA.NORMAL

    ca.pend_event(1)

    ca.detach_context()


def test_shared_contexts():
    # create a shared context
    status = ca.create_context(True)
    assert status == ca.ECA.NORMAL

    context = ca.current_context()
    assert context is not None

    # exception callback
    status = ca.add_exception_event(lambda arg: print(arg['ctx']))
    assert status == ca.ECA.NORMAL

    # use the shared context in new threads
    tids = []
    for pv in ['catest', 'cawave', 'cabo', 'cawaves', 'cawavec']:
        tid = threading.Thread(target=shared_context_thread, args=(context, pv))
        tids.append(tid)
        tid.start()

    for tid in tids:
        tid.join()

    # destroy the context
    ca.destroy_context()
