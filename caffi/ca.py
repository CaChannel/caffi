"""
The is the low level access to EPICS channel access library. It maps the corresponding C API to Python functions.
Even though as same as possible, there are subtle differences:

  - The `ca_` prefix of the C function name has been removed, e.g. C function `ca_create_channel` is now
    Python function :func:`create_channel`.

  - The C function `ca_context_destroy` has been renamed to :func:`destroy_context` to have the same symmetry
    as *XXX*\_context.

  - The two separate C functions `ca_client_status` and `ca_context_status` have been merged into :func:`show_context`.
    Internally it calls the appropriate C function depending on whether *context* is given.

  - The order of the argument might have been altered to allow default arguments, thus more pythonic.
    Take C function `array_put_callback` for example,
    ::

        int ca_array_put_callback
        (
            chtype                 type,
            unsigned long          count,
            chid                   chanId,
            const void *           pValue,
            caEventCallBackFunc *  pFunc,
            void *                 pArg
        );

    Its Python counterpart,
    ::

        put(chid, value, chtype=None, count=None, callback=None)

    Only two arguments are mandatory, which are the channel identifier and the value to write.
    The others are made optional and have reasonable defaults.

  - In C API the callback function handler has the following signature,
    ::

        void (*)(struct xxx_handler_args)

    In Python counterpart, the callback signature is
    ::

        def callback(epicsArgs):

    *epicsArgs* is a dict converted from `xxx_handler_args`.

  - C functions normally return status code to indicate success or failure. The Python counterparts follow
    this but have exceptions:

    - The get functions in C require a user supplied memory pointer passed as argument. In Python the function
      :func:`get` and :func:`sg_get` returns a tuple of form (:class:`ECA`, :class:`DBRValue`)

      The first item is the status code, which must be :data:`ECA.NORMAL`, before using the second item.

      The second item holds the reference to the allocated memory. And the memory is not stable until a subsequent
      call of :func:`pend_io` returns :data:`ECA.NORMAL`. Then the value can be retrieved by calling
      :meth:`DBRValue.get`.


    - All the creation functions, :func:`create_channel`, :func:`create_subscription` and :func:`sg_create`
      return a tuple of the form (:class:`ECA`, *object identifier*).
      The object identifier can only be used if the first item is :data:`ECA.NORMAL`.

  - In C the following macros definition are also accessible as :class:`enum.IntEnum` type:

    ======================  ============
    C Macros                Python Enum
    ======================  ============
    *ECA_XXX*               :class:`ECA`
    *DBE_XXX*               :class:`DBE`
    *DBF_XXX*               :class:`DBF`
    *DBR_XXX*               :class:`DBR`
    *CA_OP_XXX*             :class:`CA_OP`
    *cs_xxx*                :class:`ChannelState`
    *XXX_ALARM* (severity)  :class:`AlarmSeverity`
    *XXX_ALARM* (status)    :class:`AlarmCondition`
    ======================  ============

    This makes it convenient when interactively examine the code value. e.g.
    ::

        >>> ca.create_context(True)
        <ECA.NORMAL: 1>
        >>> status, chid = ca.create_channel('catest')
        >>> ca.pend_io(2)
        <ECA.NORMAL: 1>
        >>> ca.name(chid)
        'catest'
        >>> ca.host_name(chid)
        'localhost:5064'
        >>> ca.field_type(chid)
        <DBF.DOUBLE: 6>
        >>> ca.element_count(chid)
        1
        >>> ca.read_access(chid)
        True
        >>> ca.write_access(chid)
        True
        >>> ca.put(chid, 10)
        <ECA.NORMAL: 1>
        >>> ca.flush_io()
        <ECA.NORMAL: 1>
        >>> status, dbrvalue = ca.get(chid)
        >>> ca.pend_io(2)
        <ECA.NORMAL: 1>
        >>> dbrvalue.get()
        10.0

"""
from __future__ import (print_function, absolute_import)
import collections
import numbers
import sys

from .compat import *
from ._ca import *
from .constants import *
from .dbr import *
from .macros import *

__all__ = ['create_context', 'current_context', 'attach_context', 'detach_context', 'destroy_context', 'show_context',
           'add_exception_event', 'replace_access_rights_event', 'change_connection_event',
           'create_channel', 'clear_channel', 'get', 'put', 'create_subscription', 'clear_subscription',
           'field_type', 'element_count', 'name', 'state', 'host_name', 'read_access', 'write_access',
           'pend_event', 'pend_io', 'poll', 'pend', 'flush_io', 'test_io', 'message',
           'sg_create', 'sg_delete', 'sg_get', 'sg_put', 'sg_reset', 'sg_block', 'sg_test', 'version']

# globals
__channels = {}
__exception_callback = {}

DBR_TYPE_STRING = {
    DBR.STRING:   'dbr_string_t',
    DBR.INT:      'dbr_int_t',
    DBR.FLOAT:    'dbr_float_t',
    DBR.CHAR:     'dbr_char_t',
    DBR.ENUM:     'dbr_enum_t',
    DBR.LONG:     'dbr_long_t',
    DBR.DOUBLE:   'dbr_double_t',
    DBR.PUT_ACKT: 'dbr_put_ackt_t',
    DBR.PUT_ACKS: 'dbr_put_acks_t',
}


@ffi.callback('void(*)(struct exception_handler_args)')
def _exception_callback(arg):
    if arg.pFile == ffi.NULL:
        file = ''
    else:
        file = to_string(ffi.string(arg.pFile))

    epics_arg = {
        'chid':   arg.chid,
        'type':   DBR(arg.type),
        'count':  arg.count,
        'addr':   arg.addr,
        'stat':   ECA(arg.stat),
        'op':     CA_OP(arg.op),
        'ctx':    to_string(ffi.string(arg.ctx)),
        'file':   file,
        'lineNo': arg.lineNo
    }

    user_callback = ffi.from_handle(arg.usr)
    if callable(user_callback):
        user_callback(epics_arg)


