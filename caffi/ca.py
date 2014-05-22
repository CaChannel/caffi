"""
The is the low level access to EPICS channel access library. It maps the corresponding C API to Python functions.
Even though as same as possible, there are subtle differences:

  - The `ca_` prefix of the function name has been removed, e.g. C function `ca_create_channel` is now Python function `create_channel`.

  - The order of the argument might have been altered to be allow default arguments, thus more pythonic.
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

        put(chid, value, dbrType=None, count=None, callback=None, args=())

    Only two arguments are mandatory, which are the channel identifier and the value to write.
    The others are made optional and have reasonable defaults.

  - In C API the callback function handler has the following signature,
    ::

        void (*)(struct xxx_handler_args)

    In Python counterpart, the callback signature is
    ::

        def callback(epicsArgs, userArgs):

    *epicsArgs* is a dict converted from `xxx_handler_args`. *userArgs* is a tuple supplied by user when the callback is registered.

"""
from __future__ import (print_function, absolute_import)

# compatible to python 3
import sys
if sys.hexversion >= 0x03000000:
    basestring = [str, bytes]

# globals
__channels = {}
__monitors = {}
__exception_callback = None

from ._ca import *
from .constants import *
from .dbr import *

# macros defined in C, rewrote as functions

DBR_TYPE_STRING = {
    DBR_STRING : 'dbr_string_t',
    DBR_INT:     'dbr_int_t',
    DBR_FLOAT:   'dbr_float_t',
    DBR_CHAR:    'dbr_char_t',
    DBR_ENUM:    'dbr_enum_t',
    DBR_LONG:    'dbr_long_t',
    DBR_DOUBLE:  'dbr_double_t',
}

@ffi.callback('void(*)(struct exception_handler_args)')
def _exceptionCB(carg):
    epics_arg = {
        'chid'  : carg.chid,
        'type'  : carg.type,
        'count' : carg.count,
        'addr'  : carg.addr,
        'stat'  : carg.stat,
        'op'    : carg.op,
        'ctx'   : carg.ctx,
        'file'  : ffi.string(carg.pFile),
        'lineNo': carg.lineNo
    }
    user_callback, user_arg = ffi.from_handle(carg.usr)
    if callable(user_callback):
        user_callback(epics_arg, user_arg)

def add_exception_event(callback=None, args=()):
    """
    Replace the currently installed CA context global exception handler call back.

    :param callback:    User callback function to be executed when an exceptions occur.
                        Passing None causes the default exception handler to be reinstalled.
                        The first argument is a dict including the following fields: *chid*, *type*,
                        *count*, *addr*, *stat*, *op*, *ctx*, *file*, *lineNo*.
    :param arg:         User variable retained and passed back to user function above as the second argument.

    :return: ECA_NORMAL

    When an error occurs in the server asynchronous to the clients thread then information about this type of error
    is passed from the server to the client in an exception message. When the client receives this exception message
    an exception handler callback is called.
    The default exception handler prints a diagnostic message on the client's standard out and
    terminates execution if the error condition is severe.

    .. note::   Certain fields in first argument are not applicable in the context of some error messages.
                For instance, a failed get will supply the address in the client task
                where the returned value was requested to be written.
                For other failed operations the value of the addr field should not be used.

    """
    # keep a reference to the returned pointer of (callback, args),
    # otherwise it will be garbage collected
    global __exception_callback
    __exception_callback = ffi.new_handle((callback, args))
    status = libca.ca_add_exception_event(_exceptionCB, __exception_callback)
    return status



@ffi.callback('void(struct event_handler_args)')
def _eventCB(arg):
    epics_arg = {
        'chid'  : arg.chid,
        'type'  : arg.type,
        'count' : arg.count,
        'status': arg.status,
        'value' : format_dbr(arg.type, arg.count, arg.dbr)
    }
    user_callback, user_arg = ffi.from_handle(arg.usr)
    if (callable(user_callback)):
        user_callback(epics_arg, user_arg)


