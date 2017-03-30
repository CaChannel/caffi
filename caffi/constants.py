"""
The macros defined macros.py are exported as IntEnum.

"""
from enum import IntEnum
from .ca import ffi, libca
from .compat import to_string
from .macros import *

__all__ = ['ChannelState', 'CA_OP', 'CA_PRIORITY',
           'CA_K', 'ECA', 'DBE',
           'AlarmSeverity', 'AlarmCondition']


class ChannelState(IntEnum):
    """
    Enum redefined from C enum channel_state
    """
    NEVER_CONN  = cs_never_conn #: valid chid, IOC not found
    PREV_CONN   = cs_prev_conn #: valid chid, IOC was found, but unavailable
    CONN        = cs_conn #: valid chid, IOC was found, still available
    CLOSED      = cs_closed #: channel deleted
    NEVER_SEARCH= cs_never_search #: invalid chid


class CA_OP(IntEnum):
    """
    Enum redefined from C macros CA_OP_XXX
    """
    GET             = CA_OP_GET #: get value
    PUT             = CA_OP_PUT #: put value
    CREATE_CHANNEL  = CA_OP_CREATE_CHANNEL #: create channel
    ADD_EVENT       = CA_OP_ADD_EVENT #: subscribe
    CLEAR_EVENT     = CA_OP_CLEAR_EVENT #: unsubscribe
    OTHER           = CA_OP_OTHER #: other
    CONN_UP         = CA_OP_CONN_UP #: connection established
    CONN_DOWN       = CA_OP_CONN_DOWN #: connection lost


class CA_PRIORITY(IntEnum):
    """
    Enum redefined from CA_PRIORITY_XXX macros.
    """
    MAX     = CA_PRIORITY_MAX
    MIN     = CA_PRIORITY_MIN
    DEFAULT = CA_PRIORITY_DEFAULT

    DB_LINKS= CA_PRIORITY_DB_LINKS
    ARCHIVE = CA_PRIORITY_ARCHIVE
    OPI     = CA_PRIORITY_OPI


class DBE(IntEnum):
    """
    Enum redefined from DBE_XXX macros.
    """
    #: Trigger an event when a significant change in the channel's value
    #: occurs. Relies on the monitor deadband field under DCT.
    VALUE       = DBE_VALUE

    #: Trigger an event when an archive significant change in the channel's
    #: value occurs. Relies on the archiver monitor deadband field under DCT.
    ARCHIVE     = DBE_ARCHIVE

    #: Trigger an event when the alarm state changes
    ALARM       = DBE_ALARM

    #: Trigger an event when a property change (control limit, graphical
    #: limit, status string, enum string ...) occurs.
    PROPERTY    = DBE_PROPERTY


class CA_K(IntEnum):
    """
    Enum redefined from CA_K_XXX
    """
    INFO    = CA_K_INFO
    ERROR   = CA_K_ERROR
    SUCCESS = CA_K_SUCCESS
    WARNING = CA_K_WARNING
    SEVERE  = CA_K_SEVERE
    FATAL   = CA_K_FATAL