def add_exception_event(callback=None):
    """
    Replace the currently installed CA context global exception handler call back.

    :param callback:    User callback function to be executed when an exceptions occur.
                        Passing None causes the default exception handler to be reinstalled.
                        The argument is a dict including the following fields:

                        ======  =============
                        field   value
                        ======  =============
                        chid    channel identifier (may be NULL)
                        type    type requested
                        count   count requested
                        addr    user's address to write results of CA_OP.GET (may be NULL)
                        stat    status code, :class:`ECA`
                        op      operation, :class:`CA_OP`
                        ctx     a character string containing context info
                        file    source file name (may be empty)
                        lineNo  source file line number (may be zero)
                        ======  =============

    :type callback:     callable, None
    :return:
        - :data:`ECA.NORMAL` - Normal successful completion

    When an error occurs in the server asynchronous to the clients thread then information about this type of error
    is passed from the server to the client in an exception message. When the client receives this exception message
    an exception handler callback is called.

    The default exception handler prints a diagnostic message on the client's standard out and
    terminates execution if the error condition is severe.

    .. note::   Certain fields are not applicable in the context of some error messages.
                For instance, a failed get will supply the address in the client task
                where the returned value was requested to be written.
                For other failed operations the value of the *addr* field should not be used.

    """
    if callable(callback):
        callback_handle = ffi.new_handle(callback)
        status = libca.ca_add_exception_event(_exception_callback, callback_handle)
    else:
        callback_handle = None
        status = libca.ca_add_exception_event(ffi.NULL, ffi.NULL)

    # keep a reference to the returned pointer of (callback, args),
    # otherwise it will be garbage collected
    context = libca.ca_current_context()
    __exception_callback[context] = callback_handle

    return ECA(status)


def create_context(preemptive_callback=True):
    """
    :param bool preemptive_callback: enable preemptive callback
    :return:
        - :data:`ECA.NORMAL` - Normal successful completion
        - :data:`ECA.ALLOCMEM` - Failed, unable to allocate space in pool
        - :data:`ECA.NOTTHREADED` - Current thread is already a member of a non-preemptive callback CA context
                                    (possibly created implicitly)

    This function, or :func:`attach_context`, should be called once from each thread prior to
    making any of the other Channel Access calls. If one of the above is not called before
    making other CA calls then a non-preemptive context is created by default,
    and future attempts to create a preemptive context for the current threads will fail.

    If preemptive callback is disabled then additional threads are not allowed to
    join the CA context using :func:`attach_context` because allowing other threads to join implies
    that CA callbacks will be called preemptively from more than one thread.

    """
    if preemptive_callback:
        status = libca.ca_context_create(libca.ca_enable_preemptive_callback)
    else:
        status = libca.ca_context_create(libca.ca_disable_preemptive_callback)

    return ECA(status)


def destroy_context():
    """
    Shut down the calling thread's channel access client context and free any resources allocated.
    Detach the calling thread from any CA client context.

    Any user-created threads that have attached themselves to the CA context must stop using it
    prior to its being destroyed.

    On many OS that execute programs in a process based environment the resources used by the client library
    such as sockets and allocated memory are automatically released by the system when the process exits and
    :func:`destroy_context` hasn't been called, but on light weight systems such as vxWorks or RTEMS
    no cleanup occurs unless the application calls :func:`destroy_context`.
    """
    context = libca.ca_current_context()
    if context != ffi.NULL and context in __exception_callback:
        del __exception_callback[context]

    libca.ca_context_destroy()


def attach_context(context):
    """
    :param cdata context: The CA context to join with.
    :return:
        - :data:`ECA.NORMAL` - Normal successful completion
        - :data:`ECA.NOTTHREADED` - Context is not preemptive so cannot be joined
        - :data:`ECA.ISATTACHED` - Thread already attached to a CA context

    The calling thread becomes a member of the specified CA context.
    If context is non preemptive, then additional threads are not allowed to join the CA context
    because allowing other threads to join implies that CA callbacks will be called preemptively
    from more than one thread.
    """
    status = libca.ca_attach_context(context)
    return ECA(status)


def detach_context():
    """
    Detach from any CA context currently attached to the calling thread.

    This does not cleanup or shutdown any currently attached CA context.
    """
    libca.ca_detach_context()


def current_context():
    """
    :return: The current thread's CA context. If none then None is returned.
    """
    context = libca.ca_current_context()
    if context == ffi.NULL:
        context = None
    return context


def show_context(context=None, level=0):
    """
    Prints information about the client context including, at higher interest levels, status for each channel.

    :param context: The CA context to examine. Default is the calling threads CA context.
    :param level:   The interest level. Increasing level produces increasing detail.
    :type context:  cdata, None
    :type level:    int
    """
    if context is None:
        libca.ca_client_status(level)
    else:
        libca.ca_context_status(context, level)


@ffi.callback('void(*)(struct connection_handler_args)')
def _connect_callback(arg):
    epics_arg = {
        'chid': arg.chid,
        'op':   CA_OP(arg.op)
    }

    # If chid is not in cache, it well indicates
    # that the python object has been garbage collected.
    # Then don't try to call from_handle, that is undefined and may crash.
    if arg.chid not in __channels:
        return

    user_callback = __channels[arg.chid]['connection_callback']

    if callable(user_callback):
        user_callback(epics_arg)