def create_context(preemptive_callback=True):
    """
    :param bool preemptive_callback: enable preemptive callback
    :return:
                - ECA_NORMAL - Normal successful completion
                - ECA_ALLOCMEM - Failed, unable to allocate space in pool
                - ECA_NOTTHREADED - Current thread is already a member of a non-preemptive callback CA context (possibly created implicitly)

    This function, or :func:`attach_context`, should be called once from each thread prior to
    making any of the other Channel Access calls. If one of the above is not called before
    making other CA calls then a non-preemptive context is created by default,
    and future attempts to create a preemptive context for the current threads will fail.

    If preemptive callback is disabled then additional threads are not allowed to
    join the CA context using :func:`attach_context` because allowing other threads to join implies
    that CA callbacks will be called preemptively from more than one thread.

    """
    if preemptive_callback:
        return libca.ca_context_create(libca.ca_enable_preemptive_callback)
    else:
        return libca.ca_context_create(libca.ca_disable_preemptive_callback)


def destroy_context():
    """
    Shut down the calling thread's channel access client context and free any resources allocated.
    Detach the calling thread from any CA client context.

    Any user-created threads that have attached themselves to the CA context must stop using it prior to its being destroyed.

    On many OS that execute programs in a process based environment the resources used by the client library
    such as sockets and allocated memory are automatically released by the system when the process exits and
    :func:`destroy_context` hasn't been called, but on light weight systems such as vxWorks or RTEMS
    no cleanup occurs unless the application calls :func:`destroy_context`.
    """
    libca.ca_context_destroy()


def attach_context(context):
    """
    :param context: The CA context to join with.
    :return:
                - ECA_NORMAL - Normal successful completion
                - ECA_NOTTHREADED - Context is not preemptive so cannot be joined
                - ECA_ISATTACHED - Thread already attached to a CA context

    The calling thread becomes a member of the specified CA context.
    If context is non preemptive, then additional threads are not allowed to join the CA context
    because allowing other threads to join implies that CA callbacks will be called preemptively from more than one thread.
    """
    libca.ca_attach_context(context)


def current_context():
    """
    :return: The current thread's CA context. If none then None is returned.
    """
    context = libca.ca_current_context()
    if context == ffi.NULL:
        context = None
    return None

def show_context(context=None, level=0):
    """
    Prints information about the client context including, at higher interest levels, status for each channel.

    :param context: The CA context to examine. Default is the calling threads CA context.
    :param level: The interest level. Increasing level produces increasing detail.

    """
    if context is None:
        libca.ca_client_status(level)
    else:
        libca.ca_context_status(context, level)


@ffi.callback('void(*)(struct connection_handler_args)')
def _connectCB(carg):
    epics_arg = {
        'chid'  : carg.chid,
        'up'    : carg.op == CA_OP_CONN_UP
    }

    user_callback, user_arg = ffi.from_handle(libca.ca_puser(carg.chid))
    if callable(user_callback):
        user_callback(epics_arg, user_arg)


def create_channel(name, callback=None, args=(), priority=CA_PRIORITY_DEFAULT):
    """
    This function creates a CA channel.

    :param str name:        Process variable name string.
    :param callable callback:    Optional user's call back function to be run when the connection state changes.
                        Casual users of channel access may decide to leave it None
                        if they do not need to have a call back function run in response to each connection state change event.
    :param tuple args:        The value is retained in storage associated with the specified channel.
                        Casual users of channel access may wish to leave it empty.
    :param int priority:    The priority level for dispatch within the server or network,
                        with 0 specifying the lowest dispatch priority and 99 the highest.
                        This parameter currently does not impact dispatch priorities within the client,
                        but this might change in the future.
                        The abstract priority range specified is mapped into an operating system specific range of priorities within the server.
                        This parameter is ignored if the server is running on a network or operating system
                        that does not have native support for prioritized delivery or execution respectively.
                        Specifying many different priorities within the same program can increase resource consumption
                        in the client and the server because an independent virtual circuit, and associated data structures,
                        is created for each priority that is used on a particular server.
    :return:            The channel identifier.

    The CA client library will attempt to establish and maintain a virtual circuit between the caller's application
    and a named process variable in a CA server.
    Each call to ca_create_channel allocates resources in the CA client library and potentially also a CA server.
    The function :func:`clear_channel` is used to release these resources.
    If successful, the routine returns a channel identifier.
    This identifier can be used with any channel access call that operates on a channel.

    The circuit may be initially connected or disconnected depending on the state of the network and the location of the channel.
    A channel will only enter a connected state after the server's address is determined,
    and only if channel access successfully establishes a virtual circuit through the network to the server.
    Channel access routines that send a request to a server will return *ECA_DISCONNCHID* if the channel is currently disconnected.

    There are two ways to obtain asynchronous notification when a channel enters a connected state.

    - The first and simplest method requires that you call ca_pend_io(), and wait for successful completion,
      prior to using a channel that was created without specifying call back function.

    - The second method requires that you register a connection handler by supplying a valid connection callback function pointer.
      This connection handler is called whenever the connection state of the channel changes.
      If you have installed a connection handler then :func:`pend_io` will not block waiting for the channel to enter a connected state.

    The function :func:`state` can be used to test the connection state of a channel.
    Valid connections may be isolated from invalid ones with this function :func:`pend_io` times out.

    Due to the inherently transient nature of network connections
    the order of connection call backs relative to the order that :func:`create_channel` calls are made by the application
    can't be guaranteed, and application programs may need to be prepared for a connected channel to
    enter a disconnected state at any time.

    """
    pchid = ffi.new('chid *')

    if callable(callback):
        connect_callback = _connectCB
        user_connect_callback = ffi.new_handle((callback, args))
    else:
        connect_callback = ffi.NULL
        user_connect_callback = ffi.NULL
    status = libca.ca_create_channel(name, connect_callback, user_connect_callback, priority, pchid)
    if status == ECA_NORMAL:
        chid = pchid[0]
        __channels[chid] = {'callbacks':set(), 'monitors' : set()}
        if user_connect_callback != ffi.NULL:
            __channels[chid]['callbacks'].add(user_connect_callback)
    else:
        chid = None
    return chid


