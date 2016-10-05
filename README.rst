caffi
=====

caffi is the Channel Access Foreign Function Interface.
It uses `CFFI <https://pypi.python.org/pypi/cffi>`_ to call EPICS channel access library.

It is the goal of this package to provide direct low level
interface to channel access, alike the C API.


Install
-------
EPICS dynamic libraries have been shipped with the package for Windows, Linux and OS X.
But if the environment variables *EPICS_BASE* and *EPICS_HOST_ARCH* are set,
those libraries under path ``${EPICS_BASE}/lib/${EPICS_HOST_ARCH}`` will be used.

Either use *pip*,
::

    $ pip install caffi

or checkout source code from the git repository,
::

    $ git clone https://github.com/CaChannel/caffi.git
    $ cd caffi
    $ python setup.py install


Documents
---------
Latest documents are hosted at `Read the Dcos <http://caffi.readthedocs.org>`_.


Example
-------

::

    import caffi.ca as ca

    context = ca.create_context()

    status, chid = ca.create_channel('catest')
    assert status == ca.ECA.NORMAL

    status = ca.pend_io(3)
    assert status == ca.ECA.NORMAL

    status = ca.put(chid, 123)
    status = ca.flush_io()

    status, value = ca.get(chid)
    assert status == ca.ECA.NORMAL

    status = ca.pend_io(3)
    assert status == ca.ECA.NORMAL

    assert value.get() == 123