def create_channel(name, callback=None, priority=CA_PRIORITY.DEFAULT):
    """
    This function creates a CA channel.

    :param name:        Process variable name string.
    :param callback:    Optional user's call back function to be run when the connection state changes.
                        Casual users of channel access may decide to leave it None if they do not need to
                        have a call back function run in response to each connection state change event.
                        The callback receives one *dict* argument including the following fields:

                        =====   =============
                        field   value
                        =====   =============
                        chid    channel identifier
                        op      - CA_OP.CONN_UP - connected
                                - CA_OP.CONN_DOWN - disconnected
                        =====   =============

    :param priority:    The priority level for dispatch within the server or network,
                        with 0 specifying the lowest dispatch priority and 99 the highest.
                        This parameter currently does not impact dispatch priorities within the client,
                        but this might change in the future.
                        The abstract priority range specified is mapped into an operating system specific
                        range of priorities within the server.
                        This parameter is ignored if the server is running on a network or operating system
                        that does not have native support for prioritized delivery or execution respectively.
                        Specifying many different priorities within the same program can increase resource consumption
                        in the client and the server because an independent virtual circuit, and associated
                        data structures, is created for each priority that is used on a particular server.
    :type name:         str
    :type callback:     callable, None
    :type priority:     int, :class:`CA_PRIORITY`
    :return:            (:class:`ECA`, channel identifier or None)

                        - :data:`ECA.NORMAL` - Normal successful completion
                        - :data:`ECA.BADSTR` - Invalid string
                        - :data:`ECA.BADPRIORITY` - Invalid priority
                        - :data:`ECA.UNAVAILINSERV` - Not supported by attached service
                        - :data:`ECA.ALLOCMEM` - Unable to allocate memory

    The CA client library will attempt to establish and maintain a virtual circuit between the caller's application
    and a named process variable in a CA server. Each call to ca_create_channel allocates resources
    in the CA client library and potentially also a CA server.
    The function :func:`clear_channel` is used to release these resources.

    If successful, the routine returns a channel identifier. This identifier can be used with any channel access call
    that operates on a channel.

    The circuit may be initially connected or disconnected depending on the state of the network
    and the location of the channel. A channel will only enter a connected state
    after the server's address is determined, and only if channel access successfully establishes a virtual circuit
    through the network to the server. Channel access routines that send a request to a server
    will return :data:`ECA.DISCONNCHID` if the channel is currently disconnected.

    There are two ways to obtain asynchronous notification when a channel enters a connected state.

    - The first and simplest method requires that you call ca_pend_io(), and wait for successful completion,
      prior to using a channel that was created without specifying call back function.

    - The second method requires that you register a connection handler
      by supplying a valid connection callback function pointer. This connection handler is called whenever
      the connection state of the channel changes. If you have installed a connection handler
      then :func:`pend_io` will not block waiting for the channel to enter a connected state.

    The function :func:`state` can be used to test the connection state of a channel.
    Valid connections may be isolated from invalid ones with this function :func:`pend_io` times out.

    Due to the inherently transient nature of network connections the order of connection call backs
    relative to the order that :func:`create_channel` calls are made by the application
    can't be guaranteed, and application programs may need to be prepared for a connected channel to
    enter a disconnected state at any time.

    """
    name = to_bytes(name)

    pchid = ffi.new('chid *')

    if callable(callback):
        connect_callback = _connect_callback
    else:
        connect_callback = ffi.NULL

    status = libca.ca_create_channel(name, connect_callback, ffi.NULL, priority, pchid)
    if status != ECA_NORMAL:
        return ECA(status), None

    chid = pchid[0]
    __channels[chid] = {'callbacks': set(), 'monitors': {}}

    if callable(callback):
        __channels[chid]['connection_callback'] = callback
    else:
        __channels[chid]['connection_callback'] = None

    return ECA(status), chid


def change_connection_event(chid, callback=None):
    """
    Change the connection event callback function.

    :param chid:        Channel identifier
    :param callback:    User's call back function to be run when the connection state changes. The callback receives
                        the same argument as :func:`create_channel`. This will replace the previous connection callback
                        function. If an invalid *callback* is given, no connection callback is used.
    :return:
        - :datA:`ECA.NORMAL` - Normal successful completion
        - :data:`ECA.BADCHID` - Corrupted CHID

    """
    if chid not in __channels:
        return ECA.BADCHID

    if callable(callback):
        __channels[chid]['connection_callback'] = callback
        status = libca.ca_change_connection_event(chid, _connect_callback)
    else:
        __channels[chid]['connection_callback'] = None
        status = libca.ca_change_connection_event(chid, ffi.NULL)

    # store the reference so it won't be garbage collected
    return ECA(status)


@ffi.callback('void(*)(struct access_rights_handler_args)')
def _access_rights_callback(arg):
    epics_arg = {
        'chid': arg.chid,
        'read_access': arg.ar.access & 0x01 == 0x01,
        'write_access': arg.ar.access & 0x02 == 0x02
    }
    # If chid is not in cache, it well indicates
    # that the python object has been garbage collected.
    # Then don't try to call from_handle, that is undefined and may crash.
    if arg.chid not in __channels:
        return

    callback = __channels[arg.chid]['access_rights_callback']
    if callable(callback):
        callback(epics_arg)


def replace_access_rights_event(chid, callback=None):
    """
    Install or replace the access rights state change callback handler for the specified channel.

    :param chid:     The channel identifier
    :param callback: User supplied call back function. Passing None uninstalls the current handler.
                     The callback receives one *dict* argument including the following fields:

                     ============   =============
                     field          value
                     ============   =============
                     chid           channel identifier
                     read_access    True if with read access rights
                     write_access   True if with write access rights
                     ============   =============

    :type chid:      cdata
    :type callback:  callable, None
    :return:
        - :data:`ECA.NORMAL` - Normal successful completion
        - :data:`ECA.BADCHID` - Corrupted CHID

    The callback handler is called in the following situations.

        - whenever CA connects the channel immediately before the channel's connection handler is called
        - whenever CA disconnects the channel immediately after the channel's disconnect call back is called
        - once immediately after installation if the channel is connected.
        - whenever the access rights state of a connected channel changes

    When a channel is created no access rights handler is installed.
    """
    if chid not in __channels:
        return ECA.BADCHID

    if callable(callback):
        __channels[chid]['access_rights_callback'] = callback
        status = libca.ca_replace_access_rights_event(chid, _access_rights_callback)
    else:
        __channels[chid]['access_rights_callback'] = None
        status = libca.ca_replace_access_rights_event(chid, ffi.NULL)

    return ECA(status)