@ffi.callback('void(struct event_handler_args)')
def _getCB(arg):
    epics_arg = {
        'chid'  : arg.chid,
        'type'  : arg.type,
        'count' : arg.count,
        'status': arg.status,
        'value' : format_dbr(arg.type, arg.count, arg.dbr)
    }

    user_callback, user_arg = ffi.from_handle(arg.usr)
    __channels[arg.chid]['callbacks'].remove(arg.usr)
    if callable(user_callback):
        user_callback(epics_arg, user_arg)


def get(chid, dbrtype=None, count=None, callback=None, args=()):
    """
    Read a scalar or array value from a process variable.

    :param chid: Channel identifier
    :param value: A scalar or array value to be written to the channel
    :param dbrtype: The external type of the supplied value to be written.
                    Conversion will occur if this does not match the native type.
                    Default is the native type.
    :param count:   Element count to be read from the specified channel.
                    If *callback* is specified, a count of zero means use the current element count from the server.
    :param callback: User supplied callback function to be run when requested operation completes.
    :param args: User supplied variable retained and then passed back to user supplied function above
    :return:  Pointer to a buffer where the current value of the channel is to be written.

    When no *callback* is specified the returned channel value can't be assumed to be stable
    in the application supplied buffer until after *ECA_NORMAL* is returned from :func:`pend_io`.
    If a connection is lost outstanding ca get requests are not automatically reissued following reconnect.

    When *callback* is specified a value is read from the channel and
    then the user's callback is invoked with a pointer to the retrieved value.
    Note that ca_pend_io will not block for the delivery of values requested by ca_get_callback.
    If the channel disconnects before a ca get callback request can be completed,
    then the clients call back function is called with failure status.

    All of these functions return *ECA_DISCONN* if the channel is currently disconnected.

    All get requests are accumulated (buffered) and not forwarded to the IOC until one of
    :func:`flush_io`, :func:`pend_io`, or :func:`pend_event` are called.
    This allows several requests to be efficiently sent over the network in one message.

    """
    if count is None or count < 0:
        count = libca.ca_element_count(chid)

    if dbrtype is None:
        dbrtype = libca.ca_field_type(chid)

    if callable(callback):
        get_callback = ffi.new_handle((callback, args))
        __channels[chid]['callbacks'].add(get_callback)
        libca.ca_array_get_callback(dbrtype, count, chid, _getCB, get_callback)
        return None
    else:
        value = ffi.new('char[]', dbr_size_n(dbrtype, count))
        libca.ca_array_get(dbrtype, count, chid, value)
        return value


@ffi.callback('void(struct event_handler_args)')
def _put_callback(arg):
    epics_arg = {
        'chid'  : arg.chid,
        'type'  : arg.type,
        'count' : arg.count,
        'status': arg.status
    }
    user_callback, user_arg = ffi.from_handle(arg.usr)
    __channels[arg.chid]['callbacks'].remove(arg.usr)
    if callable(user_callback):
        user_callback(epics_arg, user_arg)


