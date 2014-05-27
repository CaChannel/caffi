"""
The macros defined in C header files, *cadef.h*, *caeventmask.h*, *caerr.h* are exported as integer constants.

"""
from enum import IntEnum

# cadef.h

cs_never_conn = 0
cs_prev_conn  = 1
cs_conn       = 2
cs_closed     = 3

class ChannelState(IntEnum):
    """
    Enum redefined from C enum channel_state
    """
    NEVER_CONN = cs_never_conn
    PREV_CONN  = cs_prev_conn
    CONN       = cs_conn
    CLOSED     = cs_closed


#/*
# *  External OP codes for CA operations
# */
CA_OP_GET             = 0
CA_OP_PUT             = 1
CA_OP_CREATE_CHANNEL  = 2
CA_OP_ADD_EVENT       = 3
CA_OP_CLEAR_EVENT     = 4
CA_OP_OTHER           = 5

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


#/*
# * used with connection_handler_args
# */
CA_OP_CONN_UP    =   6
CA_OP_CONN_DOWN  =   7

TYPENOTCONN = -1 #/* the channel's native type when disconnected   */

CA_PRIORITY_MAX     = 99
CA_PRIORITY_MIN     = 0
CA_PRIORITY_DEFAULT = CA_PRIORITY_MIN

CA_PRIORITY_DB_LINKS= 80
CA_PRIORITY_ARCHIVE = 20
CA_PRIORITY_OPI     = 0

