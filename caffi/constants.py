"""
The macros defined macros.py are exported as IntEnum.

"""
from enum import IntEnum

__all__ = ['ChannelState', 'CA_OP', 'CA_PRIORITY',
           'CA_K', 'ECA', 'DBE',
           'AlarmSeverity', 'AlarmCondition']

from .compat import to_string
from .macros import *

class ChannelState(IntEnum):
    """
    Enum redefined from C enum channel_state
    """
    NEVER_CONN = cs_never_conn
    PREV_CONN  = cs_prev_conn
    CONN       = cs_conn
    CLOSED     = cs_closed


class CA_OP(IntEnum):
    """
    Enum redefined from C macros CA_OP_XXX
    """
    GET             = CA_OP_GET
    PUT             = CA_OP_PUT
    CREATE_CHANNEL  = CA_OP_CREATE_CHANNEL
    ADD_EVENT       = CA_OP_ADD_EVENT
    CLEAR_EVENT     = CA_OP_CLEAR_EVENT
    OTHER           = CA_OP_OTHER
    CONN_UP         = CA_OP_CONN_UP
    CONN_DOWN       = CA_OP_CONN_DOWN


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

    DBE_VALUE
    Trigger an event when a significant change in the channel's value
    occurs. Relies on the monitor deadband field under DCT.

    DBE_ARCHIVE (DBE_LOG)
    Trigger an event when an archive significant change in the channel's
    valuue occurs. Relies on the archiver monitor deadband field under DCT.

    DBE_ALARM
    Trigger an event when the alarm state changes

    DBE_PROPERTY
    Trigger an event when a property change (control limit, graphical
    limit, status string, enum string ...) occurs.
    """
    VALUE       = DBE_VALUE
    ARCHIVE     = DBE_ARCHIVE
    LOG         = DBE_LOG
    ALARM       = DBE_ALARM
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
    """
    NORMAL          = ECA_NORMAL
    MAXIOC          = ECA_MAXIOC
    UKNHOST         = ECA_UKNHOST
    UKNSERV         = ECA_UKNSERV
    SOCK            = ECA_SOCK
    CONN            = ECA_CONN
    ALLOCMEM        = ECA_ALLOCMEM
    UKNCHAN         = ECA_UKNCHAN
    UKFIELD         = ECA_UKFIELD
    TOLARGE         = ECA_TOLARGE
    TIMEOUT         = ECA_TIMEOUT
    NOSUPPORT       = ECA_NOSUPPORT
    STRTOBIG        = ECA_STRTOBIG
    DISCONNCHID     = ECA_DISCONNCHID
    BADTYPE         = ECA_BADTYPE
    CHIDNOTFOUND    = ECA_CHIDNOTFOUND
    CHIDRETRY       = ECA_CHIDRETRY
    INTERNAL        = ECA_INTERNAL
    DBLCLFAIL       = ECA_DBLCLFAIL
    GETFAIL         = ECA_GETFAIL
    PUTFAIL         = ECA_PUTFAIL
    ADDFAIL         = ECA_ADDFAIL
    BADCOUNT        = ECA_BADCOUNT
    BADSTR          = ECA_BADSTR
    DISCONN         = ECA_DISCONN
    DBLCHNL         = ECA_DBLCHNL
    EVDISALLOW      = ECA_EVDISALLOW
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
    IODONE          = ECA_IODONE
    IOINPROGRESS    = ECA_IOINPROGRESS
    BADSYNCGRP      = ECA_BADSYNCGRP
    PUTCBINPROG     = ECA_PUTCBINPROG
    NORDACCESS      = ECA_NORDACCESS
    NOWTACCESS      = ECA_NOWTACCESS
    ANACHRONISM     = ECA_ANACHRONISM
    NOSEARCHADDR    = ECA_NOSEARCHADDR
    NOCONVERT       = ECA_NOCONVERT
    BADCHID         = ECA_BADCHID
    BADFUNCPTR      = ECA_BADFUNCPTR
    ISATTACHED      = ECA_ISATTACHED
    UNAVAILINSERV   = ECA_UNAVAILINSERV
    CHANDESTROY     = ECA_CHANDESTROY
    BADPRIORITY     = ECA_BADPRIORITY
    NOTTHREADED     = ECA_NOTTHREADED
    # 16KARRAYCLIEN is an invalid variable name
    ARRAYCLIEN      = ECA_16KARRAYCLIEN
    CONNSEQTMO      = ECA_CONNSEQTMO
    UNRESPTMO       = ECA_UNRESPTMO

    def severity(self):
        """
        Return the severity of the status code
        """
        return CA_K(CA_EXTRACT_MSG_SEVERITY(self.value))

    def message(self):
        """
        Return the string representation of the status code
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

    """
    # None is Python keyword
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