def put(chid, value, dbrtype=None, count=None, callback=None, args=()):
    """
    Write a scalar or array value to a process variable.

    :param chid: Channel identifier
    :param value: A scalar or array value to be written to the channel
    :param dbrtype: The external type of the supplied value to be written.
                    Conversion will occur if this does not match the native type.
                    Default is the native type.
    :param count: Element count to be written to the channel. Default is native element count. But it can be reduced to
                  match the length of user supplied value.
    :param callback: User supplied callback function to be run when requested operation completes.
    :param args: User supplied variable retained and then passed back to user supplied function above
    :return:
                - ECA_NORMAL - Normal successful completion
                - ECA_BADCHID - Corrupted CHID
                - ECA_BADTYPE - Invalid DBR_XXXX type
                - ECA_BADCOUNT - Requested count larger than native element count
                - ECA_STRTOBIG - Unusually large string supplied
                - ECA_NOWTACCESS - Write access denied
                - ECA_ALLOCMEM - Unable to allocate memory
                - ECA_DISCONN - Channel is disconnected

    When invoked without callback the client will receive no response unless the request can not be fulfilled in the server.
    If unsuccessful an exception handler is run on the client side.

    When invoked with callback the user supplied asynchronous call back is called only
    after the initiated write operation, and all actions resulting from the initiating write operation, complete.

    If unsuccessful the call back function is invoked indicating failure status.

    If the channel disconnects before a put callback request can be completed, then the client's call back function is
    called with failure status, but this does not guarantee that the server did not receive and process the request
    before the disconnect. If a connection is lost and then resumed outstanding ca put requests are not automatically
    reissued following reconnect.

    All of these functions return *ECA_DISCONN* if the channel is currently disconnected.

    All put requests are accumulated (buffered) and not forwarded to the IOC until one of :func:`flush_io`, :func:`pend_io`,
    or :func:`pend_event` are called. This allows several requests to be efficiently combined into one message.
    """
    if dbrtype is None:
        dbrtype = libca.ca_field_type(chid)

    element_count = libca.ca_element_count(chid)
    if count is None or count < 0:
        count = element_count

    # treat single value and sequence differently to create c type value
    try:
        value_count = len(value)
    except TypeError:
        value_count = 1
    else:
        # string type is also a sequence but it is counted as one if DBR_STRING type
        if isinstance(value, basestring) and dbrtype == DBR_STRING:
            value_count = 1

   # setup c value
    if value_count == 1:
        cvalue = ffi.new(DBR_TYPE_STRING[dbrtype]+'*', value)
    else:
        cvalue = ffi.new(DBR_TYPE_STRING[dbrtype]+'[]', value)

    # the actual count requested is the minimum of all three
    count = min(count, element_count, value_count)

    if callback == None or not callable(callback):
        libca.ca_array_put(dbrtype, count, chid, cvalue)
    else:
        put_callback = ffi.new_handle((callback,args,))
        __channels[chid]['callbacks'].add(put_callback)
        libca.ca_array_put_callback(dbrtype, count, chid, cvalue, _put_callback, put_callback)


