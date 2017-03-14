from __future__ import print_function
import caffi.ca as ca

# create preemptive enabled context
status = ca.create_context(True)
assert status == ca.ECA.NORMAL

import pytest

@pytest.mark.parametrize("name, input",[
    ('cawaves', ['1', '2', '3', '4']),
    ('cawaveh', [1, 2, 3, 4]),
    ('cawavef', [1, 2, 3, 4]),
    ('cawavec', [1, 2, 3, 4]),
    ('cawavel', [1, 2, 3, 4]),
    ('cawave',  [1, 2, 3, 4]),
    ('cabo',    [1, 2, 3, 4])])
def test_put_get(name, input):
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

    element_count = ca.element_count(chid)

    if element_count == 1:
        assert value.get() == input[0]
    else:
        assert value.get() == input[:element_count]

    ca.clear_channel(chid)

# destroy context
ca.destroy_context()
