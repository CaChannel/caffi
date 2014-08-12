"""
The macros defined in C header files, *cadef.h*, *caeventmask.h*, *caerr.h* are exported as IntEnum.

"""
from enum import IntEnum

__all__ = ['ChannelState', 'CA_OP', 'CA_PRIORITY',
           'CA_K', 'ECA', 'DBE',
           'AlarmSeverity', 'AlarmCondition', 'POSIX_TIME_AT_EPICS_EPOCH']

from ._ca import *
from .compat import to_string

class ChannelState(IntEnum):
    """
    Enum redefined from C enum channel_state
    """
    NEVER_CONN = libca.cs_never_conn
    PREV_CONN  = libca.cs_prev_conn
    CONN       = libca.cs_conn
    CLOSED     = libca.cs_closed


class CA_OP(IntEnum):
    """
    Enum redefined from C macros CA_OP_XXX
    """
    GET             = libca.CA_OP_GET
    PUT             = libca.CA_OP_PUT
    CREATE_CHANNEL  = libca.CA_OP_CREATE_CHANNEL
    ADD_EVENT       = libca.CA_OP_ADD_EVENT
    CLEAR_EVENT     = libca.CA_OP_CLEAR_EVENT
    OTHER           = libca.CA_OP_OTHER
    CONN_UP         = libca.CA_OP_CONN_UP
    CONN_DOWN       = libca.CA_OP_CONN_DOWN


class CA_PRIORITY(IntEnum):
    """
    Enum redefined from CA_PRIORITY_XXX macros.
    """
    MAX     = libca.CA_PRIORITY_MAX
    MIN     = libca.CA_PRIORITY_MIN
    DEFAULT = libca.CA_PRIORITY_DEFAULT

    DB_LINKS= libca.CA_PRIORITY_DB_LINKS
    ARCHIVE = libca.CA_PRIORITY_ARCHIVE
    OPI     = libca.CA_PRIORITY_OPI


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
    VALUE       = libca.DBE_VALUE
    ARCHIVE     = libca.DBE_ARCHIVE
    LOG         = libca.DBE_LOG
    ALARM       = libca.DBE_ALARM
    PROPERTY    = libca.DBE_PROPERTY


# caerr.h
#/*  CA Status Code Definitions   */

CA_K_INFO       = 3   #/* successful */
CA_K_ERROR      = 2   #/* failed- continue */
CA_K_SUCCESS    = 1   #/* successful */
CA_K_WARNING    = 0   #/* unsuccessful */
CA_K_SEVERE     = 4   #/* failed- quit */
CA_K_FATAL      = CA_K_ERROR | CA_K_SEVERE

CA_M_MSG_NO     = 0x0000FFF8
CA_M_SEVERITY   = 0x00000007
CA_M_LEVEL      = 0x00000003
CA_M_SUCCESS    = 0x00000001
CA_M_ERROR      = 0x00000002
CA_M_SEVERE     = 0x00000004

CA_V_MSG_NO     = 0x03
CA_V_SEVERITY   = 0x00
CA_V_SUCCESS    = 0x00


def CA_EXTRACT_MSG_NO(code):
    return (code & CA_M_MSG_NO) >> CA_V_MSG_NO


def CA_EXTRACT_MSG_SEVERITY(code):
    return (code & CA_M_SEVERITY) >> CA_V_SEVERITY


ECA_NORMAL          =   1
ECA_MAXIOC          =  10
ECA_UKNHOST         =  18
ECA_UKNSERV         =  26
ECA_SOCK            =  34
ECA_CONN            =  40
ECA_ALLOCMEM        =  48
ECA_UKNCHAN         =  56
ECA_UKFIELD         =  64
ECA_TOLARGE         =  72
ECA_TIMEOUT         =  80
ECA_NOSUPPORT       =  88
ECA_STRTOBIG        =  96
ECA_DISCONNCHID     = 106
ECA_BADTYPE         = 114
ECA_CHIDNOTFOUND    = 123
ECA_CHIDRETRY       = 131
ECA_INTERNAL        = 142
ECA_DBLCLFAIL       = 144
ECA_GETFAIL         = 152
ECA_PUTFAIL         = 160
ECA_ADDFAIL         = 168
ECA_BADCOUNT        = 176
ECA_BADSTR          = 186
ECA_DISCONN         = 192
ECA_DBLCHNL         = 200
ECA_EVDISALLOW      = 210
ECA_BUILDGET        = 216
ECA_NEEDSFP         = 224
ECA_OVEVFAIL        = 232
ECA_BADMONID        = 242
ECA_NEWADDR         = 248
ECA_NEWCONN         = 259
ECA_NOCACTX         = 264
ECA_DEFUNCT         = 278
ECA_EMPTYSTR        = 280
ECA_NOREPEATER      = 288
ECA_NOCHANMSG       = 296
ECA_DLCKREST        = 304
ECA_SERVBEHIND      = 312
ECA_NOCAST          = 320
ECA_BADMASK         = 330
ECA_IODONE          = 339
ECA_IOINPROGRESS    = 347
ECA_BADSYNCGRP      = 354
ECA_PUTCBINPROG     = 362
ECA_NORDACCESS      = 368
ECA_NOWTACCESS      = 376
ECA_ANACHRONISM     = 386
ECA_NOSEARCHADDR    = 392
ECA_NOCONVERT       = 400
ECA_BADCHID         = 410
ECA_BADFUNCPTR      = 418
ECA_ISATTACHED      = 424
ECA_UNAVAILINSERV   = 432
ECA_CHANDESTROY     = 440
ECA_BADPRIORITY     = 450
ECA_NOTTHREADED     = 458
ECA_16KARRAYCLIEN   = 464
ECA_CONNSEQTMO      = 472
ECA_UNRESPTMO       = 480


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


# epicsTime.h
#/* The EPICS Epoch is 00:00:00 Jan 1, 1990 UTC */
POSIX_TIME_AT_EPICS_EPOCH = 631152000


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
    No      =  libca.epicsSevNone
    Minor   =  libca.epicsSevMinor
    Major   =  libca.epicsSevMajor
    Invalid =  libca.epicsSevInvalid


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
    No        =  libca.epicsAlarmNone
    Read      =  libca.epicsAlarmRead
    Write     =  libca.epicsAlarmWrite
    HiHi      =  libca.epicsAlarmHiHi
    High      =  libca.epicsAlarmHigh
    LoLo      =  libca.epicsAlarmLoLo
    Low       =  libca.epicsAlarmLow
    State     =  libca.epicsAlarmState
    Cos       =  libca.epicsAlarmCos
    Comm      =  libca.epicsAlarmComm
    Timeout   =  libca.epicsAlarmTimeout
    HwLimit   =  libca.epicsAlarmHwLimit
    Calc      =  libca.epicsAlarmCalc
    Scan      =  libca.epicsAlarmScan
    Link      =  libca.epicsAlarmLink
    Soft      =  libca.epicsAlarmSoft
    BadSub    =  libca.epicsAlarmBadSub
    UDF       =  libca.epicsAlarmUDF
    Disable   =  libca.epicsAlarmDisable
    Simm      =  libca.epicsAlarmSimm
    ReadAccess=  libca.epicsAlarmReadAccess
    WriteAccess= libca.epicsAlarmWriteAccess