def create_subscription(chid, callback, args=(), dbrtype=None, count=None, mask=DBE_VALUE|DBE_ALARM):
    """
    Register a state change subscription and specify a call back function to be invoked
    whenever the process variable undergoes significant state changes.

    :param chid: Channel identifier
    :param callback: User supplied callback function to be run when requested operation completes.
    :param args: User supplied variable retained and then passed back to user supplied function above
    :param dbrtype: The external type of the supplied value to be written.
                    Conversion will occur if this does not match the native type.
                    Default is the native type.
    :param count:   Element count to be written to the channel. Default is native element count.
                    But it can be reduced to match the length of user supplied value.
    :param mask:    A mask with bits set for each of the event trigger types requested.
                    The event trigger mask must be a bitwise or of one or more of the following constants.

                    - DBE_VALUE - Trigger events when the channel value exceeds the monitor dead band
                    - DBE_ARCHIVE (or DBE_LOG) - Trigger events when the channel value exceeds the archival dead band
                    - DBE_ALARM - Trigger events when the channel alarm state changes
                    - DBE_PROPERTY - Trigger events when a channel property changes.

    :return:
                - ECA_NORMAL - Normal successful completion
                - ECA_BADCHID - Corrupted CHID
                - ECA_BADTYPE - Invalid DBR_XXXX type
                - ECA_ALLOCMEM - Unable to allocate memory
                - ECA_ADDFAIL - A local database event add failed

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
    if dbrtype is None:
        dbrtype = libca.ca_field_type(chid)

    element_count = libca.ca_element_count(chid)
    if count is None or count < 0 or count > element_count:
        count = element_count

    pevid = ffi.new('evid *')

    monitor_callback = ffi.new_handle((callback,args,))

    status = libca.ca_create_subscription(dbrtype, count, chid, mask, _eventCB, monitor_callback, pevid)

    evid = pevid[0]

    if evid != ffi.NULL:
        __channels[chid]['monitors'].add(evid)
        __monitors[evid] = (chid, monitor_callback)

    return evid


def clear_subscription(evid):
    """
    Cancel a subscription.

    :param evid: event id returned by :meth:`create_subscription`
    :return:
                - ECA_NORMAL - Normal successful completion
                - ECA_BADCHID - Corrupted CHID

    All cancel-subscription requests such as the above are accumulated (buffered) and not forwarded to the server
    until one of :func:`flush_io`, :func:`pend_io`, or :func:`pend_event` are called.
    This allows several requests to be efficiently sent together in one message.

    """
    status = libca.ca_clear_subscription(evid)

    chid = __monitors[evid][0]
    __channels[chid]['monitors'].remove(evid)
    del __monitors[evid]

    return status


def clear_channel(chid):
    """
    Shutdown and reclaim resources associated with a channel created by ca_create_channel().

    :param chid: Channel identifier
    :return:
                - ECA_NORMAL - Normal successful completion
                - ECA_BADCHID - Corrupted CHID

    All remote operation requests such as the above are accumulated (buffered) and not forwarded to the IOC
    until one of :func:`flush_io`, :func:`pend_io` or :func:`pend_event` are called.
    This allows several requests to be efficiently sent over the network in one message.

    Clearing a channel does not cause its disconnect handler to be called,
    but clearing a channel does shutdown and reclaim any channel state change event subscriptions (monitors)
    registered with the channel.

    """
    # clear all subscriptions for this channel
    for evid in list(__channels[chid]['monitors']):
        status = clear_subscription(evid)

    status = libca.ca_clear_channel(chid)

    # remove from channels list
    del __channels[chid]

    return status


def pend_event(timeout):
    """
    The send buffer is flushed and CA background activity is processed for *timeout* seconds.

    :param timeout: The duration to block in this routine in seconds. A timeout of zero seconds blocks forever.
    :return:
                - ECA_TIMEOUT - The operation timed out
                - ECA_EVDISALLOW - Function inappropriate for use within a call back handler


    The :func:`pend_event` function will not return before the specified timeout expires and
    all unfinished channel access labor has been processed, and unlike :func:`pend_io`
    returning from the function does not indicate anything about the status of pending IO requests.

    It return ECA_TIMEOUT when successful. This behavior probably isn't intuitive,
    but it is preserved to insure backwards compatibility.

    See also Thread Safety and Preemptive Callback to User Code.
    """

    status = libca.ca_pend_event(timeout)
    return status


def poll():
    """
    The send buffer is flushed and any outstanding CA background activity is processed.

    .. note:: same as pend_event(1e-12)

    """
    status = libca.ca_pend_event(1e-12)
    return


def pend_io(timeout):
    """
    This function flushes the send buffer and then blocks until outstanding get requests *without* callback complete,
    and until channels created *without* callback connect for the first time.

    :param timeout: Specifies the time out interval. A timeout interval of zero specifies forever.
    :return:
                - ECA_NORMAL - Normal successful completion
                - ECA_TIMEOUT - Selected IO requests didn't complete before specified timeout
                - ECA_EVDISALLOW - Function inappropriate for use within an event handler

    If ECA_NORMAL is returned then it can be safely assumed that all outstanding get requests *without* callback
    have completed successfully and channels created *without* callback have connected for the first time.

    If ECA_TIMEOUT is returned then it must be assumed for all previous get requests and
    properly qualified first time channel connects have failed.

    If ECA_TIMEOUT is returned then get requests may be reissued followed by a subsequent call to :func:`pend_io`.
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
    return status


