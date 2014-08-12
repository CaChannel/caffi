"""
CaChannel class having identical API as of caPython/CaChannel class,
based on caffi
"""
# python 2 -> 3 compatible layer
from __future__ import print_function
from functools import wraps
import time
import sys

import caffi.ca as ca
import caffi.dbr as dbr
ca.dbf_text = dbr.dbf_type_to_text
ca.dbr_text = dbr.dbr_type_to_text


# create default preemptive enabled context
ca.create_context(True)
CONTEXT = ca.current_context()

cs_never_search = 4

# retrieve numeric waveforms as numpy arrays, default No
USE_NUMPY = False


class CaChannelException(Exception):
    def __init__(self, status):
        self.status = status

    def __str__(self):
        return ca.message(self.status)

# A wrapper to automatically attach to default CA context
def attach_ca_context(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if ca.current_context() != CONTEXT:
            ca.attach_context(CONTEXT)
        return func(*args, **kwargs)

    return wrapper


class CaChannel:
    """CaChannel: A Python class with identical API as of caPython/CaChannel.

    This class implements the methods to operate on channel access so that you can find
    their  C library counterparts ,
    http://www.aps.anl.gov/epics/base/R3-14/12-docs/CAref.html#Function.
    Therefore an understanding of C API helps much.

    To get started easily, convenient methods are created for often used operations,

    ==========    ======
    Operation     Method
    ==========    ======
    connect       :meth:`searchw`
    read          :meth:`getw`
    write         :meth:`putw`
    ==========    ======

    They have shorter names and default arguments. It is recommended to start with these methods.
    Study the other C alike methods when necessary.

    >>> import CaChannel
    >>> chan = CaChannel.CaChannel('catest')
    >>> chan.searchw()
    >>> chan.putw(12.3)
    >>> chan.getw()
    12.3
    """

    ca_timeout = 1.0

    def __init__(self, pvName=None):
        self._pvname = pvName
        self._chid = None
        self._evid = None
        self._timeout = None
        self._callbacks={}

    def __del__(self):
        try:
            ca.attach_context(CONTEXT)
            self.clear_event()
            self.clear_channel()
            self.flush_io()
        except:
            pass


    def version(self):
        return "CaChannel, version v28-05-2014"
#
# Class helper methods
#
    def setTimeout(self, timeout):
        """Set the timeout for this channel object. It overrides the class timeout.

        :param float timeout:  timeout in seconds

        """
        if (timeout>=0 or timeout is None):
            self._timeout = timeout
        else:
            raise ValueError


    def getTimeout(self):
        """Retrieve the timeout set for this channel object.

        :return: timeout in seconds for this channel instance

        """
        if self._timeout is None:
            timeout = CaChannel.ca_timeout
        else:
            timeout = self._timeout

        return timeout


#
# *************** Channel access medthod ***************
#

#
# Connection methods
#   search_and_connect
#   search
#   clear_channel
    @attach_ca_context
    def search_and_connect(self, pvName, callback, *user_args):
        """Attempt to establish a connection to a process variable.

        :param str pvName:          process variable name
        :param callable callback:   function called when connection completes and connection status changes later on.
        :param user_args:           user provided arguments that are passed to callback when it is invoked.
        :raises CaChannelException: if error happens

        The user arguments are returned to the user in a tuple in the callback function.
        The order of the arguments is preserved.

        Each Python callback function is required to have two arguments.
        The first argument is a tuple containing the results of the action.
        The second argument is a tuple containing any user arguments specified by ``user_args``.
        If no arguments were specified then the tuple is empty.


        .. note:: All remote operation requests such as the above are accumulated (buffered)
           and not forwarded to the IOC until one of execution methods (:meth:`pend_io`, :meth:`poll`, :meth:`pend_event`, :meth:`flush_io`)
           is called. This allows several requests to be efficiently sent over the network in one message.

        >>> chan = CaChannel('catest')
        >>> def connCB(epicsArgs, userArgs):
        ...     chid = epicsArgs[0]
        ...     connection_state = epicsArgs[1]
        ...     if connection_state == ca.CA_OP_CONN_UP:
        ...         print(ca.name(chid), "is connected")
        >>> chan.search_and_connect(None, connCB, chan)
        >>> status = chan.pend_event(2)
        catest is connected
        """
        if pvName is None:
            pvName = self._pvname
        else:
            self._pvname = pvName

        self._callbacks['connCB']=(callback, user_args)

        status, self._chid = ca.create_channel(pvName, self._conn_callback)
        if status != ca.ECA.NORMAL:
            raise CaChannelException(status)

    @attach_ca_context
    def search(self, pvName=None):
        """Attempt to establish a connection to a process variable.

        :param str pvName: process variable name
        :raises CaChannelException: if error happens

        .. note:: All remote operation requests such as the above are accumulated (buffered)
           and not forwarded to the IOC until one of execution methods (:meth:`pend_io`, :meth:`poll`, :meth:`pend_event`, :meth:`flush_io`)
           is called. This allows several requests to be efficiently sent over the network in one message.

        >>> chan = CaChannel()
        >>> chan.search('catest')
        >>> status = chan.pend_io(1)
        >>> chan.state()
        2
        """
        if pvName is None:
            pvName = self._pvname
        else:
            self._pvname = pvName

        ca.attach_context(CONTEXT)
        status, self._chid = ca.create_channel(pvName)
        if status != ca.ECA.NORMAL:
            raise CaChannelException(status)

    @attach_ca_context
    def clear_channel(self):
        """Close a channel created by one of the search functions.

        Clearing a channel does not cause its connection handler to be called.
        Clearing a channel does remove any monitors registered for that channel.
        If the channel is currently connected then resources are freed only some
        time after this request is flushed out to the server.

        .. note:: All remote operation requests such as the above are accumulated (buffered)
           and not forwarded to the IOC until one of execution methods (:meth:`pend_io`, :meth:`poll`, :meth:`pend_event`, :meth:`flush_io`)
           is called. This allows several requests to be efficiently sent over the network in one message.

        """
        if(self._chid is not None):
            ca.clear_channel(self._chid)


#
# Write methods
#   array_put
#   array_put_callback
#
    @attach_ca_context
    def array_put(self, value, req_type=None, count=None):
        """Write a value or array of values to a channel

        :param value:           data to be written. For multiple values use a list or tuple
        :param req_type:        database request type (``ca.DBR_XXXX``). Defaults to be the native data type.
        :param int count:       number of data values to write. Defaults to be the native count.

        >>> chan = CaChannel('catest')
        >>> chan.searchw()
        >>> chan.array_put(123)
        >>> chan.flush_io()
        >>> chan.getw()
        123.0
        >>> chan = CaChannel('cabo')
        >>> chan.searchw()
        >>> chan.array_put('Busy', ca.DBR_STRING)
        >>> chan.flush_io()
        >>> chan.getw()
        1
        >>> chan = CaChannel('cawave')
        >>> chan.searchw()
        >>> chan.array_put([1,2,3])
        >>> chan.flush_io()
        >>> chan.getw()
        [1.0, 2.0, 3.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        >>> chan.getw(count=3, use_numpy=True)
        array([ 1.,  2.,  3.])
        >>> chan = CaChannel('cawavec')
        >>> chan.searchw()
        >>> chan.array_put('1234',count=3)
        >>> chan.flush_io()
        >>> chan.getw(count=4)
        [49, 50, 51, 0]
        """
        status = ca.put(self._chid, value, dbrtype=req_type,count=count)
        if status != ca.ECA.NORMAL:
            raise CaChannelException(status)


    @attach_ca_context
    def array_put_callback(self, value, req_type, count, callback, *user_args):
        """Write a value or array of values to a channel and execute the user
        supplied callback after the put has completed.

        :param value:           data to be written. For multiple values use a list or tuple.
        :param req_type:        database request type (``ca.DBR_XXXX``). Defaults to be the native data type.
        :param int count:       number of data values to write, Defaults to be the native count.
        :param callable callback: function called when the write is completed.
        :param user_args:       user provided arguments that are passed to callback when it is invoked.
        :raises CaChannelException: if error happens

        Each Python callback function is required to have two arguments.
        The first argument is a dictionary containing the results of the action.

        =======  =====  =======
        field    type   comment
        =======  =====  =======
        chid     int    channels id structure
        type     int    database request type (ca.DBR_XXXX)
        count    int    number of values to transfered
        status   int    CA status return code (ca.ECA_XXXX)
        =======  =====  =======

        The second argument is a tuple containing any user arguments specified by ``user_args``.
        If no arguments were specified then the tuple is empty.


        >>> def putCB(epicsArgs, userArgs):
        ...     print(ca.name(epicsArgs['chid']), 'put completed')
        >>> chan = CaChannel('catest')
        >>> chan.searchw()
        >>> chan.array_put_callback(145, None, None, putCB)
        >>> status = chan.pend_event(1)
        catest put completed
        >>> chan = CaChannel('cabo')
        >>> chan.searchw()
        >>> chan.array_put_callback('Busy', ca.DBR_STRING, None, putCB)
        >>> status = chan.pend_event(1)
        cabo put completed
        >>> chan = CaChannel('cawave')
        >>> chan.searchw()
        >>> chan.array_put_callback([1,2,3], None, None, putCB)
        >>> status = chan.pend_event(1)
        cawave put completed
        >>> chan = CaChannel('cawavec')
        >>> chan.searchw()
        >>> chan.array_put_callback('123', None, None, putCB)
        >>> status = chan.pend_event(1)
        cawavec put completed
        """
        status = ca.put(self._chid, value, req_type, count, callback, user_args)
        if status != ca.ECA.NORMAL:
            raise CaChannelException(status)
#
# Read methods
#   getValue
#   array_get
#   array_get_callback
#

    # Obtain read value after ECA_NORMAL is returned on an array_get().
    def getValue(self):
        """Return the value(s) after array_get has completed"""
        dbrvalue = self.val.get()
        if isinstance(dbrvalue, dict):
            value = {}
            self._format_value(dbrvalue, value)
        else:
            value = dbrvalue

        if not self.val.use_numpy:
            if isinstance(value, dict):
                if hasattr(value['pv_value'], 'tolist'):
                   value['pv_value'] = value['pv_value'].tolist()
            else:
                if hasattr(value, 'tolist'):
                    value = value.tolist()
        return value


    # Simulate with a synchronous getw function call
    @attach_ca_context
    def array_get(self, req_type=None, count=None, **keywords):
        """Read a value or array of values from a channel. The new value is
        retrieved by a call to getValue method.

        :param req_type:    database request type (``ca.DBR_XXXX``). Defaults to be the native data type.
        :param int count:   number of data values to read, Defaults to be the native count.
        :param keywords:    optional arguments assigned by keywords

                            ===========   =====
                            keyword       value
                            ===========   =====
                            use_numpy     True if waveform should be returned as numpy array. Default :data:`CaChannel.USE_NUMPY`.
                            ===========   =====

        :raises CaChannelException: if error happens

        .. note:: All remote operation requests such as the above are accumulated (buffered)
           and not forwarded to the IOC until one of execution methods (``pend_io``, ``poll``, ``pend_event``, ``flush_io``)
           is called. This allows several requests to be efficiently sent over the network in one message.


        >>> chan = CaChannel('catest')
        >>> chan.searchw()
        >>> chan.putw(123)
        >>> chan.array_get()
        >>> chan.pend_io()
        >>> chan.getValue()
        123.0
        """
        use_numpy = keywords.get('use_numpy', USE_NUMPY)
        status, self.val = ca.get(self._chid, req_type, count)
        self.val.use_numpy = use_numpy
        if status != ca.ECA.NORMAL:
            raise CaChannelException(status)


    @attach_ca_context
    def array_get_callback(self, req_type, count, callback, *user_args, **keywords):
        """Read a value or array of values from a channel and execute the user
        supplied callback after the get has completed.

        :param req_type:        database request type (``ca.DBR_XXXX``). Defaults to be the native data type.
        :param int count:       number of data values to read, Defaults to be the native count.
        :param callable callback:  function called when the get is completed.
        :param user_args:       user provided arguments that are passed to callback when it is invoked.
        :param keywords:        optional arguments assigned by keywords

                                ===========   =====
                                keyword       value
                                ===========   =====
                                use_numpy     True if waveform should be returned as numpy array. Default :data:`CaChannel.USE_NUMPY`.
                                ===========   =====

        :raises CaChannelException: if error happens

        Each Python callback function is required to have two arguments.
        The first argument is a dictionary containing the results of the action.

        +-----------------+---------------+------------------------------------+-------------------------+---------------+-------------+---------------+
        | field           |  type         |  comment                           |       request type                                                    |
        |                 |               |                                    +----------+--------------+---------------+-------------+---------------+
        |                 |               |                                    | DBR_XXXX | DBR_STS_XXXX | DBR_TIME_XXXX | DBR_GR_XXXX | DBR_CTRL_XXXX |
        +=================+===============+====================================+==========+==============+===============+=============+===============+
        | chid            |   int         |   channels id number               |    X     |       X      |     X         |   X         | X             |
        +-----------------+---------------+------------------------------------+----------+--------------+---------------+-------------+---------------+
        | type            |   int         |   database request type            |    X     |       X      |     X         |   X         | X             |
        |                 |               |   (ca.DBR_XXXX)                    |          |              |               |             |               |
        +-----------------+---------------+------------------------------------+----------+--------------+---------------+-------------+---------------+
        | count           |   int         |   number of values to transfered   |    X     |       X      |     X         |   X         | X             |
        +-----------------+---------------+------------------------------------+----------+--------------+---------------+-------------+---------------+
        | status          |   int         |   CA status return code            |    X     |       X      |     X         |   X         | X             |
        |                 |               |   (ca.ECA_XXXX)                    |          |              |               |             |               |
        +-----------------+---------------+------------------------------------+----------+--------------+---------------+-------------+---------------+
        | pv_value        |               |   PV value                         |    X     |       X      |     X         |   X         | X             |
        +-----------------+---------------+------------------------------------+----------+--------------+---------------+-------------+---------------+
        | pv_status       |   int         |   PV alarm status                  |          |       X      |     X         |   X         | X             |
        +-----------------+---------------+------------------------------------+----------+--------------+---------------+-------------+---------------+
        | pv_severity     |   int         |   PV alarm severity                |          |       X      |     X         |   X         | X             |
        +-----------------+---------------+------------------------------------+----------+--------------+---------------+-------------+---------------+
        | pv_seconds      |   float       |   timestamp                        |          |              |     X         |   X         | X             |
        +-----------------+---------------+------------------------------------+----------+--------------+---------------+-------------+---------------+
        | pv_nostrings    |   int         |   ENUM PV's number of states       |          |              |               |   X         | X             |
        +-----------------+---------------+------------------------------------+----------+--------------+---------------+-------------+---------------+
        | pv_statestrings |   string list |   ENUM PV's states string          |          |              |               |   X         | X             |
        +-----------------+---------------+------------------------------------+----------+--------------+---------------+-------------+---------------+
        | pv_units        |   string      |   units                            |          |              |               |   X         | X             |
        +-----------------+---------------+------------------------------------+----------+--------------+---------------+-------------+---------------+
        | pv_precision    |   int         |   precision                        |          |              |               |   X         | X             |
        +-----------------+---------------+------------------------------------+----------+--------------+---------------+-------------+---------------+
        | pv_updislim     |   float       |   upper display limit              |          |              |               |   X         | X             |
        +-----------------+---------------+------------------------------------+----------+--------------+---------------+-------------+---------------+
        | pv_lodislim     |   float       |   lower display limit              |          |              |               |   X         | X             |
        +-----------------+---------------+------------------------------------+----------+--------------+---------------+-------------+---------------+
        | pv_upalarmlim   |   float       |   upper alarm limit                |          |              |               |   X         | X             |
        +-----------------+---------------+------------------------------------+----------+--------------+---------------+-------------+---------------+
        | pv_upwarnlim    |   float       |   upper warning limit              |          |              |               |   X         | X             |
        +-----------------+---------------+------------------------------------+----------+--------------+---------------+-------------+---------------+
        | pv_loalarmlim   |   float       |   lower alarm limit                |          |              |               |   X         | X             |
        +-----------------+---------------+------------------------------------+----------+--------------+---------------+-------------+---------------+
        | pv_lowarnlim    |   float       |   lower warning limit              |          |              |               |   X         | X             |
        +-----------------+---------------+------------------------------------+----------+--------------+---------------+-------------+---------------+
        | pv_upctrllim    |   float       |   upper control limit              |          |              |               |             | X             |
        +-----------------+---------------+------------------------------------+----------+--------------+---------------+-------------+---------------+
        | pv_loctrllim    |   float       |   lower control limit              |          |              |               |             | X             |
        +-----------------+---------------+------------------------------------+----------+--------------+---------------+-------------+---------------+

        The second argument is a tuple containing any user arguments specified by ``user_args``.
        If no arguments were specified then the tuple is empty.

        .. note:: All remote operation requests such as the above are accumulated (buffered)
           and not forwarded to the IOC until one of execution methods (``pend_io``, ``poll``, ``pend_event``, ``flush_io``)
           is called. This allows several requests to be efficiently sent over the network in one message.

        >>> def getCB(epicsArgs, userArgs):
        ...     for item in sorted(epicsArgs.keys()):
        ...         if item.startswith('pv_'):
        ...             print(item,epicsArgs[item])
        >>> chan = CaChannel('catest')
        >>> chan.searchw()
        >>> chan.putw(145)
        >>> chan.array_get_callback(ca.DBR_CTRL_DOUBLE, 1, getCB)
        >>> status = chan.pend_event(1)
        pv_loalarmlim -20.0
        pv_loctrllim 0.0
        pv_lodislim 0.0
        pv_lowarnlim -10.0
        pv_precision 3
        pv_severity 2
        pv_status 3
        pv_units mm
        pv_upalarmlim 20.0
        pv_upctrllim 0.0
        pv_updislim 0.0
        pv_upwarnlim 10.0
        pv_value 145.0
        >>> chan = CaChannel('cabo')
        >>> chan.searchw()
        >>> chan.putw(0)
        >>> chan.array_get_callback(ca.DBR_CTRL_ENUM, 1, getCB)
        >>> status = chan.pend_event(1)
        pv_nostrings 2
        pv_severity 0
        pv_statestrings ('Done', 'Busy')
        pv_status 0
        pv_value 0
        """
        use_numpy = keywords.get('use_numpy', USE_NUMPY)
        self._callbacks['getCB']=(callback, user_args, use_numpy)
        status, self.val = ca.get(self._chid, req_type, count, self._get_callback)
        if status != ca.ECA.NORMAL:
            raise CaChannelException(status)


#
# Monitor methods
#   add_masked_array_event
#   clear_event
#

    # Creates a new event id and stores it on self.__evid.  Only one event registered
    # per CaChannel object.  If an event is already registered the event is cleared
    # before registering a new event.
    @attach_ca_context
    def add_masked_array_event(self, req_type, count, mask, callback, *user_args, **keywords):
        """Specify a callback function to be executed whenever changes occur to a PV.

        :param req_type:        database request type (``ca.DBR_XXXX``). Defaults to be the native data type.
        :param int  count:      number of data values to read, Defaults to be the native count.
        :param mask:            logical or of ``ca.DBE_VALUE``, ``ca.DBE_LOG``, ``ca.DBE_ALARM``.
                                Defaults to be ``ca.DBE_VALUE|ca.DBE_ALARM``.
        :param callable callback:        function called when the get is completed.
        :param user_args:       user provided arguments that are passed to callback when
                                it is invoked.
        :param keywords:        optional arguments assigned by keywords

                                ===========   =====
                                keyword       value
                                ===========   =====
                                use_numpy     True if waveform should be returned as numpy array. Default :data:`CaChannel.USE_NUMPY`.
                                ===========   =====

        :raises CaChannelException: if error happens

        .. note:: All remote operation requests such as the above are accumulated (buffered)
           and not forwarded to the IOC until one of execution methods (:meth:`pend_io`, :meth:`poll`, :meth:`pend_event`, :meth:`flush_io`)
           is called. This allows several requests to be efficiently sent over the network in one message.

        >>> def eventCB(epicsArgs, userArgs):
        ...     print('pv_value', epicsArgs['pv_value'])
        ...     print('pv_status', int(epicsArgs['pv_status']))
        ...     print('pv_severity', int(epicsArgs['pv_severity']))
        >>> chan = CaChannel('cabo')
        >>> chan.searchw()
        >>> chan.putw(1)
        >>> chan.add_masked_array_event(ca.DBR_STS_ENUM, None, None, eventCB)
        >>> status = chan.pend_event(1)
        pv_value 1
        pv_status 7
        pv_severity 1
        >>> chan.clear_event()
        >>> chan.add_masked_array_event(ca.DBR_STS_STRING, None, None, eventCB)
        >>> status = chan.pend_event(1)
        pv_value Busy
        pv_status 7
        pv_severity 1
        >>> chan.clear_event()
        """
        if self._evid is not None:
            self.clear_event()
            self.flush_io()

        if mask is None:
            mask = ca.DBE_ALARM | ca.DBE_VALUE

        use_numpy = keywords.get('use_numpy', USE_NUMPY)
        self._callbacks['eventCB']=(callback, user_args, use_numpy)

        status, self._evid = ca.create_subscription(self._chid, self._event_callback, (), req_type, count, mask)

        if status != ca.ECA.NORMAL:
            raise CaChannelException(status)


    @attach_ca_context
    def clear_event(self):
        """Remove previously installed callback function.

        .. note:: All remote operation requests such as the above are accumulated (buffered)
           and not forwarded to the IOC until one of execution methods (:meth:`pend_io`, :meth:`poll`, :meth:`pend_event`, :meth:`flush_io`)
           is called. This allows several requests to be efficiently sent over the network in one message.
        """
        if self._evid is not None:
            status = ca.clear_subscription(self._evid)
            self._evid = None
            if status != ca.ECA.NORMAL:
                raise CaChannelException(status)


#
# Execute methods
#   pend_io
#   pend_event
#   poll
#   flush_io
#

    @attach_ca_context
    def pend_io(self,timeout=None):
        """Flush the send buffer and wait until outstanding queries (``search``, ``array_get``) complete
        or the specified timeout expires.

        :param float timeout:         seconds to wait
        :raises CaChannelException: if timeout or other error happens

        """
        if timeout is None:
            timeout = self.getTimeout()
        status = ca.pend_io(float(timeout))
        if status != ca.ECA.NORMAL:
            raise CaChannelException(status)


    @attach_ca_context
    def pend_event(self,timeout=None):
        """Flush the send buffer and process background activity (connect/get/put/monitor callbacks) for ``timeout`` seconds.

        It will not return before the specified timeout expires and all unfinished channel access labor has been processed.

        :param float timeout:  seconds to wait

        """
        if timeout is None:
            timeout = 0.1
        status = ca.pend_event(timeout)
        # status is always ECA_TIMEOUT
        return status


    @attach_ca_context
    def poll(self):
        """Flush the send buffer and execute any outstanding background activity.

        .. note:: It is an alias to ``pend_event(1e-12)``.
        """
        ca.attach_context(CONTEXT)
        status = ca.poll()
        # status is always ECA_TIMEOUT
        return status


    @attach_ca_context
    def flush_io(self):
        """Flush the send buffer and does not execute outstanding background activity."""
        status = ca.flush_io()
        if status != ca.ECA.NORMAL:
            raise CaChannelException(status)


#
# Channel Access Macros
#   field_type
#   element_count
#   name
#   state
#   host_name
#   read_access
#   write_access
#
    def field_type(self):
        """Native type of the PV in the server (``ca.DBF_XXXX``).

        >>> chan = CaChannel('catest')
        >>> chan.searchw()
        >>> ftype = chan.field_type()
        >>> ftype
        6
        >>> ca.dbf_text(ftype)
        'DBF_DOUBLE'
        >>> ca.DBF_DOUBLE == ftype
        True
        """
        return int(ca.field_type(self._chid))


    def element_count(self):
        """Maximum array element count of the PV in the server.

        >>> chan = CaChannel('catest')
        >>> chan.searchw()
        >>> chan.element_count()
        1
        """
        return int(ca.element_count(self._chid))


    def name(self):
        """Channel name specified when the channel was created.

        >>> chan = CaChannel('catest')
        >>> chan.searchw()
        >>> chan.name()
        'catest'
        """
        return ca.name(self._chid)


    def state(self):
        """Current state of the CA connection.

            ==================    =============
            States                Meaning
            ==================    =============
            ca.cs_never_conn      PV not found
            ca.cs_prev_conn       PV was found but unavailable
            ca.cs_conn            PV was found and available
            ca.cs_closed          PV not closed
            ca.cs_never_search    PV not searched yet
            ==================    =============

        >>> chan = CaChannel('catest')
        >>> chan.searchw()
        >>> chan.state()
        2
        """
        if self._chid is None:
            return cs_never_search
        else:
            return int(ca.state(self._chid))


    def host_name(self):
        """Host name that hosts the process variable."""
        return ca.host_name(self._chid)


    def read_access(self):
        """Access right to read the channel.

         :return: True if the channel can be read, False otherwise.

         """
        return ca.read_access(self._chid)


    def write_access(self):
        """Access right to write the channel.

        :return: True if the channel can be written, False otherwise.

        """
        return ca.write_access(self._chid)


#
# Wait functions
#
# These functions wait for completion of the requested action.
    def searchw(self, pvName=None):
        """Attempt to establish a connection to a process variable.

        :param str pvName:          process variable name
        :raises CaChannelException: if timeout or error happens

        .. note:: This method waits for connection to be established or fail with exception.

        >>> chan = CaChannel('non-exist-channel')
        >>> chan.searchw()
        Traceback (most recent call last):
            ...
        CaChannelException: User specified timeout on IO operation expired
        """
        self.search(pvName)
        timeout = self.getTimeout()
        self.pend_io(timeout)


    def putw(self, value, req_type=None):
        """Write a value or array of values to a channel

        If the request type is omitted the data is written as the Python type corresponding to the native format.
        Multi-element data is specified as a tuple or a list.
        Internally the sequence is converted to a list before inserting the values into a C array.
        Access using non-numerical types is restricted to the first element in the data field.
        Mixing character types with numerical types writes bogus results but is not prohibited at this time.
        DBF_ENUM fields can be written using DBR_ENUM and DBR_STRING types.
        DBR_STRING writes of a field of type DBF_ENUM must be accompanied by a valid string out of the possible enumerated values.

        :param value:           data to be written. For multiple values use a list or tuple
        :param req_type:        database request type (``ca.DBR_XXXX``). Defaults to be the native data type.
        :raises CaChannelException: if timeout or error happens

        .. note:: This method does flush the request to the channel access server.

        >>> chan = CaChannel('catest')
        >>> chan.searchw()
        >>> chan.putw(145)
        >>> chan.getw()
        145.0
        >>> chan = CaChannel('cabo')
        >>> chan.searchw()
        >>> chan.putw('Busy', ca.DBR_STRING)
        >>> chan.getw()
        1
        >>> chan.getw(ca.DBR_STRING)
        'Busy'
        >>> chan = CaChannel('cawave')
        >>> chan.searchw()
        >>> chan.putw([1,2,3])
        >>> chan.getw(req_type=ca.DBR_LONG,count=4)
        [1, 2, 3, 0]
        >>> chan = CaChannel('cawavec')
        >>> chan.searchw()
        >>> chan.putw('123')
        >>> chan.getw(count=4)
        [49, 50, 51, 0]
        >>> chan = CaChannel('cawaves')
        >>> chan.searchw()
        >>> chan.putw(['string 1','string 2'])
        >>> chan.getw()
        ['string 1', 'string 2', '']
        """
        self.array_put(value, req_type)
        self.flush_io()


    def getw(self, req_type=None, count=None, **keywords):
        """Read the value from a channel.

        :param req_type:        database request type. Defaults to be the native data type.
        :param int count:       number of data values to read, Defaults to be the native count.
        :param keywords:        optional arguments assigned by keywords

                                ===========   =====
                                keyword       value
                                ===========   =====
                                use_numpy     True if waveform should be returned as numpy array. Default :data:`CaChannel.USE_NUMPY`.
                                ===========   =====
        :return:                If req_type is plain request type, only the value is returned. Otherwise a dict returns
                                with information depending on the request type, same as the first argument passed to user's callback.
                                See :meth:`array_get_callback`.

        :raises CaChannelException: if timeout error happens

        If the request type is omitted the data is returned to the user as the Python type corresponding to the native format.
        Multi-element data has all the elements returned as items in a list and must be accessed using a numerical type.
        Access using non-numerical types is restricted to the first element in the data field.
        DBF_ENUM fields can be read using DBR_ENUM and DBR_STRING types.
        DBR_STRING reads of a field of type DBF_ENUM returns the string corresponding to the current enumerated value.

        """
        self.array_get(req_type, count, **keywords)
        timeout = self.getTimeout()
        self.pend_io(timeout)

        value = self.getValue()
        return value


#
# Callback functions
#
# These functions hook user supplied callback functions to CA extension

    def _conn_callback(self, epicsArgs, userArgs):
        callback = self._callbacks.get('connCB')
        if callback is None:
            return
        callbackFunc, userArgs = callback
        if epicsArgs['up']: OP = 6
        else: OP = 7
        epicsArgs = (self._chid, OP)
        try:
            callbackFunc(epicsArgs, userArgs)
        except:
            pass


    def _put_callback(self, epicsArgs, userArgs):
        callback = self._callbacks.get('putCB')
        if callback is None:
            return
        callbackFunc, userArgs = callback
        try:
            callbackFunc(epicsArgs, userArgs)
        except:
            pass


    def _get_callback(self, epicsArgs, userArgs):
        callback = self._callbacks.get('getCB')
        if callback is None:
            return
        callbackFunc, userArgs, use_numpy = callback
        epicsArgs = self._format_cb_args(epicsArgs, use_numpy)
        try:
            callbackFunc(epicsArgs, userArgs)
        except:
            pass


    def _event_callback(self, epicsArgs, userArgs):
        callback = self._callbacks.get('eventCB')
        if callback is None:
            return
        callbackFunc, userArgs, use_numpy = callback
        epicsArgs = self._format_cb_args(epicsArgs, use_numpy)
        try:
            callbackFunc(epicsArgs, userArgs)
        except:
            pass


    def _format_cb_args(self, args, use_numpy):
        epicsArgs={}
        epicsArgs['chid']   = args['chid']
        epicsArgs['type']   = args['type']
        epicsArgs['count']  = args['count']
        epicsArgs['status'] = args['status']
        self._format_value(args['value'], epicsArgs, use_numpy)

        return epicsArgs


    def _format_value(self, value, epicsArgs, use_numpy):
        # dbr value fields are prefixed with 'pv_'
        if isinstance(value, dict):
            for key in value:
                if key == 'lower_alarm_limit':
                    new_key = 'loalarmlim'
                elif key == 'lower_ctrl_limit':
                    new_key = 'loctrllim'
                elif key == 'lower_disp_limit':
                    new_key = 'lodislim'
                elif key == 'lower_warning_limit':
                    new_key = 'lowarnlim'
                elif key == 'upper_alarm_limit':
                    new_key = 'upalarmlim'
                elif key == 'upper_ctrl_limit':
                    new_key = 'upctrllim'
                elif key == 'upper_disp_limit':
                    new_key = 'updislim'
                elif key == 'upper_warning_limit':
                    new_key = 'upwarnlim'
                elif key == 'no_str':
                    new_key = 'nostrings'
                elif key == 'strs':
                    new_key = 'statestrings'
                else:
                    new_key = key
                epicsArgs['pv_' + new_key] = value[key]
            if 'pv_status' in epicsArgs:
                epicsArgs['pv_status'] = int(epicsArgs['pv_status'])
                epicsArgs['pv_severity'] = int(epicsArgs['pv_severity'])
            # convert stamp(datetime) to seconds and nano seconds
            if 'pv_stamp' in epicsArgs:
                stamp = epicsArgs['pv_stamp']
                seconds = int(time.mktime(stamp.timetuple()))
                nseconds = int(stamp.microsecond * 1e3)
                epicsArgs['pv_seconds'] = seconds
                epicsArgs['pv_nseconds'] = nseconds
                del epicsArgs['pv_stamp']
        else:
            epicsArgs['pv_value'] = value

        if not use_numpy and hasattr(epicsArgs['pv_value'], 'tolist'):
            epicsArgs['pv_value'] = epicsArgs['pv_value'].tolist()

        return epicsArgs


if __name__ == "__main__":
    import doctest
    doctest.testmod()