# caeventmask.h
"""
    event selections
    (If any more than 8 of these are needed then update the
    select field in the event_block struct in db_event.c from
    unsigned char to unsigned short)


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


DBE_VALUE       = (1<<0)
DBE_ARCHIVE     = (1<<1)
DBE_LOG         = DBE_ARCHIVE
DBE_ALARM       = (1<<2)
DBE_PROPERTY    = (1<<3)


# caerr.h
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


# db_access.h
# /* database field types */
DBF_STRING  = 0
DBF_INT     = 1
DBF_SHORT   = 1
DBF_FLOAT   = 2
DBF_ENUM    = 3
DBF_CHAR    = 4
DBF_LONG    = 5
DBF_DOUBLE  = 6
DBF_NO_ACCESS=7
LAST_TYPE   = DBF_DOUBLE


# /* data request buffer types */
DBR_STRING      = DBF_STRING
DBR_INT	        = DBF_INT
DBR_SHORT       = DBF_INT
DBR_FLOAT       = DBF_FLOAT
DBR_ENUM        = DBF_ENUM
DBR_CHAR        = DBF_CHAR
DBR_LONG        = DBF_LONG
DBR_DOUBLE      = DBF_DOUBLE
DBR_STS_STRING  = 7
DBR_STS_SHORT   = 8
DBR_STS_INT     = DBR_STS_SHORT
DBR_STS_FLOAT   = 9
DBR_STS_ENUM    = 10
DBR_STS_CHAR    = 11
DBR_STS_LONG    = 12
DBR_STS_DOUBLE  = 13
DBR_TIME_STRING = 14
DBR_TIME_INT    = 15
DBR_TIME_SHORT  = 15
DBR_TIME_FLOAT  = 16
DBR_TIME_ENUM   = 17
DBR_TIME_CHAR   = 18
DBR_TIME_LONG   = 19
DBR_TIME_DOUBLE = 20
DBR_GR_STRING   = 21
DBR_GR_SHORT    = 22
DBR_GR_INT      = DBR_GR_SHORT
DBR_GR_FLOAT    = 23
DBR_GR_ENUM     = 24
DBR_GR_CHAR     = 25
DBR_GR_LONG     = 26
DBR_GR_DOUBLE   = 27
DBR_CTRL_STRING = 28
DBR_CTRL_SHORT  = 29
DBR_CTRL_INT    = DBR_CTRL_SHORT
DBR_CTRL_FLOAT  = 30
DBR_CTRL_ENUM   = 31
DBR_CTRL_CHAR   = 32
DBR_CTRL_LONG   = 33
DBR_CTRL_DOUBLE = 34
DBR_PUT_ACKT    = DBR_CTRL_DOUBLE + 1
DBR_PUT_ACKS    = DBR_PUT_ACKT + 1
DBR_STSACK_STRING=DBR_PUT_ACKS + 1
DBR_CLASS_NAME  = DBR_STSACK_STRING + 1
LAST_BUFFER_TYPE= DBR_CLASS_NAME

#/*
# * type checking macros -- return non-zero if condition is true, zero otherwise
# */
def dbf_type_is_valid(dbftype):
    return dbftype >= 0 and dbftype <= LAST_TYPE


def dbr_type_is_valid(dbrtype):
    return dbrtype >= 0 and dbrtype <= LAST_BUFFER_TYPE


def dbr_type_is_plain(dbrtype):
    return dbrtype >= DBR_STRING and dbrtype <= DBR_DOUBLE


def dbr_type_is_STS(dbrtype):
    return dbrtype >= DBR_STS_STRING and dbrtype <= DBR_STS_DOUBLE


def dbr_type_is_TIME(dbrtype):
    return dbrtype >= DBR_TIME_STRING and dbrtype <= DBR_TIME_DOUBLE


def dbr_type_is_GR(dbrtype):
    return dbrtype >= DBR_GR_STRING and dbrtype <= DBR_GR_DOUBLE


def dbr_type_is_CTRL(dbrtype):
    return dbrtype >= DBR_CTRL_STRING and dbrtype <= DBR_CTRL_DOUBLE


def dbr_type_is_STRING(dbrtype):
    return ( dbr_type_is_valid(dbrtype) and
             dbrtype % (LAST_TYPE + 1) == DBR_STRING )


def dbr_type_is_SHORT(dbrtype):
    return ( dbr_type_is_valid(dbrtype) and
             dbrtype % (LAST_TYPE + 1) == DBR_SHORT )


def dbr_type_is_FLOAT(dbrtype):
    return ( dbr_type_is_valid(dbrtype) and
             dbrtype % (LAST_TYPE + 1) == DBR_FLOAT )

def dbr_type_is_ENUM(dbrtype):
    return ( dbr_type_is_valid(dbrtype) and
             dbrtype % (LAST_TYPE + 1) == DBR_ENUM )


def dbr_type_is_CHAR(dbrtype):
    return ( dbr_type_is_valid(dbrtype) and
             dbrtype % (LAST_TYPE + 1) == DBR_CHAR )


def dbr_type_is_LONG(dbrtype):
    return ( dbr_type_is_valid(dbrtype) and
             dbrtype % (LAST_TYPE + 1) == DBR_LONG )


def dbr_type_is_DOUBLE(dbrtype):
    return ( dbr_type_is_valid(dbrtype) and
             dbrtype % (LAST_TYPE + 1) == DBR_DOUBLE )


#/*
# * type conversion macros
# */
def dbf_type_to_DBR(dbftype):
    if dbf_type_is_valid(dbftype):
        return dbftype
    else:
        return -1


def dbf_type_to_DBR_STS(dbftype):
    if dbf_type_is_valid(dbftype):
        return dbftype + LAST_TYPE + 1
    else:
        return -1


def dbf_type_to_DBR_TIME(dbftype):
    if dbf_type_is_valid(dbftype):
        return dbftype + 2 * (LAST_TYPE + 1)
    else:
        return -1


def dbf_type_to_DBR_GR(dbftype):
    if dbf_type_is_valid(dbftype):
        return dbftype + 3 * (LAST_TYPE + 1)
    else:
        return -1


def dbf_type_to_DBR_CTRL(dbftype):
    if dbf_type_is_valid(dbftype):
        return dbftype + 4 * (LAST_TYPE + 1)
    else:
        return -1


class DBR(IntEnum):
    """
    Enum redefined from DBR_XXX macros.
    """
    INVALID     = TYPENOTCONN
    STRING      = DBR_STRING
    INT         = DBR_INT
    SHORT       = DBR_SHORT
    FLOAT       = DBR_FLOAT
    ENUM        = DBR_ENUM
    CHAR        = DBR_CHAR
    LONG        = DBR_LONG
    DOUBLE      = DBR_DOUBLE
    STS_STRING  = DBR_STS_STRING
    STS_SHORT   = DBR_STS_SHORT
    STS_INT     = DBR_STS_INT
    STS_FLOAT   = DBR_STS_FLOAT
    STS_ENUM    = DBR_STS_ENUM
    STS_CHAR    = DBR_STS_CHAR
    STS_LONG    = DBR_STS_LONG
    STS_DOUBLE  = DBR_STS_DOUBLE
    TIME_STRING = DBR_TIME_STRING
    TIME_INT    = DBR_TIME_INT
    TIME_SHORT  = DBR_TIME_SHORT
    TIME_FLOAT  = DBR_TIME_FLOAT
    TIME_ENUM   = DBR_TIME_ENUM
    TIME_CHAR   = DBR_TIME_CHAR
    TIME_LONG   = DBR_TIME_LONG
    TIME_DOUBLE = DBR_TIME_DOUBLE
    GR_STRING   = DBR_GR_STRING
    GR_SHORT    = DBR_GR_SHORT
    GR_INT      = DBR_GR_INT
    GR_FLOAT    = DBR_GR_FLOAT
    GR_ENUM     = DBR_GR_ENUM
    GR_CHAR     = DBR_GR_CHAR
    GR_LONG     = DBR_GR_LONG
    GR_DOUBLE   = DBR_GR_DOUBLE
    CTRL_STRING = DBR_CTRL_STRING
    CTRL_SHORT  = DBR_CTRL_SHORT
    CTRL_INT    = DBR_CTRL_INT
    CTRL_FLOAT  = DBR_CTRL_FLOAT
    CTRL_ENUM   = DBR_CTRL_ENUM
    CTRL_CHAR   = DBR_CTRL_CHAR
    CTRL_LONG   = DBR_CTRL_LONG
    CTRL_DOUBLE = DBR_CTRL_DOUBLE
    PUT_ACKT    = DBR_PUT_ACKT
    PUT_ACKS    = DBR_PUT_ACKS
    STSACK_STRING=DBR_STSACK_STRING
    CLASS_NAME  = DBR_CLASS_NAME

    def isSTRING(self):
        return dbr_type_is_STRING(self.value)

    def isSHORT(self):
        return dbr_type_is_SHORT(self.value)

    def isFLOAT(self):
        return dbr_type_is_FLOAT(self.value)

    def isENUM(self):
        return dbr_type_is_ENUM(self.value)

    def isCHAR(self):
        return dbr_type_is_CHAR(self.value)

    def isLONG(self):
        return dbr_type_is_LONG(self.value)

    def isDOUBLE(self):
        return dbr_type_is_DOUBLE(self.value)

    def isPlain(self):
        return dbr_type_is_plain(self.value)

    def isSTS(self):
        return dbr_type_is_STS(self.value)

    def isTIME(self):
        return dbr_type_is_TIME(self.value)

    def isGR(self):
        return dbr_type_is_GR(self.value)

    def isCTRL(self):
        return dbr_type_is_CTRL(self.value)


class DBF(IntEnum):
    """
    Enum redefined from DBF_XXX macros.
    """
    INVALID = TYPENOTCONN
    STRING  = DBF_STRING
    INT     = DBF_INT
    SHORT   = DBF_SHORT
    FLOAT   = DBF_FLOAT
    ENUM    = DBF_ENUM
    CHAR    = DBF_CHAR
    LONG    = DBF_LONG
    DOUBLE  = DBF_DOUBLE

    def toSTS(self):
        return DBR(dbf_type_to_DBR_STS(self.value))

    def toTIME(self):
        return DBR(dbf_type_to_DBR_TIME(self.value))

    def toGR(self):
        return DBR(dbf_type_to_DBR_GR(self.value))

    def toCTRL(self):
        return DBR(dbf_type_to_DBR_GR(self.value))


# epicsTime.h
#/* The EPICS Epoch is 00:00:00 Jan 1, 1990 UTC */
POSIX_TIME_AT_EPICS_EPOCH = 631152000


# alarm.h

#/* ALARM SEVERITIES - must match menuAlarmSevr.dbd */

NO_ALARM     = 0
MINOR_ALARM  = 1
MAJOR_ALARM  = 2
INVALID_ALARM= 3

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


#NO_ALARM         =  0
READ_ALARM       =  1
WRITE_ALARM      =  2
HIHI_ALARM       =  3
HIGH_ALARM       =  4
LOLO_ALARM       =  5
LOW_ALARM        =  6
STATE_ALARM      =  7
COS_ALARM        =  8
COMM_ALARM       =  9
TIMEOUT_ALARM    = 10
HW_LIMIT_ALARM   = 11
CALC_ALARM       = 12
SCAN_ALARM       = 13
LINK_ALARM       = 14
SOFT_ALARM       = 15
BAD_SUB_ALARM    = 16
UDF_ALARM        = 17
DISABLE_ALARM    = 18
SIMM_ALARM       = 19
READ_ACCESS_ALARM= 20
WRITE_ACCESS_ALARM=21


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
    No        =  NO_ALARM
    Read      =  READ_ALARM
    Write     =  WRITE_ALARM
    HiHi      =  HIHI_ALARM
    High      =  HIGH_ALARM
    LoLo      =  LOLO_ALARM
    Low       =  LOW_ALARM
    State     =  STATE_ALARM
    Cos       =  COS_ALARM
    Comm      =  COMM_ALARM
    Timeout   =  TIMEOUT_ALARM
    HwLimit   =  HW_LIMIT_ALARM
    Calc      =  CALC_ALARM
    Scan      =  SCAN_ALARM
    Link      =  LINK_ALARM
    Soft      =  SOFT_ALARM
    BadSub    =  BAD_SUB_ALARM
    UDF       =  UDF_ALARM
    Disable   =  DISABLE_ALARM
    Simm      =  SIMM_ALARM
    ReadAccess=  READ_ACCESS_ALARM
    WriteAccess= WRITE_ACCESS_ALARM
