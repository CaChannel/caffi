from __future__ import print_function

from caffi.ca import *

# DBF_ENUM
chid = create_channel('cabo')

status = pend_io(2)
if status != ECA_NORMAL:
    print(message(status))

for dbrtpye in [DBR_ENUM, DBR_STS_ENUM, DBR_TIME_ENUM,
                DBR_GR_ENUM, DBR_CTRL_ENUM]:
    value = get(chid, dbrtpye)
    status = pend_io(2)
    if status != ECA_NORMAL:
        print(message(status))
    else:
        print(value.get())

clear_channel(chid)


# DBF_DOUBLE can be read by any DBR types
chid = create_channel('catest')

status = pend_io(2)
if status != ECA_NORMAL:
    print(message(status))

for dbrtype in DBR:
    if dbrtype == DBR.INVALID:
        continue
    value = get(chid, dbrtype)
    status = pend_io(2)
    if status != ECA_NORMAL:
        print(message(status))
    else:
        print(dbrtype)
        print('    ', value.get())

clear_channel(chid)
