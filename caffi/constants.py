
# cadef.h
#/*
# *  External OP codes for CA operations
# */
CA_OP_GET             = 0
CA_OP_PUT             = 1
CA_OP_CREATE_CHANNEL  = 2
CA_OP_ADD_EVENT       = 3
CA_OP_CLEAR_EVENT     = 4
CA_OP_OTHER           = 5

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
ECA_TIMEOUT         =  80
ECA_IODONE          = 339
ECA_IOINPROGRESS    = 347
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

#/* The EPICS Epoch is 00:00:00 Jan 1, 1990 UTC */
POSIX_TIME_AT_EPICS_EPOCH = 631152000