@ffi.callback('void(struct event_handler_args)')
def _get_callback(arg):
    # If chid or the callback object is not in cache, it well indicates
    # that the python object has been garbage collected.
    # Then don't try to call from_handle, that is undefined and may crash.
    if arg.chid not in __channels or arg.usr not in __channels[arg.chid]['callbacks']:
        return

    user_callback, use_numpy = ffi.from_handle(arg.usr)
    __channels[arg.chid]['callbacks'].remove(arg.usr)

    epics_arg = {
        'chid':   arg.chid,
        'type':   DBR(arg.type),
        'count':  arg.count,
        'status': ECA(arg.status),
        'value':  format_dbr(arg.type, arg.count, arg.dbr, use_numpy)
    }
    if callable(user_callback):
        user_callback(epics_arg)


def get(chid, chtype=None, count=None, callback=None, use_numpy=False):
    """
    Read a scalar or array value from a process variable.

    :param chid:      Channel identifier
    :param chtype:    The external type of the supplied value to be written.
                      Conversion on the server will occur if this does not match the native type.
                      Default is the native type.
    :param count:     Element count to be read from the specified channel.
                      If *callback* is specified, a count of zero means use the current element count from the server.
    :param callback:  User supplied callback function to be run when requested operation completes.
                      The callback receives one *dict* argument including the following fields:

                      ============   =============
                      field          value
                      ============   =============
                      chid           channel identifier
                      type           the type of the item returned, :class:`DBR`
                      count          the element count of the item returned
                      status         status code of the request from the server, :class:`ECA`
                      value          If *type* is a plain type, this is the PV's value. Otherwise it is a dict
                                     containing the meta information associated with this *type*.
                      ============   =============

    :param use_numpy: whether to format numeric waveform as numpy array
    :type chid:       cdata
    :type chtype:     int, :class:`DBR`, None
    :type count:      int, None
    :type callback:   callable, None
    :type use_numpy:  bool
    :return:          (:class:`ECA`, :class:`DBRValue` or None)

                      - :data:`ECA.NORMAL` - Normal successful completion
                      - :data:`ECA.BADTYPE` - Invalid DBR_XXXX type
                      - :data:`ECA.BADCHID` - Corrupted CHID
                      - :data:`ECA.BADCOUNT` - Requested count larger than native element count
                      - :data:`ECA.GETFAIL` - A local database get failed
                      - :data:`ECA.NORDACCESS` - Read access denied
                      - :data:`ECA.ALLOCMEM` - Unable to allocate memory
                      - :data:`ECA.DISCONN` - Channel is disconnected

    When no *callback* is specified, call :meth:`DBRValue.get` to retrieve the value only if :data:`ECA.NORMAL`
    is returned from a subsequent :func:`pend_io`.
    If a connection is lost outstanding ca get requests are not automatically reissued following reconnect.

    When *callback* is specified a value is read from the channel and
    then the user's callback is invoked with a dict containing the value.
    Note that ca_pend_io will not block for the delivery of values.
    If the channel disconnects before a ca get callback request can be completed,
    then the clients call back function is called with failure status.

    All of these functions return :data:`ECA.DISCONN` if the channel is currently disconnected.

    All get requests are accumulated (buffered) and not forwarded to the IOC until one of
    :func:`flush_io`, :func:`pend_io`, or :func:`pend_event` are called.
    This allows several requests to be efficiently sent over the network in one message.

    """
    if chid not in __channels:
        return ECA.BADCHID, None

    if chtype is None:
        chtype = field_type(chid)
    if chtype == DBR.INVALID:
        return ECA.BADTYPE, None

    native_count = element_count(chid)
    if callable(callback):
        if count is None or count < 0 or count > native_count:
            count = native_count
        get_callback = ffi.new_handle((callback, use_numpy))
        status = libca.ca_array_get_callback(chtype, count, chid, _get_callback, get_callback)
        if status == ECA.NORMAL:
            __channels[chid]['callbacks'].add(get_callback)
        return ECA(status), None
    else:
        if count is None or count <= 0 or count > native_count:
            count = native_count
        value = ffi.new('char[]', dbr_size_n(chtype, count))
        status = libca.ca_array_get(chtype, count, chid, value)
        return ECA(status), DBRValue(chtype, count, value, use_numpy)


@ffi.callback('void(struct event_handler_args)')
def _put_callback(arg):
    epics_arg = {
        'chid':   arg.chid,
        'type':   DBR(arg.type),
        'count':  arg.count,
        'status': ECA(arg.status)
    }
    # If chid or the callback object is not in cache, it well indicates
    # that the python object has been garbage collected.
    # Then don't try to call from_handle, that is undefined and may crash.
    if arg.chid not in __channels or arg.usr not in __channels[arg.chid]['callbacks']:
        return

    user_callback = ffi.from_handle(arg.usr)
    __channels[arg.chid]['callbacks'].remove(arg.usr)
    if callable(user_callback):
        user_callback(epics_arg)


def _setup_put(chid, value, chtype=None, count=None):
    """
    Setup the C value for ca put. This is used by both :func:`put` and :func:`sg_put`.
    Return (chtype, count, c_value) tuple.
    """
    if chtype is None:
        chtype = field_type(chid)

    native_count = element_count(chid)
    if count is None or count <= 0 or count > native_count:
        count = native_count

    if isinstance(value, numbers.Number):
        value_count = 1
    elif isinstance(value, collections.Sequence):
        value_count = len(value)
        if isinstance(value, basestring):
            # convert to bytes
            value = to_bytes(value)
            if chtype == DBR.STRING:
                value_count = 1
            elif chtype == DBR.ENUM:
                chtype = DBR.STRING
                value_count = 1
            elif chtype == DBR.CHAR:
                value = [x for x in bytearray(value)] + [0]
                value_count = len(value)
            else:
                value = [float(value)]
                value_count = 1

        if value_count == 1 and chtype != DBR_STRING:
            value = value[0]
    else:
        return chtype, count, None

    # setup c value
    if value_count == 1:
        if chtype == DBR.STRING:
            value = to_bytes(value)
        cvalue = ffi.new(DBR_TYPE_STRING[chtype] + '*', value)
    else:
        if chtype == DBR.STRING:
            value = [to_bytes(x) for x in value]
        cvalue = ffi.new(DBR_TYPE_STRING[chtype] + '[]', value)

    # the actual count requested is the minimum of all three
    count = min(count, native_count, value_count)

    return chtype, count, cvalue


