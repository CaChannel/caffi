import caffi.ca as ca


def setup_module(module):
    global pvs, vals, gid
    pvs = {}
    vals = {}

    # create channels
    for name in ['cawaves', 'cawaveh', 'cawavef', 'cawavec', 'cawavel', 'cawave']:
        status, chid = ca.create_channel(name)
        assert status == ca.ECA.NORMAL
        pvs[name] = chid

    # wait for connections
    status = ca.pend_io(10)
    assert status == ca.ECA.NORMAL

    # create synchronous group
    status, gid = ca.sg_create()
    assert status == ca.ECA.NORMAL


def test_put_get():
    # put
    for name, chid in pvs.items():
        if ca.field_type(chid) == ca.DBF.STRING:
            ca.sg_put(gid, chid, ['1', '2', '3', '4'])
        else:
            ca.sg_put(gid, chid, [1, 2, 3, 4])

    ca.flush_io()

    status = ca.sg_block(gid, 3)
    assert status == ca.ECA.NORMAL

    # get
    for name, chid in pvs.items():
        status, dbrvalue = ca.sg_get(gid, chid, count=4)
        assert status == ca.ECA.NORMAL
        vals[name] = dbrvalue

    ca.flush_io()

    # wait for get completion
    status = ca.sg_block(gid, 3)
    assert status == ca.ECA.NORMAL

    # compare read value with written values
    for name, dbrvalue in vals.items():
        chid = pvs[name]
        element_count = ca.element_count(chid)
        value = dbrvalue.get()
        if ca.field_type(chid) == ca.DBF.STRING:
            assert value == ['1', '2', '3', '4'][:element_count]
        else:
            assert value == [1, 2, 3, 4][:element_count]


def teardown_module():
    # delete synchronous group
    ca.sg_delete(gid)

    # close channels
    for name, chid in pvs.items():
        ca.clear_channel(chid)

    ca.flush_io()

    pvs.clear()
    vals.clear()
