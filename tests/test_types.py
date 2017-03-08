from __future__ import print_function
import sys
import caffi.ca as ca

pvs = {}
vals = {}

# check for status code
def check_status(status):
    if status != ca.ECA.NORMAL:
        print(ca.message(status))
        sys.exit(1)

# create preemptive enabled context
status = ca.create_context(True)
check_status(status)

# create channels
for name in ['cawaves', 'cawaveh', 'cawavef',  'cawavec', 'cawavel','cawave', 'cabo']:
    status, chid = ca.create_channel(name)
    if status == ca.ECA.NORMAL:
        pvs[name] = chid

status = ca.pend_io(3)
check_status(status)

# put
for name, chid in pvs.items():
    if ca.field_type(chid) == ca.DBF.STRING:
        ca.put(chid, [b'1',b'2',b'3', b'4'])
    else:
        ca.put(chid, [1, 2, 3, 4])

ca.flush_io()

# get
for name, chid in pvs.items():
    status, value = ca.get(chid)
    if status == ca.ECA.NORMAL:
        vals[name] = value

# wait for get completion
status = ca.pend_io(3)
check_status(status)

# dump value
for name, value in vals.items():
    print(name, ca.field_type(pvs[name]), value.get())

# clear channels
for name, chid in pvs.items():
    ca.clear_channel(chid)

ca.flush_io()

# destroy context
ca.destroy_context()
