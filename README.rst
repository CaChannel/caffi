caffi
=====

caffi is the Channel Access Foreign Function Interface.
It uses `CFFI <https://pypi.python.org/pypi/cffi>`_ to call EPICS channel access library.

This package provides direct low level interface to channel access, alike the C API.

.. note:: cffi `commit 9fe2a9e <https://bitbucket.org/cffi/cffi/commits/9fe2a9e>`_ contains an important fix to the
   frequent hangup on Windows 64bit Python 3. That means until cffi 1.11 is released, one should patch manually.


Install
-------
EPICS dynamic libraries have been shipped with the package for Windows, Linux and macOS.
But if the environment variables *EPICS_BASE* and *EPICS_HOST_ARCH* are set on macOS and Linux,
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

    status = ca.create_context()
    assert status == ca.ECA.NORMAL

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