def pend(timeout, early):
    """
    :param float timeout: Specifies the time out interval. A timeout interval of zero specifies forever.
    :param bool early: Call :func:`pend_io` if *early* is True otherwise :func:`pend_event` is called
    :return:
                - ECA_NORMAL - Normal successful completion
                - ECA_TIMEOUT - Selected IO requests didn't complete before specified timeout
                - ECA_EVDISALLOW - Function inappropriate for use within an event handler

    """
    return libca.ca_pend(timeout, early)


def test_io():
    """
    This function tests to see if all get requests are complete and channels created without a connection callback function
    are connected. It will report the status of outstanding get requests issued, and channels created without connection callback function,
    after the last call to ca_pend_io() or CA context initialization whichever is later.

    :return:
                - ECA_IODONE - All IO operations completed
                - ECA_IOINPROGRESS - IO operations still in progress

    """
    status = (libca.test_io() == 1)
    return status


def flush_io():
    """
    Flush outstanding IO requests to the server.

    :return:
                - ECA_NORMAL - Normal successful completion

    This routine might be useful to users who need to flush requests prior to performing client side labor
    in parallel with labor performed in the server.
    Outstanding requests are also sent whenever the buffer which holds them becomes full.
    """
    status = libca.ca_flush_io()
    return status


def field_type(chid):
    """
    :param chid: channel identifier
    :return: the native type in the server of the process variable.
    """
    return libca.ca_field_type(chid)


def element_count(chid):
    """
    :param chid: channel identifier
    :return: the maximum array element count in the server for the specified IO channel.
    """
    return libca.ca_element_count(chid)


def name(chid):
    """
    :param chid: channel identifier
    :return: the name provided when the supplied channel id was created.
    """
    return ffi.string(libca.ca_name(chid))


def state(chid):
    """
    :param chid: channel identifier
    :return:
    """
    return libca.ca_state(chid)


def message(status):
    """
    :return: a message corresponding to a user specified CA status code.
    """
    return ffi.string(libca.ca_message(status))


def host_name(chid):
    """
    :param chid: channel identifier
    :return: the name of the host to which a channel is currently connected.
    """
    return ffi.string(libca.ca_host_name(chid))


def read_access(chid):
    """
    :param chid: channel identifier
    :return: True if the client currently has read access to the specified channel and False otherwise.
    """
    return libca.ca_read_access(chid)


def write_access(chid):
    """
    :param chid: channel identifier
    :return: True if the client currently has write access to the specified channel and False otherwise.
    """
    return libca.ca_write_access(chid)


def sg_create():
    """
    Create a synchronous group and return an identifier for it.

    :return: Synchronous group identifier

    A synchronous group can be used to guarantee that a set of channel access requests have completed.
    Once a synchronous group has been created then channel access get and put requests may be issued
    within it using :func:`sg_get` and :func:`sg_put` respectively.
    The routines :func:`sg_block` and :func:`sg_test` can be used to block for and test for completion respectively.
    The routine :func:`sg_reset` is used to discard knowledge of old requests which have timed out and
    in all likelihood will never be satisfied.

    Any number of asynchronous groups can have application requested operations outstanding within them at any given time.

    """
    pgid = ffi.new('CA_SYNC_GID *')
    status = libca.ca_sg_create(pgid)
    if status == ECA_NORMAL:
        gid = pgid[0]
    else:
        gid = None
    return gid


def sg_delete(gid):
    """
    Deletes a synchronous group.

    :param gid: Identifier of the synchronous group to be deleted.
    :return:
                - ECA_NORMAL - Normal successful completion
                - ECA_BADSYNCGRP - Invalid synchronous group
    """
    return libca.ca_sg_delete(gid)


def sg_block(gid, timeout):
    """
    Flushes the send buffer and then waits until outstanding requests complete or the specified time out expires.
    At this time outstanding requests include calls to :func:`sg_array_get` and calls to :func:`sg_array_put`.
    If ECA_TIMEOUT is returned then failure must be assumed for all outstanding queries.
    Operations can be reissued followed by another :func:`sg_block`.
    This routine will only block on outstanding queries issued after the last call to :func:`sg_block`,
    :func:`ca_sg_reset`, or :func:`sg_create` whichever occurs later in time.
    If no queries are outstanding then :func:`sg_block` will return immediately without processing any pending channel access activities.

    Values written into your program's variables by a channel access synchronous group request should not be
    referenced by your program until ECA_NORMAL has been received from :func:`sg_block`.
    This routine will process pending channel access background activity while it is waiting.

    :param gid: Identifier of the synchronous group.
    :param timeout: Specifies the time out interval. A timeout interval of zero specifies forever.
    :return:
                - ECA_NORMAL - Normal successful completion
                - ECA_TIMEOUT - The operation timed out
                - ECA_EVDISALLOW - Function inappropriate for use within an event handler
                - ECA_BADSYNCGRP - Invalid synchronous group
    """
    return libca.ca_sg_block(gid, timeout)