def put(chid, value, chtype=None, count=None, callback=None):
    """
    Write a scalar or array value to a process variable.

    :param chid:     Channel identifier
    :param value:    A scalar or array value to be written to the channel. If *value* is of string type, it will first
                     be convert to bytes using UTF8 codec. And the following conversion may be involved:

                     ============  =============
                     request type  conversion
                     ============  =============
                     DBR.STRING    nothing
                     DBR.ENUM      request type is changed to DBR.STRING
                     DBR.CHAR      a list of byte integers
                     Other types   a float number
                     ============  =============
    :param chtype:   The external type of the supplied value to be written.
                     Conversion on the server will occur if this does not match the native type.
                     Default is the native type.
    :param count:    Element count to be written to the channel. Default is native element count.
                     But it can be reduced to match the length of user supplied value.
    :param callback: User supplied callback function to be run when requested operation completes.
                     The callback receives one *dict* argument including the following fields:

                     ============   =============
                     field          value
                     ============   =============
                     chid           channel identifier
                     type           DBR.INVALID (-1)
                     count          0
                     status         status code of the request from the server, :class:`ECA`
                     ============   =============

    :type chid:      cdata
    :type value:     int, float, bytes, str, tuple, list, array
    :type chtype:    int, :class:`DBR`, None
    :type count:     int, None
    :type callback:  callable, None
    :return:
        - :data:`ECA.NORMAL` - Normal successful completion
        - :data:`ECA.BADCHID` - Corrupted CHID
        - :data:`ECA.BADTYPE` - Invalid DBR_XXXX type
        - :data:`ECA.BADCOUNT` - Requested count larger than native element count
        - :data:`ECA.STRTOBIG` - Unusually large string supplied
        - :data:`ECA.NOWTACCESS` - Write access denied
        - :data:`ECA.ALLOCMEM` - Unable to allocate memory
        - :data:`ECA.DISCONN` - Channel is disconnected

    When invoked without callback the client will receive no response unless the request
    can not be fulfilled in the server. If unsuccessful an exception handler is run on the client side.

    When invoked with callback the user supplied asynchronous call back is called only
    after the initiated write operation, and all actions resulting from the initiating write operation, complete.

    If unsuccessful the call back function is invoked indicating failure status.

    If the channel disconnects before a put callback request can be completed, then the client's call back function is
    called with failure status, but this does not guarantee that the server did not receive and process the request
    before the disconnect. If a connection is lost and then resumed outstanding ca put requests are not automatically
    reissued following reconnect.

    All of these functions return :data:`ECA.DISCONN` if the channel is currently disconnected.

    All put requests are accumulated (buffered) and not forwarded to the IOC until
    one of :func:`flush_io`, :func:`pend_io`, or :func:`pend_event` are called.
    This allows several requests to be efficiently combined into one message.

    """
    if chid not in __channels:
        return ECA.BADCHID

    chtype, count, cvalue = _setup_put(chid, value, chtype, count)

    if cvalue is None:
        return ECA.BADTYPE

    if callback is None or not callable(callback):
        status = libca.ca_array_put(chtype, count, chid, cvalue)
    else:
        put_callback = ffi.new_handle(callback)
        __channels[chid]['callbacks'].add(put_callback)
        status = libca.ca_array_put_callback(chtype, count, chid, cvalue, _put_callback, put_callback)

    return ECA(status)


@ffi.callback('void(struct event_handler_args)')
def _event_callback(arg):
    # If chid or the callback object is not in cache, it well indicates
    # that the python object has been garbage collected.
    # Then don't try to call from_handle, that is undefined and may crash.
    if arg.chid not in __channels or arg.usr not in __channels[arg.chid]['monitors'].values():
        return

    user_callback, use_numpy = ffi.from_handle(arg.usr)

    epics_arg = {
        'chid':   arg.chid,
        'type':   DBR(arg.type),
        'count':  arg.count,
        'status': ECA(arg.status),
        'value':  format_dbr(arg.type, arg.count, arg.dbr, use_numpy)
    }
    if callable(user_callback):
        user_callback(epics_arg)


