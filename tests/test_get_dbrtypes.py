from __future__ import print_function
import pytest
import threading
import caffi.ca as ca

def setup_module(module):
    global chid
    # create context
    status = ca.create_context(True)
    assert status == ca.ECA.NORMAL

    # create channel
    status, chid = ca.create_channel('catest')
    assert status == ca.ECA.NORMAL

    # wait for connection
    status = ca.pend_io(2)
    assert status == ca.ECA.NORMAL

    # write the value with callback
    # so that we are sure the new value has reached the server
    put_done = threading.Event()
    def put_callback(args):
        put_done.set()

    status = ca.put(chid, 1., callback=put_callback)
    assert status == ca.ECA.NORMAL

    ca.flush_io()
    put_done.wait()

@pytest.mark.parametrize("dbrtype", [
    ca.DBR.STRING, ca.DBR.SHORT, ca.DBR.FLOAT, ca.DBR.ENUM, ca.DBR.CHAR, ca.DBR.LONG, ca.DBR.DOUBLE,
    ca.DBR.STS_STRING, ca.DBR.STS_SHORT, ca.DBR.STS_FLOAT, ca.DBR.STS_ENUM,
    ca.DBR.STS_CHAR, ca.DBR.STS_LONG, ca.DBR.STS_DOUBLE,
    ca.DBR.TIME_STRING, ca.DBR.TIME_SHORT, ca.DBR.TIME_FLOAT, ca.DBR.TIME_ENUM,
    ca.DBR.TIME_CHAR, ca.DBR.TIME_LONG, ca.DBR.TIME_DOUBLE,
    ca.DBR.GR_STRING, ca.DBR.GR_SHORT, ca.DBR.GR_FLOAT, ca.DBR.GR_ENUM,
    ca.DBR.GR_CHAR, ca.DBR.GR_LONG, ca.DBR.GR_DOUBLE,
    ca.DBR.CTRL_STRING, ca.DBR.CTRL_SHORT, ca.DBR.CTRL_FLOAT, ca.DBR.CTRL_ENUM,
    ca.DBR.CTRL_CHAR, ca.DBR.CTRL_LONG, ca.DBR.CTRL_DOUBLE,
    ca.DBR.STSACK_STRING, ca.DBR.CLASS_NAME
    ])
def test_dbrtype(dbrtype):
    global chid
    status, dbrvalue = ca.get(chid, dbrtype)
    assert status == ca.ECA.NORMAL

    status = ca.pend_io(2)
    assert status == ca.ECA.NORMAL

    value = dbrvalue.get()

    # special request type
    if dbrtype == ca.DBR.CLASS_NAME:
        assert value == 'ao'
        return

    if dbrtype == ca.DBR.STSACK_STRING:
        assert value['value'] == '1.0000'
        assert value['ackt'] == 1
        assert value['acks'] == ca.AlarmSeverity.Major
        return

    value_expected = 1
    if dbrtype.isSTRING():
        value_expected = '1.0000'

    if dbrtype.isPlain():
        assert value == value_expected
    else:
        assert value['value'] == value_expected
        assert value['status'] == ca.AlarmCondition.No
        assert value['severity'] == ca.AlarmSeverity.No

        if dbrtype.isTIME():
            assert isinstance(value['stamp'], dict)
            assert 'seconds' in value['stamp']
            assert 'nanoseconds' in value['stamp']

        if dbrtype.isSTRING():
            return

        if dbrtype.isGR() or dbrtype.isCTRL():
            if dbrtype.isENUM():
                assert value['no_str'] == 0
                assert value['strs'] == ()
            else:
                lo = -10
                lolo = -20
                # char type is uint8
                if dbrtype.isCHAR():
                    lo &= 0xff
                    lolo &= 0xff
                assert value['units'] == 'mm'
                assert value['upper_disp_limit'] == 20
                assert value['lower_disp_limit'] == lolo
                assert value['upper_warning_limit'] == 10
                assert value['lower_warning_limit'] == lo
                assert value['upper_alarm_limit'] == 20
                assert value['lower_alarm_limit'] == lolo
                if dbrtype.isFLOAT() or dbrtype.isDOUBLE():
                    assert value['precision'] == 4
                if dbrtype.isCTRL():
                    assert value['upper_ctrl_limit'] == 0
                    assert value['lower_ctrl_limit'] == 0


def teardown_module(module):
    global chid
    # clear channel
    ca.clear_channel(chid)

    # destroy context
    ca.destroy_context()
