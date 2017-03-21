from __future__ import (print_function, absolute_import)
import threading
from pprint import pprint
import caffi.ca as ca


# each thread creates its own context
def context_thread(pv):
    ca.create_context(True)

    context = ca.current_context()

    # exception callback
    status = ca.add_exception_event(lambda arg: print(pv, arg['ctx']))
    assert status == ca.ECA.NORMAL

    # create channel
    status, chid = ca.create_channel(pv)
    assert status == ca.ECA.NORMAL

    status = ca.pend_io(5)
    assert status == ca.ECA.NORMAL

    ca.pend_event(2)

    ca.destroy_context()


# create a new thread for each PV
tids = []
for pv in ['catest', 'cawave', 'cabo', 'cawaves', 'cawavec']:
    tid = threading.Thread(target=context_thread, args=(pv,))
    tids.append(tid)
    tid.start()


for tid in tids:
    tid.join()
