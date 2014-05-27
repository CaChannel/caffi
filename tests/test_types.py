from __future__ import print_function
from caffi.ca import *

pvs = {}
vals = {}

create_context(True)

for name in ['cawaves', 'cawaveh', 'cawavef',  'cawavec', 'cawavel','cawave']:
    chid = create_channel(name)
    pvs[name] = chid

status = pend_io(3)
if status != ECA_NORMAL:
    print(message(status))

# put
for name, chid in pvs.items():
    if field_type(chid) == DBF_STRING:
        put(chid, [b'1',b'2',b'3', b'4'])
    else:
        put(chid, [1, 2, 3, 4])

flush_io()

# get
for name, chid in pvs.items():
    value = get(chid)
    vals[name] = value

status = pend_io(3)
if status != ECA_NORMAL:
    print(message(status))

# dump value
for name, value in vals.items():
    print(name, value.get())