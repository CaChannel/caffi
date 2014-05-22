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

gid = sg_create()

# put
for name, chid in pvs.items():
    if field_type(chid) == DBF_STRING:
        sg_put(gid, chid, ['1','2','3', '4'])
    else:
        sg_put(gid, chid, [1, 2, 3, 4])

flush_io()

status = sg_block(gid, 5)
if status != ECA_NORMAL:
    print(message(status))

# get
for name, chid in pvs.items():
    value = sg_get(gid, chid)
    vals[name] = value

flush_io()

status = sg_block(gid, 0.1)
if status != ECA_NORMAL:
    print(message(status))

# dump value
for name, value in vals.items():
    chid = pvs[name]
    type = field_type(chid)
    count = element_count(chid)
    print(name, format_dbr(type, count, value))