def create_subscription(chid, callback, chtype=None, count=None, mask=None, use_numpy=False):
    """
    Register a state change subscription and specify a call back function to be invoked
    whenever the process variable undergoes significant state changes.

    :param chid:      Channel identifier
    :param callback:  User supplied callback function to be run when requested operation completes.
                      The callback receives one *dict* argument including the following fields:

                      ============   =============
                      field          value
                      ============   =============
                      chid           channel identifier
                      type           the type of the item returned, :class:`DBR`
                      count          the element count of the item returned
                      status         status code of the request from the server, :class:`ECA`
                      value          If *type* is a plain type, this is the PV's value. Otherwise it is a dict
                                     containing the meta information associated with this *type*.
                      ============   =============

    :param chtype:    The external type of the supplied value to be written.
                      Conversion will occur if this does not match the native type.
                      Default is the native type.
    :param count:     Element count to be written to the channel. Default is native element count.
    :param mask:      A mask with bits set for each of the event trigger types requested.
                      The event trigger mask must be a bitwise or of one or more of :class:`DBE`.
    :param use_numpy: whether to format numeric waveform as numpy array
    :type chid:       cdata
    :type callback:   callable
    :type chtype:     :class:`DBR`, None
    :type count:      int, None
    :type mask:       :class:`DBE`, None
    :type use_numpy:  bool

    :return: (:class:`ECA`, event identifier or None)

                - :data:`ECA.NORMAL` - Normal successful completion
                - :data:`ECA.BADCHID` - Corrupted CHID
                - :data:`ECA.BADTYPE` - Invalid DBR_XXXX type
                - :data:`ECA.ALLOCMEM` - Unable to allocate memory
                - :data:`ECA.ADDFAIL` - A local database event add failed


    A significant change can be a change in the process variable's value, alarm status, or alarm severity.
    In the process control function block database the deadband field determines
    the magnitude of a significant change for the process variable's value.
    Each call to this function consumes resources in the client library and potentially a CA server
    until one of :func:`clear_channel` or :func:`clear_subscription` is called.

    Subscriptions may be installed or canceled against both connected and disconnected channels.
    The specified *callback* is called once immediately after the subscription is installed
    with the process variable's current state if the process variable is connected.
    Otherwise, the specified *callback* is called immediately after establishing a connection
    (or reconnection) with the process variable. The specified *callback* is called immediately
    with the process variable's current state from within :func:`create_subscription`
    if the client and the process variable share the same address space.

    If a subscription is installed on a channel in a disconnected state
    then the requested count will be set to the native maximum element count of the channel
    if the requested count is larger.

    All subscription requests such as the above are accumulated (buffered)
    and not forwarded to the IOC until one of :func:`flush_io`, :func:`pend_io`, or :func:`pend_event` are called.
    This allows several requests to be efficiently sent over the network in one message.

    If at any time after subscribing, read access to the specified process variable is lost,
    then the call back will be invoked immediately indicating that read access was lost via the status argument.
    When read access is restored normal event processing will resume starting always
    with at least one update indicating the current state of the channel.

    """
    if chid not in __channels:
        return ECA.BADCHID, None

    if chtype is None:
        chtype = field_type(chid)
    if chtype == DBR.INVALID:
        return ECA.BADTYPE, None

    # count = 0 is valid for subscription. It means only the number of changes elements.
    native_count = element_count(chid)
    if count is None or count < 0 or count > native_count:
        count = native_count

    if mask is None:
        mask = DBE.VALUE | DBE.ALARM

    pevid = ffi.new('evid *')

    monitor_callback = ffi.new_handle((callback, use_numpy))

    status = libca.ca_create_subscription(chtype, count, chid, mask, _event_callback, monitor_callback, pevid)
    if status != ECA_NORMAL:
        return ECA(status), None

    evid = pevid[0]
    __channels[chid]['monitors'][evid] = monitor_callback

    return ECA(status), evid


def clear_subscription(evid):
    """
    Cancel a subscription.

    :param cdata evid: event id returned by :meth:`create_subscription`
    :return:
        - ECA.NORMAL - Normal successful completion
        - ECA.BADCHID - Corrupted CHID

    All cancel-subscription requests such as the above are accumulated (buffered) and not forwarded to the server
    until one of :func:`flush_io`, :func:`pend_io`, or :func:`pend_event` are called.
    This allows several requests to be efficiently sent together in one message.

    """
    status = libca.ca_clear_subscription(evid)
    chid = libca.ca_evid_to_chid(evid)

    if chid not in __channels:
        return ECA.BADCHID

    if evid in __channels[chid]['monitors']:
        del __channels[chid]['monitors'][evid]

    return ECA(status)


def clear_channel(chid):
    """
    Shutdown and reclaim resources associated with a channel created by ca_create_channel().

    :param cdata chid: Channel identifier
    :return:
        - :data:`ECA.NORMAL` - Normal successful completion
        - :data:`ECA.BADCHID` - Corrupted CHID

    All remote operation requests such as the above are accumulated (buffered) and not forwarded to the IOC
    until one of :func:`flush_io`, :func:`pend_io` or :func:`pend_event` are called.
    This allows several requests to be efficiently sent over the network in one message.

    Clearing a channel does not cause its disconnect handler to be called,
    but clearing a channel does shutdown and reclaim any channel state change event subscriptions (monitors)
    registered with the channel.

    """
    if chid not in __channels:
        return ECA.BADCHID

    # clear all subscriptions for this channel
    for evid in list(__channels[chid]['monitors']):
        clear_subscription(evid)

    status = libca.ca_clear_channel(chid)

    # remove from channels list
    del __channels[chid]

    return ECA(status)


def pend_event(timeout):
    """
    The send buffer is flushed and CA background activity is processed for *timeout* seconds.

    :param float timeout: The duration to block in this routine in seconds. A timeout of zero seconds blocks forever.
    :return:
        - :data:`ECA.TIMEOUT` - The operation timed out
        - :data:`ECA.EVDISALLOW` - Function inappropriate for use within a call back handler


    The :func:`pend_event` function will not return before the specified timeout expires and
    all unfinished channel access labor has been processed, and unlike :func:`pend_io`
    returning from the function does not indicate anything about the status of pending IO requests.

    It return :data:`ECA.TIMEOUT` when successful. This behavior probably isn't intuitive,
    but it is preserved to insure backwards compatibility.

    See also Thread Safety and Preemptive Callback to User Code.
    """
    status = libca.ca_pend_event(timeout)
    return ECA(status)


def poll():
    """
    The send buffer is flushed and any outstanding CA background activity is processed.

    .. note:: same as pend_event(1e-12)

    """
    status = libca.ca_pend_event(1e-12)
    return ECA(status)


def pend_io(timeout):
    """
    This function flushes the send buffer and then blocks until outstanding get requests *without* callback complete,
    and until channels created *without* callback connect for the first time.

    :param float timeout: Specifies the time out interval. A timeout interval of zero specifies forever.
    :return:
        - :data:`ECA.NORMAL` - Normal successful completion
        - :data:`ECA.TIMEOUT` - Selected IO requests didn't complete before specified timeout
        - :data:`ECA.EVDISALLOW` - Function inappropriate for use within an event handler

    If :data:`ECA.NORMAL` is returned then it can be safely assumed that
    all outstanding get requests *without* callback have completed successfully and
    channels created *without* callback have connected for the first time.

    If :data:`ECA.TIMEOUT` is returned then it must be assumed for all previous get requests and
    properly qualified first time channel connects have failed.

    If :data:`ECA.TIMEOUT` is returned then get requests may be reissued
    followed by a subsequent call to :func:`pend_io`.
    Specifically, the function will block only for outstanding get requests issued,
    and also any channels created *without* callback,
    after the last call to ca_pend_io() or ca client context creation whichever is later.
    Note that :func:`create_channel` requests generally should not be reissued for the same process variable
    unless :func:`clear_channel` is called first.

    If no get or connection state change events are outstanding then :func:`pend_io` will flush the send buffer and
    return immediately without processing any outstanding channel access background activities.

    The delay specified should take into account worst case network delays
    such as Ethernet collision exponential back off until retransmission delays
    which can be quite long on overloaded networks.

    Unlike :func:`pend_event`, this routine will not process CA's background activities
    if none of the selected IO requests are pending.

    """
    status = libca.ca_pend_io(timeout)
    return ECA(status)