class ECA(IntEnum):
    """
    Enum redefined from ECA_XXX status code

    .. note:: ARRAY16KCLIENT is used in place of ECA_16KARRAYCLIENT, while variable
       name cannot start with a number.
    """
    NORMAL          = ECA_NORMAL #: Normal successful completion
    MAXIOC          = ECA_MAXIOC
    UKNHOST         = ECA_UKNHOST
    UKNSERV         = ECA_UKNSERV
    SOCK            = ECA_SOCK
    CONN            = ECA_CONN
    ALLOCMEM        = ECA_ALLOCMEM #: Unable to allocate additional dynamic memory
    UKNCHAN         = ECA_UKNCHAN
    UKNFIELD        = ECA_UKNFIELD
    TOLARGE         = ECA_TOLARGE #: The requested data transfer is greater than available memory or EPICS_CA_MAX_ARRAY_BYTES
    TIMEOUT         = ECA_TIMEOUT #: User specified timeout on IO operation expired
    NOSUPPORT       = ECA_NOSUPPORT
    STRTOBIG        = ECA_STRTOBIG #: The supplied string is unusually large
    DISCONNCHID     = ECA_DISCONNCHID #: The request was ignored because the specified channel is disconnected
    BADTYPE         = ECA_BADTYPE #: The data type specified is invalid
    CHIDNOTFOUND    = ECA_CHIDNOTFOUND
    CHIDRETRY       = ECA_CHIDRETRY
    INTERNAL        = ECA_INTERNAL
    DBLCLFAIL       = ECA_DBLCLFAIL
    GETFAIL         = ECA_GETFAIL #: Channel read request failed
    PUTFAIL         = ECA_PUTFAIL #: Channel write request failed
    ADDFAIL         = ECA_ADDFAIL #: Channel subscription request failed
    BADCOUNT        = ECA_BADCOUNT #: Invalid element count requested
    BADSTR          = ECA_BADSTR #: Invalid string
    DISCONN         = ECA_DISCONN #: Virtual circuit disconnect
    DBLCHNL         = ECA_DBLCHNL #: Identical process variable names on multiple servers
    EVDISALLOW      = ECA_EVDISALLOW #: Request inappropriate within subscription (monitor) update callback
    BUILDGET        = ECA_BUILDGET
    NEEDSFP         = ECA_NEEDSFP
    OVEVFAIL        = ECA_OVEVFAIL
    BADMONID        = ECA_BADMONID
    NEWADDR         = ECA_NEWADDR
    NEWCONN         = ECA_NEWCONN
    NOCACTX         = ECA_NOCACTX
    DEFUNCT         = ECA_DEFUNCT
    EMPTYSTR        = ECA_EMPTYSTR
    NOREPEATER      = ECA_NOREPEATER
    NOCHANMSG       = ECA_NOCHANMSG
    DLCKREST        = ECA_DLCKREST
    SERVBEHIND      = ECA_SERVBEHIND
    NOCAST          = ECA_NOCAST
    BADMASK         = ECA_BADMASK
    IODONE          = ECA_IODONE #: IO operations have completed
    IOINPROGRESS    = ECA_IOINPROGRESS #: IO operations are in progress
    BADSYNCGRP      = ECA_BADSYNCGRP #: Invalid synchronous group identifier
    PUTCBINPROG     = ECA_PUTCBINPROG
    NORDACCESS      = ECA_NORDACCESS
    NOWTACCESS      = ECA_NOWTACCESS #: Channel write request failed
    ANACHRONISM     = ECA_ANACHRONISM
    NOSEARCHADDR    = ECA_NOSEARCHADDR
    NOCONVERT       = ECA_NOCONVERT
    BADCHID         = ECA_BADCHID #: Invalid channel identifier
    BADFUNCPTR      = ECA_BADFUNCPTR
    ISATTACHED      = ECA_ISATTACHED #: Thread is already attached to a client context
    UNAVAILINSERV   = ECA_UNAVAILINSERV #: Not supported by attached service
    CHANDESTROY     = ECA_CHANDESTROY
    BADPRIORITY     = ECA_BADPRIORITY #: Invalid channel priority
    NOTTHREADED     = ECA_NOTTHREADED #: Preemptive callback not enabled - additional threads may not join context
    # 16KARRAYCLIENT is an invalid variable name
    ARRAY16KCLIENT  = ECA_16KARRAYCLIENT
    CONNSEQTMO      = ECA_CONNSEQTMO
    UNRESPTMO       = ECA_UNRESPTMO

    def severity(self):
        """
        :return: the severity of the status code
        :rtype: :class:`CA_K`
        """
        return CA_K(CA_EXTRACT_MSG_SEVERITY(self.value))

    def message(self):
        """
        :return: the string representation of the status code
        """
        return to_string(ffi.string(libca.ca_message(self.value)))


class AlarmSeverity(IntEnum):
    """
    Enum redefined from C enum type epicsAlarmSeverity.
    Due to the enum difference between C and Python,
    the enum item name has been greatly simplified::

        epicsSevNone  -> AlarmSeverity.No
        epicsSevMinor -> AlarmSeverity.Minor
        ...

    .. note:: *No* is used in place of *None*, which is Python keyword.
    """
    # None is a Python keyword
    No      =  NO_ALARM
    Minor   =  MINOR_ALARM
    Major   =  MAJOR_ALARM
    Invalid =  INVALID_ALARM


class AlarmCondition(IntEnum):
    """
    Enum redefined from C enum type epicsAlarmCondition.
    Due to the enum difference between C and Python,
    the enum item name has been greatly simplified::

        epicsAlarmNone -> AlarmCondition.No
        epicsAlarmRead -> AlarmCondition.Read
        ...

    .. note:: *No* is used in place of *None*, which is Python keyword.
    """
    No         = NO_ALARM
    Read       = READ_ALARM
    Write      = WRITE_ALARM
    HiHi       = HIHI_ALARM
    High       = HIGH_ALARM
    LoLo       = LOLO_ALARM
    Low        = LOW_ALARM
    State      = STATE_ALARM
    Cos        = COS_ALARM
    Comm       = COMM_ALARM
    Timeout    = TIMEOUT_ALARM
    HwLimit    = HW_LIMIT_ALARM
    Calc       = CALC_ALARM
    Scan       = SCAN_ALARM
    Link       = LINK_ALARM
    Soft       = SOFT_ALARM
    BadSub     = BAD_SUB_ALARM
    UDF        = UDF_ALARM
    Disable    = DISABLE_ALARM
    Simm       = SIMM_ALARM
    ReadAccess = READ_ACCESS_ALARM
    WriteAccess=WRITE_ACCESS_ALARM
