from __future__ import print_function
import pytest
import caffi.ca as ca

def setup_module(module):
    # create preemptive enabled context
    status = ca.create_context(True)
    assert status == ca.ECA.NORMAL


@pytest.mark.parametrize("name, input, expected", [
    ('cawaves', ['1', '2', '3', '4'], ['1', '2', '3']),
    ('cawaves', '1', ['1', '', '']),
    ('cawaveh', [1, 2, 3, 4], None),
    ('cawavef', [1, 2, 3, 4], None),
    ('cawavec', [1, 2, 3, 4], None),
    ('cawavel', [1, 2, 3, 4], None),
    ('cawave',  [1, 2, 3, 4], None),
    ('cawave',  1,            [1, 0, 0, 0]),
    ('cawave',  '1.23',       [1.23, 0, 0, 0]),
    ('cabo',    [1, 2, 3, 4], 1),
    ('cabo',    'Done',       0),
    ('catest',  1.23,         None),
    ('catest',  [1, 2, 3, 4], 1),
    ('catest',  '1.23',       1.23),
    ('cawavec', '1.23',       [49, 46, 50, 51])])
def test_put_get(name, input, expected):
    if expected is None:
        expected = input

    status, chid = ca.create_channel(name)
    assert status == ca.ECA.NORMAL

    status = ca.pend_io(10)
    assert status == ca.ECA.NORMAL

    status = ca.put(chid, input)
    assert status == ca.ECA.NORMAL

    ca.flush_io()

    status, value = ca.get(chid, count=4)
    assert status == ca.ECA.NORMAL

    status = ca.pend_io(10)
    assert status == ca.ECA.NORMAL

    assert value.get() == expected

    ca.clear_channel(chid)

def teardown_module(module):
    # destroy context
    ca.destroy_context()
