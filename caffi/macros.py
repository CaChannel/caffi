"""
The macros defined in C header files, *cadef.h*, *caeventmask.h*, *caerr.h*

"""
from ._ca import libca, ffi
from .compat import to_string, to_bytes

cs_never_conn = libca.cs_never_conn
cs_prev_conn = libca.cs_prev_conn
cs_conn = libca.cs_conn
cs_closed = libca.cs_closed

CA_OP_GET = libca.CA_OP_GET
CA_OP_PUT = libca.CA_OP_PUT
CA_OP_CREATE_CHANNEL = libca.CA_OP_CREATE_CHANNEL
CA_OP_ADD_EVENT = libca.CA_OP_ADD_EVENT
CA_OP_CLEAR_EVENT = libca.CA_OP_CLEAR_EVENT
CA_OP_OTHER = libca.CA_OP_OTHER
CA_OP_CONN_UP = libca.CA_OP_CONN_UP
CA_OP_CONN_DOWN = libca.CA_OP_CONN_DOWN

CA_PRIORITY_MAX = libca.CA_PRIORITY_MAX
CA_PRIORITY_MIN = libca.CA_PRIORITY_MIN
CA_PRIORITY_DEFAULT = libca.CA_PRIORITY_DEFAULT

CA_PRIORITY_DB_LINKS = libca.CA_PRIORITY_DB_LINKS
CA_PRIORITY_ARCHIVE = libca.CA_PRIORITY_ARCHIVE
CA_PRIORITY_OPI = libca.CA_PRIORITY_OPI

DBE_VALUE = libca.DBE_VALUE
DBE_ARCHIVE = libca.DBE_ARCHIVE
DBE_LOG = libca.DBE_LOG
DBE_ALARM = libca.DBE_ALARM
DBE_PROPERTY = libca.DBE_PROPERTY

# db_access.h
TYPENOTCONN = -1 #/* the channel's native type when disconnected   */

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
# * DBR structure size in bytes
# */
def dbr_size_n(TYPE,COUNT):
    if COUNT <=0:
        return libca.dbr_size[TYPE]
    else:
        return libca.dbr_size[TYPE] + (COUNT-1) * libca.dbr_value_size[TYPE]

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

#/*
# * type conversion macros
# */
def dbf_type_to_text(dbftype):
    if dbftype >= -1 and dbftype <= LAST_TYPE + 1:
        text = ffi.string(libca.dbf_text[dbftype + 1])
    else:
        text = ffi.string(libca.dbf_text_invalid)

    return to_string(text)
# alias
dbf_text = dbf_type_to_text

def dbf_text_to_type(text):
    for dbftype in range(0, LAST_TYPE + 2):
        if to_bytes(text) == ffi.string(libca.dbf_text[dbftype+1]):
            break
    else:
        dbftype = -1

    return dbftype

def dbr_type_to_text(dbrtype):
    if dbrtype >= 0 and dbrtype <= LAST_BUFFER_TYPE:
        text = ffi.string(libca.dbr_text[dbrtype])
    else:
        text = ffi.string(libca.dbr_text_invalid)

    return to_string(text)
# alias
dbr_text = dbr_type_to_text

def dbr_text_to_type(text):
    for dbrtype in range(0, LAST_BUFFER_TYPE + 1):
        if to_bytes(text) == ffi.string(libca.dbr_text[dbrtype]):
            break
    else:
        dbrtype = -1
    return dbrtype

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


# epicsTime.h
#/* The EPICS Epoch is 00:00:00 Jan 1, 1990 UTC */
POSIX_TIME_AT_EPICS_EPOCH = 631152000

# alarm.h
NO_ALARM = libca.epicsSevNone
MINOR_ALARM = libca.epicsSevMinor
MAJOR_ALARM = libca.epicsSevMajor
INVALID_ALARM = libca.epicsSevInvalid

READ_ALARM = libca.epicsAlarmRead
WRITE_ALARM = libca.epicsAlarmWrite
HIHI_ALARM = libca.epicsAlarmHiHi
HIGH_ALARM = libca.epicsAlarmHigh
LOLO_ALARM = libca.epicsAlarmLoLo
LOW_ALARM  = libca.epicsAlarmLow
STATE_ALARM = libca.epicsAlarmState
COS_ALARM = libca.epicsAlarmCos
COMM_ALARM = libca.epicsAlarmComm
TIMEOUT_ALARM = libca.epicsAlarmTimeout
HW_LIMIT_ALARM = libca.epicsAlarmHwLimit
CALC_ALARM = libca.epicsAlarmCalc
SCAN_ALARM = libca.epicsAlarmScan
LINK_ALARM = libca.epicsAlarmLink
SOFT_ALARM  = libca.epicsAlarmSoft
BAD_SUB_ALARM = libca.epicsAlarmBadSub
UDF_ALARM = libca.epicsAlarmUDF
DISABLE_ALARM = libca.epicsAlarmDisable
SIMM_ALARM = libca.epicsAlarmSimm
READ_ACCESS_ALARM = libca.epicsAlarmReadAccess
WRITE_ACCESS_ALARM = libca.epicsAlarmWriteAccess

def epicsAlarmSeverityStrings(severity):
    return ["NO_ALARM",
            "MINOR",
            "MAJOR",
            "INVALID"][severity]

alarmSeverityString = epicsAlarmSeverityStrings

def epicsAlarmConditionStrings(status):
    return ["NO_ALARM",
            "READ",
            "WRITE",
            "HIHI",
            "HIGH",
            "LOLO",
            "LOW",
            "STATE",
            "COS",
            "COMM",
            "TIMEOUT",
            "HWLIMIT",
            "CALC",
            "SCAN",
            "LINK",
            "SOFT",
            "BAD_SUB",
            "UDF",
            "DISABLE",
            "SIMM",
            "READ_ACCESS",
            "WRITE_ACCESS"][status]

alarmStatusString = epicsAlarmConditionStrings