def pend(timeout, early):
    """
    :param float timeout: Specifies the time out interval. A timeout interval of zero specifies forever.
    :param bool early: Call :func:`pend_io` if *early* is True otherwise :func:`pend_event` is called
    :return:
        - :data:`ECA.NORMAL` - Normal successful completion
        - :data:`ECA.TIMEOUT` - Selected IO requests didn't complete before specified timeout
        - :data:`ECA.EVDISALLOW` - Function inappropriate for use within an event handler

    """
    status = libca.ca_pend(timeout, early)
    return ECA(status)


def test_io():
    """
    This function tests to see if all get requests are complete and channels created without
    a connection callback function are connected. It will report the status of outstanding get requests issued,
    and channels created without connection callback function,
    after the last call to ca_pend_io() or CA context initialization whichever is later.

    :return:
        - :data:`ECA.IODONE` - All IO operations completed
        - :data:`ECA.IOINPROGRESS` - IO operations still in progress
    """
    status = libca.ca_test_io()
    return ECA(status)


def flush_io():
    """
    Flush outstanding IO requests to the server.

    :return:
        - :data:`ECA.NORMAL` - Normal successful completion

    This routine might be useful to users who need to flush requests prior to performing client side labor
    in parallel with labor performed in the server.
    Outstanding requests are also sent whenever the buffer which holds them becomes full.
    """
    status = libca.ca_flush_io()
    return ECA(status)


def field_type(chid):
    """
    :param cdata chid: channel identifier
    :return: the native type in the server of the process variable.
    :rtype: :class:`DBF`
    """
    return DBF(libca.ca_field_type(chid))


def element_count(chid):
    """
    :param cdata chid: channel identifier
    :return: the maximum array element count in the server for the specified IO channel.
    """
    # ca_element_count returns long in C, and cffi convert to a `long` in Python.
    # In Python 2, the `long` type has a *L* suffix when displayed. This is disturbing since mostly this number will
    # not exceed the integer range. In Python 3, there is only a `long` type for integers and without *L* suffix.
    # Only for the sake of visual pleasure, the number is converted to `int` in Python 2. In any case, if the number
    # indeed exceeds 2*31-1 (on 32bit) or 2**63-1 (on 64bit), it gets up casted to `long`.
    count = libca.ca_element_count(chid)
    if sys.hexversion < 0x03000000:
        return int(count)
    else:
        return count


def name(chid):
    """
    :param cdata chid: channel identifier
    :return: the name provided when the supplied channel id was created.
    """
    return to_string(ffi.string(libca.ca_name(chid)))


def state(chid):
    """
    :param cdata chid: channel identifier
    :return: the connection state
    :rtype: :class:`ChannelState`
    """
    if chid is None:
        return ChannelState.NEVER_SEARCH
    else:
        return ChannelState(libca.ca_state(chid))


def message(status):
    """
    :param int status: CA status code
    :return: a message corresponding to a user specified CA status code.
    """
    return to_string(ffi.string(libca.ca_message(status)))


def host_name(chid):
    """
    :param chid: channel identifier
    :return: the name of the host to which a channel is currently connected.
    """
    cstring = ffi.new('char[256]')
    libca.ca_get_host_name(chid, cstring, 256)
    return to_string(ffi.string(cstring))


def read_access(chid):
    """
    :param chid: channel identifier
    :return: True if the client currently has read access to the specified channel and False otherwise.
    """
    return libca.ca_read_access(chid) == 1


def write_access(chid):
    """
    :param chid: channel identifier
    :return: True if the client currently has write access to the specified channel and False otherwise.
    """
    return libca.ca_write_access(chid) == 1


def sg_create():
    """
    Create a synchronous group and return an identifier for it.

    :return: (:class:`ECA`, int or None)

    A synchronous group can be used to guarantee that a set of channel access requests have completed.
    Once a synchronous group has been created then channel access get and put requests may be issued
    within it using :func:`sg_get` and :func:`sg_put` respectively.
    The routines :func:`sg_block` and :func:`sg_test` can be used to block for and test for completion respectively.
    The routine :func:`sg_reset` is used to discard knowledge of old requests which have timed out and
    in all likelihood will never be satisfied.

    Any number of asynchronous groups can have application requested operations outstanding
    within them at any given time.

    """
    pgid = ffi.new('CA_SYNC_GID *')
    status = libca.ca_sg_create(pgid)
    if status != ECA_NORMAL:
        return ECA(status), None
    else:
        gid = pgid[0]
        return ECA(status), gid


def sg_delete(gid):
    """
    Deletes a synchronous group.

    :param int gid: Identifier of the synchronous group to be deleted.
    :return:
        - :data:`ECA.NORMAL` - Normal successful completion
        - :data:`ECA.BADSYNCGRP` - Invalid synchronous group
    """
    status = libca.ca_sg_delete(gid)
    return ECA(status)


