from __future__ import print_function
import sys
import caffi.ca as ca

# check for status code
def check_status(status):
    if status != ca.ECA.NORMAL:
        print(ca.message(status))
        sys.exit(1)

# create channel
status, chid = ca.create_channel('catest')
check_status(status)

# wait for connection
status = ca.pend_io(2)
check_status(status)


# DBF_DOUBLE can be read by any DBR types
for dbrtype in ca.DBR:
    # these are not for valid types for ca get
    if dbrtype in [ca.DBR.INVALID, ca.DBR.PUT_ACKS, ca.DBR.PUT_ACKT] :
        continue

    status, dbrvalue = ca.get(chid, dbrtype)
    if status != ca.ECA.NORMAL:
        continue

    status = ca.pend_io(2)
    if status != ca.ECA.NORMAL:
        print(ca.message(status))
    else:
        print(dbrtype)
        print('    ', dbrvalue.get())

ca.clear_channel(chid)

# destroy context
ca.destroy_context()
