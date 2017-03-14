from __future__ import print_function
import unittest
import caffi.ca as ca


class SyncGroupTest(unittest.TestCase):
    def setUp(self):
        self.pvs = {}
        self.vals = {}

        # create channels
        for name in ['cawaves', 'cawaveh', 'cawavef', 'cawavec', 'cawavel', 'cawave']:
            status, chid = ca.create_channel(name)
            self.assertEqual(status, ca.ECA.NORMAL)
            self.pvs[name] = chid

        # wait for connections
        status = ca.pend_io(10)
        assert status == ca.ECA.NORMAL

        # create synchronous group
        status, self.gid = ca.sg_create()
        assert status == ca.ECA.NORMAL

    def test_put_get(self):
        # put
        for name, chid in self.pvs.items():
            if ca.field_type(chid) == ca.DBF.STRING:
                ca.sg_put(self.gid, chid, ['1', '2', '3', '4'])
            else:
                ca.sg_put(self.gid, chid, [1, 2, 3, 4])

        ca.flush_io()

        status = ca.sg_block(self.gid, 3)
        assert status == ca.ECA.NORMAL

        # get
        for name, chid in self.pvs.items():
            status, dbrvalue = ca.sg_get(self.gid, chid, count=4)
            self.assertEqual(status, ca.ECA.NORMAL)
            self.vals[name] = dbrvalue

        ca.flush_io()

        # wait for get completion
        status = ca.sg_block(self.gid, 3)
        assert status == ca.ECA.NORMAL

        # compare read value with written values
        for name, dbrvalue in self.vals.items():
            chid = self.pvs[name]
            element_count = ca.element_count(chid)
            value = dbrvalue.get()
            if ca.field_type(chid) == ca.DBF.STRING:
                self.assertEqual(value, ['1', '2', '3', '4'][:element_count])
            else:
                self.assertEqual(value, [1, 2, 3, 4][:element_count])

    def tearDown(self):
        # delete synchronous group
        ca.sg_delete(self.gid)

        # close channels
        for name, chid in self.pvs.items():
            ca.clear_channel(chid)

        self.pvs.clear()
        self.vals.clear()

        ca.flush_io()

if __name__ == '__main__':
    unittest.main()