def sg_block(gid, timeout):
    """
    Flushes the send buffer and then waits until outstanding requests complete or the specified time out expires.
    At this time outstanding requests include calls to :func:`sg_get` and calls to :func:`sg_put`.
    If :data:`ECA.TIMEOUT` is returned then failure must be assumed for all outstanding queries.
    Operations can be reissued followed by another :func:`sg_block`.
    This routine will only block on outstanding queries issued after the last call to :func:`sg_block`,
    :func:`sg_reset`, or :func:`sg_create` whichever occurs later in time.
    If no queries are outstanding then :func:`sg_block` will return immediately
    without processing any pending channel access activities.

    Values written into your program's variables by a channel access synchronous group request should not be
    referenced by your program until :data:`ECA.NORMAL` has been received from :func:`sg_block`.
    This routine will process pending channel access background activity while it is waiting.

    :param int gid:       Identifier of the synchronous group.
    :param float timeout: Specifies the time out interval. A timeout interval of zero specifies forever.
    :return:
        - :data:`ECA.NORMAL` - Normal successful completion
        - :data:`ECA.TIMEOUT` - The operation timed out
        - :data:`ECA.EVDISALLOW` - Function inappropriate for use within an event handler
        - :data:`ECA.BADSYNCGRP` - Invalid synchronous group
    """
    status = libca.ca_sg_block(gid, timeout)
    return ECA(status)


def sg_test(gid):
    """
    Test to see if all requests made within a synchronous group have completed.

    :param int gid: Identifier of the synchronous group.
    :return:
        - :data:`ECA.IODONE` - IO operations completed
        - :data:`ECA.IOINPROGRESS` - Some IO operations still in progress
    """
    status = libca.ca_sg_test(gid)
    return ECA(status)


def sg_reset(gid):
    """
    Reset the number of outstanding requests within the specified synchronous group to zero so that
    :func:`sg_test` will return True and :func:`sg_block` will not block unless additional subsequent requests are made.

    :param int gid: Identifier of the synchronous group.
    :return:
        - :data:`ECA.NORMAL` - Normal successful completion
        - :data:`ECA.BADSYNCGRP` - Invalid synchronous group
    """
    status = libca.sg_reset(gid)
    return ECA(status)


def sg_put(gid, chid, value, chtype=None, count=None):
    """
    Write a value, or array of values, to a channel and increment the outstanding request count of a synchronous group.

    :param gid:    Synchronous group identifier
    :param chid:   Channel identifier
    :param value:  The value or array of values to write. If *value* is of string type, it will first
                     be convert to bytes using UTF8 codec. And the following conversion may be involved:

                     ============  =============
                     request type  conversion
                     ============  =============
                     DBR.STRING    nothing
                     DBR.ENUM      request type is changed to DBR.STRING
                     DBR.CHAR      a list of byte integers
                     Other types   a float number
                     ============  =============

    :param chtype: The type of supplied value.
                   Conversion on the server will occur if it does not match the native type.
    :param count:  The element count to be written to the specified channel.
    :type gid:     int
    :type chid:    cdata
    :type value:   int, float, bytes, str, tuple, list, array
    :type chtype:  int, :class:`DBR`
    :return:
        - :data:`ECA.NORMAL` - Normal successful completion
        - :data:`ECA.BADSYNCGRP` - Invalid synchronous group
        - :data:`ECA.BADCHID` - Corrupted CHID
        - :data:`ECA.BADTYPE` - Invalid DBR_XXXX type
        - :data:`ECA.BADCOUNT` - Requested count larger than native element count
        - :data:`ECA.STRTOBIG` - Unusually large string supplied
        - :data:`ECA.PUTFAIL` - A local database put failed

    All remote operation requests such as the above are accumulated (buffered) and not forwarded to the server
    until one of :func:`flush_io`, :func:`pend_io` or :func:`pend_event` are called.
    This allows several requests to be efficiently sent in one message.

    If a connection is lost and then resumed outstanding puts are not reissued.
    """
    chtype, count, cvalue = _setup_put(chid, value, chtype, count)

    if cvalue is None:
        return ECA.BADTYPE

    status = libca.ca_sg_array_put(gid, chtype, count, chid, cvalue)

    return ECA(status)


def sg_get(gid, chid, chtype=None, count=None, use_numpy=False):
    """
    Read a value from a channel and increment the outstanding request count of a synchronous group.

    :param gid:       Identifier of the synchronous group.
    :param chid:      Channel identifier
    :param chtype:    External type of returned value.
                      Conversion on the server will occur if this does not match native type.
    :param count:     Element count to be read from the specified channel.
    :param use_numpy: whether to format numeric waveform as numpy array
    :type gid:        int
    :type chid:       cdata
    :type chtype:     int, :class:`DBR`, None
    :type count:      int, None
    :return: (:class:`ECA`, :class:`DBRValue` or None)

                    - :data:`ECA.NORMAL` - Normal successful completion
                    - :data:`ECA.BADSYNCGRP` - Invalid synchronous group
                    - :data:`ECA.BADCHID` - Corrupted CHID
                    - :data:`ECA.BADCOUNT` - Requested count larger than native element count
                    - :data:`ECA.BADTYPE` - Invalid DBR_XXXX type
                    - :data:`ECA.GETFAIL` - A local database get failed

    Call :meth:`DBRValue.get` to retrieve the value only if :data:`ECA.NORMAL` has been received from ca_sg_block ,
    or until :func:`sg_test` returns True.

    All remote operation requests such as the above are accumulated (buffered) and not forwarded to the server
    until one of :func:`flush_io`, :func:`pend_io`, or :func:`pend_event` are called.
    This allows several requests to be efficiently sent in one message.

    If a connection is lost and then resumed outstanding gets are not reissued.
    """
    native_count = element_count(chid)
    if count is None or count <= 0 or count > native_count:
        count = native_count

    if chtype is None:
        chtype = libca.ca_field_type(chid)

    cvalue = ffi.new('char[]', dbr_size_n(chtype, count))
    status = libca.ca_sg_array_get(gid, chtype, count, chid, cvalue)
    if status != ECA_NORMAL:
        return ECA(status), None
    else:
        return ECA(status), DBRValue(chtype, count, cvalue, use_numpy)


def version():
    """
    :return: CA version string
    :rtype: str
    """
    return to_string(ffi.string(libca.ca_version()))