def sg_test(gid):
    """
    Test to see if all requests made within a synchronous group have completed.

    :param gid: Identifier of the synchronous group.
    :return: True if all IO operations are completed
    """
    return libca.ca_sg_test(gid) == ECA_IODONE


def sg_reset(gid):
    """
    Reset the number of outstanding requests within the specified synchronous group to zero so that
    :func:`sg_test` will return True and :func:`sg_block` will not block unless additional subsequent requests are made.

    :param gid: Identifier of the synchronous group.
    :return:
                - ECA_NORMAL - Normal successful completion
                - ECA_BADSYNCGRP - Invalid synchronous group
    """
    return libca.sg_reset(gid)


def sg_put(gid, chid, value, dbrtype=None, count=None):
    """
    Write a value, or array of values, to a channel and increment the outstanding request count of a synchronous group.

    :param gid: Synchronous group identifier
    :param chid: Channel identifier
    :param value: The value or array of values to write
    :param dbrtype: The type of supplied value. Conversion will occur if it does not match the native type.
                    Specify one from the set of DBR_XXXX in db_access.h.
    :param count: The element count to be written to the specified channel.
    :return:
                - ECA_NORMAL - Normal successful completion
                - ECA_BADSYNCGRP - Invalid synchronous group
                - ECA_BADCHID - Corrupted CHID
                - ECA_BADTYPE - Invalid DBR_XXXX type
                - ECA_BADCOUNT - Requested count larger than native element count
                - ECA_STRTOBIG - Unusually large string supplied
                - ECA_PUTFAIL - A local database put failed

    All remote operation requests such as the above are accumulated (buffered) and not forwarded to the server
    until one of :func:`flush_io`, :func:`pend_io` or :func:`pend_event` are called.
    This allows several requests to be efficiently sent in one message.

    If a connection is lost and then resumed outstanding puts are not reissued.
    """
    if dbrtype is None:
        dbrtype = libca.ca_field_type(chid)

    element_count = libca.ca_element_count(chid)
    if count is None or count < 0:
        count = element_count

    # treat single value and sequence differently to create c type value
    try:
        value_count = len(value)
    except TypeError:
        value_count = 1
    else:
        # string type is also a sequence but it is counted as one if DBR_STRING type
        if isinstance(value, basestring) and dbrtype == DBR_STRING:
            value_count = 1

   # setup c value
    if value_count == 1:
        cvalue = ffi.new(DBR_TYPE_STRING[dbrtype]+'*', value)
    else:
        cvalue = ffi.new(DBR_TYPE_STRING[dbrtype]+'[]', value)

    # the actual count requested is the minimum of all three
    count = min(count, element_count, value_count)

    status = libca.ca_sg_array_put(gid, dbrtype, count, chid, cvalue)

    return status

def sg_get(gid, chid, dbrtype=None, count=None):
    """
    Read a value from a channel and increment the outstanding request count of a synchronous group.

    :param gid: Identifier of the synchronous group.
    :param chid: Channel identifier
    :param dbrtype: External type of returned value. Conversion will occur if this does not match native type.
                    Specify one from the set of DBR_XXXX in db_access.h
    :param count: Element count to be read from the specified channel.
    :return: Pointer to application supplied buffer that is to contain the value or array of values to be returned


    The values written into your program's variables by :func:`sg_get` should not be referenced by your program
    until ECA_NORMAL has been received from ca_sg_block , or until :func:`sg_test` returns True.

    All remote operation requests such as the above are accumulated (buffered) and not forwarded to the server
    until one of :func:`flush_io`, :func:`pend_io`, or :func:`pend_event` are called.
    This allows several requests to be efficiently sent in one message.

    If a connection is lost and then resumed outstanding gets are not reissued.
    """
    if count is None or count < 0:
        count = libca.ca_element_count(chid)

    if dbrtype is None:
        dbrtype = libca.ca_field_type(chid)

    value = ffi.new('char[]', dbr_size_n(dbrtype, count))
    libca.ca_sg_array_get(gid, dbrtype, count, chid, value)
    return value
