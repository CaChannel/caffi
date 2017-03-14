from __future__ import print_function
import caffi.ca as ca

# create channel
status, chid = ca.create_channel('catest')
assert status == ca.ECA.NORMAL

# wait for connection
status = ca.pend_io(2)
assert status == ca.ECA.NORMAL


for dbrtype in ca.DBR:
    # these are not for valid types for ca get
    if dbrtype in [ca.DBR.INVALID, ca.DBR.PUT_ACKS, ca.DBR.PUT_ACKT]:
        continue

    status, dbrvalue = ca.get(chid, dbrtype)
    assert status == ca.ECA.NORMAL

    status = ca.pend_io(2)
    assert status == ca.ECA.NORMAL

# clear channel
ca.clear_channel(chid)

# destroy context
ca.destroy_context()
