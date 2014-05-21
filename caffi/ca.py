from __future__ import (print_function, absolute_import)

from datetime import datetime

try:
    import numpy
    ctype2dtype = {
        'dbr_int_t'    : numpy.int16,
        'dbr_float_t'  : numpy.float32,
        'dbr_char_t'   : numpy.uint8,
        'dbr_enum_t'   : numpy.uint16,
        'dbr_long_t'   : numpy.int32,
        'dbr_double_t' : numpy.float64,
    }
    has_numpy = True
except ImportError:
    has_numpy = False

import sys
if sys.hexversion >= 0x03000000:
    basestring = [str, bytes]

# globals
__channels = {}
__exception_callback = None

from cffi import FFI

ffi = FFI()

# cadef.h
ffi.cdef("""
typedef void *chid;
typedef chid chanId;
typedef long chtype;
typedef unsigned capri;
typedef double ca_real;
typedef void *evid;

/* arguments passed to user connection handlers */
struct connection_handler_args {
    chanId chid; /* channel id */
    long op;    /* one of CA_OP_CONN_UP or CA_OP_CONN_DOWN */
};
typedef void caCh (struct connection_handler_args args);

typedef struct ca_access_rights {
    unsigned    read_access:1;
    unsigned    write_access:1;
} caar;

/* arguments passed to user access rights handlers */
struct  access_rights_handler_args {
    chanId  chid;   /* channel id */
    caar    ar;     /* new access rights state */
};

typedef void caArh (struct access_rights_handler_args args);


/*
 * Arguments passed to event handlers and get/put call back handlers.
 *
 * The status field below is the CA ECA_XXX status of the requested
 * operation which is saved from when the operation was attempted in the
 * server and copied back to the clients call back routine.
 * If the status is not ECA_NORMAL then the dbr pointer will be NULL
 * and the requested operation can not be assumed to be successful.
 */
typedef struct event_handler_args {
    void            *usr;   /* user argument supplied with request */
    chanId          chid;   /* channel id */
    long            type;   /* the type of the item returned */
    long            count;  /* the element count of the item returned */
    const void      *dbr;   /* a pointer to the item returned */
    int             status; /* ECA_XXX status of the requested op from the server */
} evargs;
typedef void caEventCallBackFunc (struct event_handler_args);

/* arguments passed to user exception handlers */
struct exception_handler_args {
    void            *usr;   /* user argument supplied when installed */
    chanId          chid;   /* channel id (may be nill) */
    long            type;   /* type requested */
    long            count;  /* count requested */
    void            *addr;  /* user's address to write results of CA_OP_GET */
    long            stat;   /* channel access ECA_XXXX status code */
    long            op;     /* CA_OP_GET, CA_OP_PUT, ..., CA_OP_OTHER */
    const char      *ctx;   /* a character string containing context info */
    const char      *pFile; /* source file name (may be NULL) */
    unsigned        lineNo; /* source file line number (may be zero) */
};


short           ca_field_type(chid chan);
unsigned long   ca_element_count(chid chan);
const char *    ca_name (chid chan);
void            ca_set_puser (chid chan, void *puser);
void *          ca_puser (chid chan);
unsigned        ca_read_access (chid chan);
unsigned        ca_write_access (chid chan);

/*
 *  cs_ - `channel state'
 *
 *  cs_never_conn       valid chid, IOC not found
 *  cs_prev_conn        valid chid, IOC was found, but unavailable
 *  cs_conn             valid chid, IOC was found, still available
 *  cs_closed           channel deleted by user
 */
enum channel_state {cs_never_conn, cs_prev_conn, cs_conn, cs_closed};
enum channel_state ca_state (chid chan);

/************************************************************************/
/*  Perform Library Initialization                                      */
/*                                                                      */
/*  Must be called once before calling any of the other routines        */
/************************************************************************/
enum ca_preemptive_callback_select
{ ca_disable_preemptive_callback, ca_enable_preemptive_callback };
int ca_context_create(enum ca_preemptive_callback_select enable_premptive);

/************************************************************************/
/*  Remove CA facility from your task                                   */
/*                                                                      */
/*  Normally called automatically at task exit                          */
/************************************************************************/
void ca_context_destroy (void);

/*
 * ca_create_channel ()
 *
 * pChanName            R   channel name string
 * pConnStateCallback   R   address of connection state change
 *                          callback function
 * pUserPrivate         R   placed in the channel's user private field
 *                          o can be fetched later by ca_puser(CHID)
 *                          o passed as void * arg to *pConnectCallback above
 * priority             R   priority level in the server 0 - 100
 * pChanID              RW  channel id written here
 */
int ca_create_channel
(
    const char     *pChanName,
    caCh           *pConnStateCallback,
    void           *pUserPrivate,
    capri          priority,
    void           *pChanID
);

/*
 * ca_change_connection_event()
 *
 * chan     R   channel identifier
 * pfunc    R   address of connection call-back function
 */
int ca_change_connection_event
(
     chid       chan,
     caCh *     pfunc
);

/*
 * ca_replace_access_rights_event ()
 *
 * chan     R   channel identifier
 * pfunc    R   address of access rights call-back function
 */
int ca_replace_access_rights_event (
     chid   chan,
     caArh  *pfunc
);

/*
 * ca_add_exception_event ()
 *
 * replace the default exception handler
 *
 * pfunc    R   address of exception call-back function
 * pArg     R   copy of this pointer passed to exception
 *          call-back function
 */
typedef void caExceptionHandler (struct exception_handler_args);
int ca_add_exception_event
(
     caExceptionHandler *pfunc,
     void               *pArg
);

/*
 * ca_clear_channel()
 * - deallocate resources reserved for a channel
 *
 * chanId   R   channel ID
 */
int ca_clear_channel
(
     chid   chanId
);

/************************************************************************/
/*  Write a value to a channel                                          */
/************************************************************************/
/*
 * ca_array_put()
 *
 * type         R   data type from db_access.h
 * count        R   array element count
 * chan         R   channel identifier
 * pValue       R   new channel value copied from this location
 */
int ca_array_put
(
     chtype         type,
     unsigned long  count,
     chid           chanId,
     const void *   pValue
);

/*
 * ca_array_put_callback()
 *
 * This routine functions identically to the original ca put request
 * with the addition of a callback to the user supplied function
 * after recod processing completes in the IOC. The arguments
 * to the user supplied callback function are declared in
 * the structure event_handler_args and include the pointer
 * sized user argument supplied when ca_array_put_callback() is called.
 *
 * type         R   data type from db_access.h
 * count        R   array element count
 * chan         R   channel identifier
 * pValue       R   new channel value copied from this location
 * pFunc        R   pointer to call-back function
 * pArg         R   copy of this pointer passed to pFunc
 */
int ca_array_put_callback
(
     chtype                 type,
     unsigned long          count,
     chid                   chanId,
     const void *           pValue,
     caEventCallBackFunc *  pFunc,
     void *                 pArg
);

/************************************************************************/
/*  Read a value from a channel                                         */
/************************************************************************/
/*
 * ca_array_get()
 *
 * type     R   data type from db_access.h
 * count    R   array element count
 * chan     R   channel identifier
 * pValue   W   channel value copied to this location
 */
int ca_array_get
(
    long           type,
    unsigned long  count,
    chid           chanId,
    void *         pValue
);

/************************************************************************/
/*  Read a value from a channel and run a callback when the value       */
/*  returns                                                             */
/*                                                                      */
/*                                                                      */
/************************************************************************/
/*
 * ca_array_get_callback()
 *
 * type     R   data type from db_access.h
 * count    R   array element count
 * chan     R   channel identifier
 * pFunc    R   pointer to call-back function
 * pArg     R   copy of this pointer passed to pFunc
 */
int ca_array_get_callback
(
    chtype                 type,
    unsigned long          count,
    chid                   chanId,
    caEventCallBackFunc *  pFunc,
    void *                 pArg
);

/************************************************************************/
/*  Specify a function to be executed whenever significant changes      */
/*  occur to a channel.                                                 */
/*  NOTES:                                                              */
/*  1)  Evid may be omited by passing a NULL pointer                    */
/*                                                                      */
/*  2)  An array count of zero specifies the native db count            */
/*                                                                      */
/************************************************************************/

/*
 * ca_create_subscription ()
 *
 * type     R   data type from db_access.h
 * count    R   array element count
 * chan     R   channel identifier
 * mask     R   event mask - one of {DBE_VALUE, DBE_ALARM, DBE_LOG}
 * pFunc    R   pointer to call-back function
 * pArg     R   copy of this pointer passed to pFunc
 * pEventID W   event id written at specified address
 */
int ca_create_subscription
(
    chtype                 type,
    unsigned long          count,
    chid                   chanId,
    long                   mask,
    caEventCallBackFunc *  pFunc,
    void *                 pArg,
    evid *                 pEventID
);

/************************************************************************/
/*  Remove a function from a list of those specified to run             */
/*  whenever significant changes occur to a channel                     */
/*                                                                      */
/************************************************************************/
/*
 * ca_clear_subscription()
 *
 * eventID  R   event id
 */
int ca_clear_subscription
(
    evid    eventId
);

/************************************************************************/
/*                                                                      */
/*   Requested data is not necessarily stable prior to                  */
/*   return from called subroutine.  Call ca_pend_io()                  */
/*   to guarantee that requested data is stable.  Call the routine      */
/*   ca_flush_io() to force all outstanding requests to be              */
/*   sent out over the network.  Significant increases in               */
/*   performance have been measured when batching several remote        */
/*   requests together into one message.  Additional                    */
/*   improvements can be obtained by performing local processing        */
/*   in parallel with outstanding remote processing.                    */
/*                                                                      */
/*   FLOW OF TYPICAL APPLICATION                                        */
/*                                                                      */
/*   search()       ! Obtain Channel ids                                */
/*   .              ! "				                                    */
/*   .              ! "                                                 */
/*   pend_io        ! wait for channels to connect                      */
/*                                                                      */
/*   get()          ! several requests for remote info                  */
/*   get()          ! "					                                */
/*   add_event()    ! "					                                */
/*   get()          ! "					                                */
/*   .                                                                  */
/*   .                                                                  */
/*   .                                                                  */
/*   flush_io()     ! send get requests                                 */
/*                  ! optional parallel processing                      */
/*   .              ! "					                                */
/*   .              ! "					                                */
/*   pend_io()      ! wait for replies from get requests                */
/*   .              ! access to requested data                          */
/*   .              ! "					                                */
/*   pend_event()   ! wait for requested events                         */
/*                                                                      */
/************************************************************************/

/************************************************************************/
/*  These routines wait for channel subscription events and call the    */
/*  functions specified with add_event when events occur. If the        */
/*  timeout is specified as 0 an infinite timeout is assumed.           */
/*  ca_flush_io() is called by this routine. If ca_pend_io ()           */
/*  is called when no IO is outstanding then it will return immediately */
/*  without processing.                                                 */
/************************************************************************/

/*
 * ca_pend_event()
 *
 * timeOut  R   wait for this delay in seconds
 */
int ca_pend_event(ca_real timeOut);

/*
 * ca_pend_io()
 *
 * timeOut  R   wait for this delay in seconds but return early
 *              if all get requests (or search requests with null
 *              connection handler pointer have completed)
 */
int ca_pend_io(ca_real timeOut);

/************************************************************************/
/*  Send out all outstanding messages in the send queue                 */
/************************************************************************/
/*
 * ca_flush_io()
 */
int ca_flush_io();

/*
 * ca_host_name_function()
 *
 * channel  R   channel identifier
 *
 * !!!! this function is _not_ thread safe !!!!
 */
const char * ca_host_name (chid channel);
/* thread safe version */
unsigned ca_get_host_name ( chid pChan,
    char *pBuf, unsigned bufLength );

/*
 * ca_replace_printf_handler ()
 *
 * for apps that want to change where ca formatted
 * text output goes
 *
 * use two ifdef's for trad C compatibility
 *
 * ca_printf_func   R   pointer to new function called when
 *                          CA prints an error message
 */
/*
typedef int caPrintfFunc (const char *pformat, va_list args);
int ca_replace_printf_handler (
    caPrintfFunc    *ca_printf_func
);
*/

/*
 * used when an auxillary thread needs to join a CA client context started
 * by another thread
 */
struct ca_client_context * ca_current_context ();
int ca_attach_context ( struct ca_client_context * context );


int ca_client_status ( unsigned level );
int ca_context_status ( struct ca_client_context *, unsigned level );


const char * ca_message(long ca_status);

""")

# epicsTypes.h
ffi.cdef("""
typedef int8_t          epicsInt8;
typedef uint8_t         epicsUInt8;
typedef int16_t         epicsInt16;
typedef uint16_t        epicsUInt16;
typedef epicsUInt16     epicsEnum16;
typedef int32_t         epicsInt32;
typedef uint32_t        epicsUInt32;
typedef int64_t         epicsInt64;
typedef uint64_t        epicsUInt64;

typedef float           epicsFloat32;
typedef double          epicsFloat64;
typedef epicsInt32      epicsStatus;

typedef struct {
    unsigned    length;
    char        *pString;
}epicsString;

/*
 * !! Dont use this - it may vanish in the future !!
 *
 * Provided only for backwards compatibility with
 * db_access.h
 *
 */
typedef char            epicsOldString[40];

""")

# epicsTime.h
ffi.cdef("""
/* epics time stamp for C interface*/
typedef struct epicsTimeStamp {
    epicsUInt32    secPastEpoch;   /* seconds since 0000 Jan 1, 1990 */
    epicsUInt32    nsec;           /* nanoseconds within second */
} epicsTimeStamp;
""")

# db_access.h
ffi.cdef("""
/*
 * architecture independent types
 *
 * (so far this is sufficient for all archs we have ported to)
 */
typedef epicsOldString dbr_string_t;
typedef epicsUInt8 dbr_char_t;
typedef epicsInt16 dbr_short_t;
typedef epicsUInt16	dbr_ushort_t;
typedef epicsInt16 dbr_int_t;
typedef epicsUInt16 dbr_enum_t;
typedef epicsInt32 dbr_long_t;
typedef epicsUInt32 dbr_ulong_t;
typedef epicsFloat32 dbr_float_t;
typedef epicsFloat64 dbr_double_t;
typedef epicsUInt16	dbr_put_ackt_t;
typedef epicsUInt16	dbr_put_acks_t;
typedef epicsOldString dbr_stsack_string_t;
typedef epicsOldString dbr_class_name_t;


/* VALUES WITH STATUS STRUCTURES */

/* structure for a  string status field */
struct dbr_sts_string {
	dbr_short_t	status;	 		/* status of value */
	dbr_short_t	severity;		/* severity of alarm */
	dbr_string_t	value;			/* current value */
};

/* structure for a  string status and ack field */
struct dbr_stsack_string{
	dbr_ushort_t	status;	 		/* status of value */
	dbr_ushort_t	severity;		/* severity of alarm */
	dbr_ushort_t	ackt;	 		/* ack transient? */
	dbr_ushort_t	acks;			/* ack severity	*/
	dbr_string_t	value;			/* current value */
};
/* structure for an short status field */
struct dbr_sts_int{
	dbr_short_t	status;	 		/* status of value */
	dbr_short_t	severity;		/* severity of alarm */
	dbr_short_t	value;			/* current value */
};
struct dbr_sts_short{
	dbr_short_t	status;	 		/* status of value */
	dbr_short_t	severity;		/* severity of alarm */
	dbr_short_t	value;			/* current value */
};

/* structure for a  float status field */
struct dbr_sts_float{
	dbr_short_t	status;	 		/* status of value */
	dbr_short_t	severity;		/* severity of alarm */
	dbr_float_t	value;			/* current value */
};

/* structure for a  enum status field */
struct dbr_sts_enum{
	dbr_short_t	status;	 		/* status of value */
	dbr_short_t	severity;		/* severity of alarm */
	dbr_enum_t	value;			/* current value */
};

/* structure for a char status field */
struct dbr_sts_char{
	dbr_short_t	status;	 	/* status of value */
	dbr_short_t	severity;	/* severity of alarm */
	dbr_char_t	RISC_pad;	/* RISC alignment */
	dbr_char_t	value;		/* current value */
};

/* structure for a long status field */
struct dbr_sts_long{
	dbr_short_t	status;	 		/* status of value */
	dbr_short_t	severity;		/* severity of alarm */
	dbr_long_t	value;			/* current value */
};

/* structure for a double status field */
struct dbr_sts_double{
	dbr_short_t	status;	 		/* status of value */
	dbr_short_t	severity;		/* severity of alarm */
	dbr_long_t	RISC_pad;		/* RISC alignment */
	dbr_double_t	value;			/* current value */
};

/* VALUES WITH STATUS AND TIME STRUCTURES */

/* structure for a  string time field */
struct dbr_time_string{
	dbr_short_t	status;	 		/* status of value */
	dbr_short_t	severity;		/* severity of alarm */
	epicsTimeStamp	stamp;			/* time stamp */
	dbr_string_t	value;			/* current value */
};

/* structure for an short time field */
struct dbr_time_short{
	dbr_short_t	status;	 		/* status of value */
	dbr_short_t	severity;		/* severity of alarm */
	epicsTimeStamp	stamp;			/* time stamp */
	dbr_short_t	RISC_pad;		/* RISC alignment */
	dbr_short_t	value;			/* current value */
};

/* structure for a  float time field */
struct dbr_time_float{
	dbr_short_t	status;	 		/* status of value */
	dbr_short_t	severity;		/* severity of alarm */
	epicsTimeStamp	stamp;			/* time stamp */
	dbr_float_t	value;			/* current value */
};

/* structure for a  enum time field */
struct dbr_time_enum{
	dbr_short_t	status;	 		/* status of value */
	dbr_short_t	severity;		/* severity of alarm */
	epicsTimeStamp	stamp;			/* time stamp */
	dbr_short_t	RISC_pad;		/* RISC alignment */
	dbr_enum_t	value;			/* current value */
};

/* structure for a char time field */
struct dbr_time_char{
	dbr_short_t	status;	 		/* status of value */
	dbr_short_t	severity;		/* severity of alarm */
	epicsTimeStamp	stamp;			/* time stamp */
	dbr_short_t	RISC_pad0;		/* RISC alignment */
	dbr_char_t	RISC_pad1;		/* RISC alignment */
	dbr_char_t	value;			/* current value */
};

/* structure for a long time field */
struct dbr_time_long{
	dbr_short_t	status;	 		/* status of value */
	dbr_short_t	severity;		/* severity of alarm */
	epicsTimeStamp	stamp;			/* time stamp */
	dbr_long_t	value;			/* current value */
};

/* structure for a double time field */
struct dbr_time_double{
	dbr_short_t	status;	 		/* status of value */
	dbr_short_t	severity;		/* severity of alarm */
	epicsTimeStamp	stamp;			/* time stamp */
	dbr_long_t	RISC_pad;		/* RISC alignment */
	dbr_double_t	value;			/* current value */
};

/* VALUES WITH STATUS AND GRAPHIC STRUCTURES */

/* structure for a graphic string */
	/* not implemented; use struct_dbr_sts_string */

/* structure for a graphic short field */
struct dbr_gr_int{
	dbr_short_t	status;	 		/* status of value */
	dbr_short_t	severity;		/* severity of alarm */
	char		units[8];	/* units of value */
	dbr_short_t	upper_disp_limit;	/* upper limit of graph */
	dbr_short_t	lower_disp_limit;	/* lower limit of graph */
	dbr_short_t	upper_alarm_limit;
	dbr_short_t	upper_warning_limit;
	dbr_short_t	lower_warning_limit;
	dbr_short_t	lower_alarm_limit;
	dbr_short_t	value;			/* current value */
};
struct dbr_gr_short{
	dbr_short_t	status;	 		/* status of value */
	dbr_short_t	severity;		/* severity of alarm */
	char		units[8];	/* units of value */
	dbr_short_t	upper_disp_limit;	/* upper limit of graph */
	dbr_short_t	lower_disp_limit;	/* lower limit of graph */
	dbr_short_t	upper_alarm_limit;
	dbr_short_t	upper_warning_limit;
	dbr_short_t	lower_warning_limit;
	dbr_short_t	lower_alarm_limit;
	dbr_short_t	value;			/* current value */
};

/* structure for a graphic floating point field */
struct dbr_gr_float{
	dbr_short_t	status;	 		/* status of value */
	dbr_short_t	severity;		/* severity of alarm */
	dbr_short_t	precision;		/* number of decimal places */
	dbr_short_t	RISC_pad0;		/* RISC alignment */
	char		units[8];	/* units of value */
	dbr_float_t	upper_disp_limit;	/* upper limit of graph */
	dbr_float_t	lower_disp_limit;	/* lower limit of graph */
	dbr_float_t	upper_alarm_limit;
	dbr_float_t	upper_warning_limit;
	dbr_float_t	lower_warning_limit;
	dbr_float_t	lower_alarm_limit;
	dbr_float_t	value;			/* current value */
};

/* structure for a graphic enumeration field */
struct dbr_gr_enum{
	dbr_short_t	status;	 		/* status of value */
	dbr_short_t	severity;		/* severity of alarm */
	dbr_short_t	no_str;			/* number of strings */
	char		strs[16][26];
						/* state strings */
	dbr_enum_t	value;			/* current value */
};

/* structure for a graphic char field */
struct dbr_gr_char{
	dbr_short_t	status;	 		/* status of value */
	dbr_short_t	severity;		/* severity of alarm */
	char		units[8];	/* units of value */
	dbr_char_t	upper_disp_limit;	/* upper limit of graph */
	dbr_char_t	lower_disp_limit;	/* lower limit of graph */
	dbr_char_t	upper_alarm_limit;
	dbr_char_t	upper_warning_limit;
	dbr_char_t	lower_warning_limit;
	dbr_char_t	lower_alarm_limit;
	dbr_char_t	RISC_pad;		/* RISC alignment */
	dbr_char_t	value;			/* current value */
};

/* structure for a graphic long field */
struct dbr_gr_long{
	dbr_short_t	status;	 		/* status of value */
	dbr_short_t	severity;		/* severity of alarm */
	char		units[8];	/* units of value */
	dbr_long_t	upper_disp_limit;	/* upper limit of graph */
	dbr_long_t	lower_disp_limit;	/* lower limit of graph */
	dbr_long_t	upper_alarm_limit;
	dbr_long_t	upper_warning_limit;
	dbr_long_t	lower_warning_limit;
	dbr_long_t	lower_alarm_limit;
	dbr_long_t	value;			/* current value */
};

/* structure for a graphic double field */
struct dbr_gr_double{
	dbr_short_t	status;	 		/* status of value */
	dbr_short_t	severity;		/* severity of alarm */
	dbr_short_t	precision;		/* number of decimal places */
	dbr_short_t	RISC_pad0;		/* RISC alignment */
	char		units[8];	/* units of value */
	dbr_double_t	upper_disp_limit;	/* upper limit of graph */
	dbr_double_t	lower_disp_limit;	/* lower limit of graph */
	dbr_double_t	upper_alarm_limit;
	dbr_double_t	upper_warning_limit;
	dbr_double_t	lower_warning_limit;
	dbr_double_t	lower_alarm_limit;
	dbr_double_t	value;			/* current value */
};

/* VALUES WITH STATUS, GRAPHIC and CONTROL STRUCTURES */

/* structure for a control string */
	/* not implemented; use struct_dbr_sts_string */

/* structure for a control integer */
struct dbr_ctrl_int{
	dbr_short_t	status;	 		/* status of value */
	dbr_short_t	severity;		/* severity of alarm */
	char		units[8];	/* units of value */
	dbr_short_t	upper_disp_limit;	/* upper limit of graph */
	dbr_short_t	lower_disp_limit;	/* lower limit of graph */
	dbr_short_t	upper_alarm_limit;
	dbr_short_t	upper_warning_limit;
	dbr_short_t	lower_warning_limit;
	dbr_short_t	lower_alarm_limit;
	dbr_short_t	upper_ctrl_limit;	/* upper control limit */
	dbr_short_t	lower_ctrl_limit;	/* lower control limit */
	dbr_short_t	value;			/* current value */
};
struct dbr_ctrl_short{
	dbr_short_t	status;	 		/* status of value */
	dbr_short_t	severity;		/* severity of alarm */
	char		units[8];	/* units of value */
	dbr_short_t	upper_disp_limit;	/* upper limit of graph */
	dbr_short_t	lower_disp_limit;	/* lower limit of graph */
	dbr_short_t	upper_alarm_limit;
	dbr_short_t	upper_warning_limit;
	dbr_short_t	lower_warning_limit;
	dbr_short_t	lower_alarm_limit;
	dbr_short_t	upper_ctrl_limit;	/* upper control limit */
	dbr_short_t	lower_ctrl_limit;	/* lower control limit */
	dbr_short_t	value;			/* current value */
};

/* structure for a control floating point field */
struct dbr_ctrl_float{
	dbr_short_t	status;	 		/* status of value */
	dbr_short_t	severity;		/* severity of alarm */
	dbr_short_t	precision;		/* number of decimal places */
	dbr_short_t	RISC_pad;		/* RISC alignment */
	char		units[8];	/* units of value */
	dbr_float_t	upper_disp_limit;	/* upper limit of graph */
	dbr_float_t	lower_disp_limit;	/* lower limit of graph */
	dbr_float_t	upper_alarm_limit;
	dbr_float_t	upper_warning_limit;
	dbr_float_t	lower_warning_limit;
	dbr_float_t	lower_alarm_limit;
 	dbr_float_t	upper_ctrl_limit;	/* upper control limit */
	dbr_float_t	lower_ctrl_limit;	/* lower control limit */
	dbr_float_t	value;			/* current value */
};

/* structure for a control enumeration field */
struct dbr_ctrl_enum{
	dbr_short_t	status;	 		/* status of value */
	dbr_short_t	severity;		/* severity of alarm */
	dbr_short_t	no_str;			/* number of strings */
	char	strs[16][26];
					/* state strings */
	dbr_enum_t	value;		/* current value */
};

/* structure for a control char field */
struct dbr_ctrl_char{
	dbr_short_t	status;	 		/* status of value */
	dbr_short_t	severity;		/* severity of alarm */
	char		units[8];	/* units of value */
	dbr_char_t	upper_disp_limit;	/* upper limit of graph */
	dbr_char_t	lower_disp_limit;	/* lower limit of graph */
	dbr_char_t	upper_alarm_limit;
	dbr_char_t	upper_warning_limit;
	dbr_char_t	lower_warning_limit;
	dbr_char_t	lower_alarm_limit;
	dbr_char_t	upper_ctrl_limit;	/* upper control limit */
	dbr_char_t	lower_ctrl_limit;	/* lower control limit */
	dbr_char_t	RISC_pad;		/* RISC alignment */
	dbr_char_t	value;			/* current value */
};

/* structure for a control long field */
struct dbr_ctrl_long{
	dbr_short_t	status;	 		/* status of value */
	dbr_short_t	severity;		/* severity of alarm */
	char		units[8];	/* units of value */
	dbr_long_t	upper_disp_limit;	/* upper limit of graph */
	dbr_long_t	lower_disp_limit;	/* lower limit of graph */
	dbr_long_t	upper_alarm_limit;
	dbr_long_t	upper_warning_limit;
	dbr_long_t	lower_warning_limit;
	dbr_long_t	lower_alarm_limit;
	dbr_long_t	upper_ctrl_limit;	/* upper control limit */
	dbr_long_t	lower_ctrl_limit;	/* lower control limit */
	dbr_long_t	value;			/* current value */
};

/* structure for a control double field */
typedef struct dbr_ctrl_double{
	dbr_short_t	status;	 		/* status of value */
	dbr_short_t	severity;		/* severity of alarm */
	dbr_short_t	precision;		/* number of decimal places */
	dbr_short_t	RISC_pad0;		/* RISC alignment */
	char		units[8];	/* units of value */
	dbr_double_t	upper_disp_limit;	/* upper limit of graph */
	dbr_double_t	lower_disp_limit;	/* lower limit of graph */
	dbr_double_t	upper_alarm_limit;
	dbr_double_t	upper_warning_limit;
	dbr_double_t	lower_warning_limit;
	dbr_double_t	lower_alarm_limit;
	dbr_double_t	upper_ctrl_limit;	/* upper control limit */
	dbr_double_t	lower_ctrl_limit;	/* lower control limit */
	dbr_double_t	value;			/* current value */
};

/* union for each fetch buffers */
union db_access_val{
	dbr_string_t		strval;		/* string max size	      */
	dbr_short_t		shrtval;	/* short		      */
	dbr_short_t		intval;		/* short		      */
	dbr_float_t		fltval;		/* IEEE Float		      */
	dbr_enum_t		enmval;		/* item number		      */
	dbr_char_t		charval;	/* character		      */
	dbr_long_t		longval;	/* long			      */
	dbr_double_t		doubleval;	/* double		      */
	struct dbr_sts_string	sstrval;	/* string field	with status   */
	struct dbr_sts_short	sshrtval;	/* short field with status    */
	struct dbr_sts_float	sfltval;	/* float field with status    */
	struct dbr_sts_enum	senmval;	/* item number with status    */
	struct dbr_sts_char	schrval;	/* char field with status     */
	struct dbr_sts_long	slngval;	/* long field with status     */
	struct dbr_sts_double	sdblval;	/* double field with time     */
	struct dbr_time_string	tstrval;	/* string field	with time     */
	struct dbr_time_short	tshrtval;	/* short field with time      */
	struct dbr_time_float	tfltval;	/* float field with time      */
	struct dbr_time_enum	tenmval;	/* item number with time      */
	struct dbr_time_char	tchrval;	/* char field with time	      */
	struct dbr_time_long	tlngval;	/* long field with time	      */
	struct dbr_time_double	tdblval;	/* double field with time     */
	struct dbr_sts_string	gstrval;	/* graphic string info	      */
	struct dbr_gr_short	gshrtval;	/* graphic short info	      */
	struct dbr_gr_float	gfltval;	/* graphic float info	      */
	struct dbr_gr_enum	genmval;	/* graphic item info	      */
	struct dbr_gr_char	gchrval;	/* graphic char info	      */
	struct dbr_gr_long	glngval;	/* graphic long info	      */
	struct dbr_gr_double	gdblval;	/* graphic double info	      */
	struct dbr_sts_string	cstrval;	/* control string info	      */
	struct dbr_ctrl_short	cshrtval;	/* control short info	      */
	struct dbr_ctrl_float	cfltval;	/* control float info	      */
	struct dbr_ctrl_enum	cenmval;	/* control item info	      */
	struct dbr_ctrl_char	cchrval;	/* control char info	      */
	struct dbr_ctrl_long	clngval;	/* control long info	      */
	struct dbr_ctrl_double	cdblval;	/* control double info	      */
	dbr_put_ackt_t		putackt;	/* item number		      */
	dbr_put_acks_t		putacks;	/* item number		      */
	struct dbr_sts_string	sastrval;	/* string field	with status   */
	dbr_string_t		classname;	/* string max size	      */
};

/* size for each type - array indexed by the DBR_ type code */
const unsigned short dbr_size[];

/* size for each type's value - array indexed by the DBR_ type code */
const unsigned short dbr_value_size[];

const unsigned short dbr_value_offset[];
""")

# used with connection_handler_args
CA_OP_CONN_UP    =   6
CA_OP_CONN_DOWN  =   7

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

def dbr_size_n(TYPE,COUNT):
    if COUNT <=0:
        return libca.dbr_size[TYPE]
    else:
        return libca.dbr_size[TYPE] + (COUNT-1) * libca.dbr_value_size[TYPE]

#/*
# * ptr to value given a pointer to the structure and the DBR type
# */
def dbr_value_ptr(PDBR, DBR_TYPE):
    return ffi.cast('char*', PDBR) + libca.dbr_value_offset[DBR_TYPE]

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

import os.path
import platform
import sys
def libca_path():
    cwd = os.path.dirname(os.path.abspath(__file__))
    osname = platform.system()
    is64bit = sys.maxsize > 2**32
    if osname == 'Darwin':
        host_arch = 'darwin-x86'
        libca_name = 'libca.dylib'
    elif osname == 'Linux':
        libca_name = 'libca.so'
        if is64bit:
            host_arch = 'linux-x86_64'
        else:
            host_arch = 'linux-x86'
    elif osname == 'Windows':
        libca_name = 'ca.dll'
        if is64bit:
            host_arch = 'windows-x64'
        else:
            host_arch = 'win32-x86'
    else:
        raise OSError('Unsupported Operation System %s' % osname)

    return os.path.join(cwd, 'lib', host_arch, libca_name)


libca = ffi.dlopen(libca_path())


def _format_dbr_sts(cvalue, value):
    value['status'] = cvalue.status
    value['severity'] = cvalue.severity


def _format_dbr_time(cvalue, value):
    timestamp_posix = cvalue.stamp.secPastEpoch + POSIX_TIME_AT_EPICS_EPOCH + cvalue.stamp.nsec / 1e9
    value['stamp'] = datetime.fromtimestamp(timestamp_posix)


def _format_dbr_gr(cvalue, value):
    value['units'] = ffi.string(cvalue.units)
    value['upper_disp_limit'] = cvalue.upper_disp_limit
    value['lower_disp_limit'] = cvalue.lower_disp_limit
    value['upper_alarm_limit'] = cvalue.upper_alarm_limit
    value['upper_warning_limit'] = cvalue.upper_warning_limit
    value['lower_alarm_limit'] = cvalue.lower_alarm_limit
    value['lower_warning_limit'] = cvalue.lower_warning_limit


def _format_dbr_ctrl(cvalue, value):
    value['upper_ctrl_limit'] = cvalue.upper_ctrl_limit
    value['lower_ctrl_limit'] = cvalue.lower_ctrl_limit


def _format_plain_value(valueType, count, cvalue):
    if count == 1:
        value = ffi.cast(valueType+'*', cvalue)[0]
    else:
        cvalue = ffi.cast(valueType+'[%d]'%count, cvalue)

        if has_numpy:
            value = numpy.frombuffer(ffi.buffer(cvalue), dtype=ctype2dtype[valueType])
        else:
            value = list(cvalue)

    return value


def _format_dbr(dbrType, count, dbrValue):
    if dbrType == DBR_STRING:
        cvalue = _format_plain_value('dbr_string_t*', dbrValue)
        if count == 1:
            value = ffi.string(cvalue[0])
        else:
            value = []
            for i in range(count):
                value.append(ffi.string(cvalue[i]))

    elif dbrType == DBR_INT:
        value = _format_plain_value('dbr_int_t', count, dbrValue)

    elif dbrType == DBR_FLOAT:
        value = _format_plain_value('dbr_float_t', count, dbrValue)

    elif dbrType == DBR_CHAR:
        value = _format_plain_value('dbr_char_t', count, dbrValue)

    elif dbrType == DBR_ENUM:
        value = _format_plain_value('dbr_enum_t', count, dbrValue)

    elif dbrType == DBR_LONG:
        value = _format_plain_value('dbr_long_t', count, dbrValue)

    elif dbrType == DBR_DOUBLE:
        value = _format_plain_value('dbr_double_t', count, dbrValue)

    elif dbrType == DBR_STS_DOUBLE:
        value = {}
        cvalue = ffi.cast('struct dbr_sts_double*', count, dbrValue)
        _format_dbr_sts(cvalue, value)
        value['value'] = _format_plain_value('dbr_double_t', count, dbr_value_ptr(cvalue, dbrType))

    elif dbrType == DBR_TIME_DOUBLE:
        value = {}
        cvalue = ffi.cast('struct dbr_time_double*', dbrValue)
        _format_dbr_sts(cvalue, value)
        _format_dbr_time(cvalue, value)
        value['value'] = _format_plain_value('dbr_double_t', count, dbr_value_ptr(cvalue, dbrType))

    elif dbrType == DBR_GR_DOUBLE:
        value = {}
        cvalue = ffi.cast('struct dbr_gr_double*', dbrValue)
        _format_dbr_sts(cvalue, value)
        _format_dbr_gr(cvalue, value)
        value['value'] = _format_plain_value('dbr_double_t', count, dbr_value_ptr(cvalue, dbrType))

    elif dbrType == DBR_CTRL_DOUBLE:
        value = {}
        cvalue = ffi.cast('struct dbr_ctrl_double*', dbrValue)
        _format_dbr_sts(cvalue, value)
        _format_dbr_gr(cvalue, value)
        value['precision'] = cvalue.precision
        _format_dbr_ctrl(cvalue, value)
        value['value'] = _format_plain_value('dbr_double_t', count, dbr_value_ptr(cvalue, dbrType))

    return value


def add_exception_event(callback, *args):
    """
    Replace the currently installed CA context global exception handler call back.

    :param callback:   User callback function to be executed when an exceptions occur.
                            Passing a nill value causes the default exception handler to be reinstalled.
                            The following structure is passed by value to the user's callback function.
                            Currently, the op field can be one of
                                CA_OP_GET, CA_OP_PUT, CA_OP_CREATE_CHANNEL, CA_OP_ADD_EVENT,
                                CA_OP_CLEAR_EVENT, or CA_OP_OTHER.
    :param arg:       User variable retained and passed back to user function above

    :return: ECA_NORMAL

    When an error occurs in the server asynchronous to the clients thread then information about this type of error
    is passed from the server to the client in an exception message. When the client receives this exception message
    an exception handler callback is called.
    The default exception handler prints a diagnostic message on the client's standard out and
    terminates execution if the error condition is severe.

    .. note::   Certain fields in "struct exception_handler_args" are not applicable in the context of some error messages.
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


@ffi.callback('void(*)(struct exception_handler_args)')
def _exceptionCB(carg):
    epics_arg = {}
    epics_arg['chid']    = carg.chid
    epics_arg['type']    = carg.type
    epics_arg['count']   = carg.count
    epics_arg['stat']    = carg.stat
    epics_arg['op']      = carg.op
    epics_arg['ctx']     = carg.ctx
    epics_arg['file']    = ffi.string(carg.pFile)
    epics_arg['lineNo']  = carg.lineNo

    user_callback, user_arg = ffi.from_handle(carg.usr)
    user_callback(epics_arg, user_arg)


@ffi.callback('void(*)(struct connection_handler_args)')
def _connectCB(carg):
    epics_arg = {}
    epics_arg['chid'] = carg.chid
    epics_arg['up'] = (carg.op == CA_OP_CONN_UP)

    user_callback, user_arg = ffi.from_handle(libca.ca_puser(carg.chid))
    user_callback(epics_arg, user_arg)


@ffi.callback('void(struct event_handler_args)')
def _putCB(arg):
    epics_arg = {}
    epics_arg['chid'] = arg.chid
    epics_arg['type'] = arg.type
    epics_arg['count'] = arg.count
    epics_arg['status'] = arg.status

    user_callback, user_arg = ffi.from_handle(arg.usr)
    __channels[arg.chid]['callbacks'].remove(arg.usr)
    user_callback(epics_arg, user_arg)


@ffi.callback('void(struct event_handler_args)')
def _eventCB(arg):
    epics_arg = {}
    epics_arg['chid'] = arg.chid
    epics_arg['type'] = arg.type
    epics_arg['count'] = arg.count
    epics_arg['status'] = arg.status
    epics_arg['value'] = _format_dbr(arg.type, arg.count, arg.dbr)

    user_callback, user_arg = ffi.from_handle(arg.usr)
    user_callback(epics_arg, user_arg)

@ffi.callback('void(struct event_handler_args)')
def _getCB(arg):
    epics_arg = {}
    epics_arg['chid'] = arg.chid
    epics_arg['type'] = arg.type
    epics_arg['count'] = arg.count
    epics_arg['status'] = arg.status
    epics_arg['value'] = _format_dbr(arg.type, arg.count, arg.dbr)

    user_callback, user_arg = ffi.from_handle(arg.usr)
    __channels[arg.chid]['callbacks'].remove(arg.usr)
    user_callback(epics_arg, user_arg)

def create_context(preemptive_callback = True):
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
    ca_context_destroy() hasn't been called, but on light weight systems such as vxWorks or RTEMS
    no cleanup occurs unless the application calls ca_context_destroy().
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
    :return: The current thread's CA context. If none then nill is returned.
    """
    return libca.ca_current_context()


def create_channel(name, callback, *args):
    """
    This function creates a CA channel.

    The CA client library will attempt to establish and maintain a virtual circuit between the caller's application
    and a named process variable in a CA server.
    Each call to ca_create_channel allocates resources in the CA client library and potentially also a CA server.
    The function ca_clear_channel() is used to release these resources.
    If successful, the routine writes a channel identifier into the user's variable of type "chid".
    This identifier can be used with any channel access call that operates on a channel.

    The circuit may be initially connected or disconnected depending on the state of the network and the location of the channel.
    A channel will only enter a connected state after the server's address is determined,
    and only if channel access successfully establishes a virtual circuit through the network to the server.
    Channel access routines that send a request to a server will return ECA_DISCONNCHID if the channel is currently disconnected.

    There are two ways to obtain asynchronous notification when a channel enters a connected state.

    The first and simplest method requires that you call ca_pend_io(), and wait for successful completion,
    prior to using a channel that was created specifying a nill connection call back function pointer.
    The second method requires that you register a connection handler by supplying a valid connection callback function pointer.
    This connection handler is called whenever the connection state of the channel changes.
    If you have installed a connection handler then ca_pend_io() will not block waiting for the channel to enter a connected state.
    The function ca_state(CHID) can be used to test the connection state of a channel.
    Valid connections may be isolated from invalid ones with this function if ca_pend_io() times out.

    Due to the inherently transient nature of network connections
    the order of connection call backs relative to the order that ca_create_channel() calls are made by the application
    can't be guaranteed, and application programs may need to be prepared for a connected channel to
    enter a disconnected state at any time.

    :param name:        Process variable name string.
    :param callback:    Optional user's call back function to be run when the connection state changes.
                        Casual users of channel access may decide to set this field to nill or 0
                        if they do not need to have a call back function run in response to each connection state change event.
                        The following structure is passed by value to the user's connection callback function.
                        The op field will be set by the CA client library to CA_OP_CONN_UP when the channel connects, and to CA_OP_CONN_DOWN when the channel disconnects.
                        See ca_puser if the PUSER argument is required in your callback handler.
                        ::

                            struct  ca_connection_handler_args {
                                chanId  chid;  /* channel id */
                                long    op;    /* one of CA_OP_CONN_UP or CA_OP_CONN_DOWN */
                            };

    :param args:        The value of this void pointer argument is retained in storage associated with the specified channel.
                        See the MACROS manual page for reading and writing this field.
                        Casual users of channel access may wish to set this field to nill or 0.
    :param priority:    The priority level for dispatch within the server or network,
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

    """
    pchid = ffi.new('chid *')

    connect_callback = ffi.new_handle((callback, args))

    status = libca.ca_create_channel(name, _connectCB, connect_callback, CA_PRIORITY_DEFAULT, pchid)
    chid = pchid[0]
    if chid != ffi.NULL:
        __channels[chid] = {'callbacks':set(), 'monitors' : {}}
        __channels[chid]['callbacks'].add(connect_callback)
    return chid


def get(chid, dbrType, count, callback, *args):
    """
    Read a scalar or array value from a process variable.

    :param chid: Channel identifier
    :param value: A scalar or array value to be written to the channel
    :param dbrType: The external type of the supplied value to be written.
                    Conversion will occur if this does not match the native type.
                    Default is the native type.
    :param count:   Element count to be read from the specified channel.
                    For ca_array_get_callback a count of zero means use the current element count from the server.
    :param callback: User supplied callback function to be run when requested operation completes.
    :param args: User supplied variable retained and then passed back to user supplied function above
    :return:    None

    When ca_get or ca_array_get are invoked the returned channel value can't be assumed to be stable
    in the application supplied buffer until after ECA_NORMAL is returned from ca_pend_io.
    If a connection is lost outstanding ca get requests are not automatically reissued following reconnect.

    When ca_get_callback or ca_array_get_callback are invoked a value is read from the channel and
    then the user's callback is invoked with a pointer to the retrieved value.
    Note that ca_pend_io will not block for the delivery of values requested by ca_get_callback.
    If the channel disconnects before a ca get callback request can be completed,
    then the clients call back function is called with failure status.

    All of these functions return ECA_DISCONN if the channel is currently disconnected.

    All get requests are accumulated (buffered) and not forwarded to the IOC until one of
    ca_flush_io, ca_pend_io, ca_pend_event, or ca_sg_pend are called.
    This allows several requests to be efficiently sent over the network in one message.

    """
    if count is None or count < 0:
        count = libca.ca_element_count(chid)

    if dbrType is None:
        dbrType = libca.ca_field_type(chid)

    if callable(callback):
        get_callback = ffi.new_handle((callback, args))
        __channels[chid]['callbacks'].add(get_callback)
        libca.ca_array_get_callback(dbrType, count, chid, _getCB, get_callback)
        return None
    else:
        value = ffi.new('char[]', dbr_size_n(dbrType, count))
        libca.ca_array_get(dbrType, count, chid, value)
        return value


DBR_TYPE_STRING = {
    DBR_STRING : 'dbr_string_t',
    DBR_INT:     'dbr_int_t',
    DBR_FLOAT:   'dbr_float_t',
    DBR_CHAR:    'dbr_char_t',
    DBR_ENUM:    'dbr_enum_t',
    DBR_LONG:    'dbr_long_t',
    DBR_DOUBLE:  'dbr_double_t',
}


def put(chid, value, dbrType, count, callback=None, *args):
    """
    Write a scalar or array value to a process variable.

    :param chid: Channel identifier
    :param value: A scalar or array value to be written to the channel
    :param dbrType: The external type of the supplied value to be written.
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

    When ca_put or ca_array_put are invoked the client will receive no response unless the request can not be fulfilled in the server.
    If unsuccessful an exception handler is run on the client side.

    When ca_put_callback or ca_array_put_callback are invoked the user supplied asynchronous call back is called only
    after the initiated write operation, and all actions resulting from the initiating write operation, complete.

    If unsuccessful the call back function is invoked indicating failure status.

    If the channel disconnects before a put callback request can be completed, then the client's call back function is
    called with failure status, but this does not guarantee that the server did not receive and process the request
    before the disconnect. If a connection is lost and then resumed outstanding ca put requests are not automatically
    reissued following reconnect.

    All of these functions return ECA_DISCONN if the channel is currently disconnected.

    All put requests are accumulated (buffered) and not forwarded to the IOC until one of ca_flush_io, ca_pend_io,
    ca_pend_event, or ca_sg_pend are called. This allows several requests to be efficiently combined into one message.
    """
    if dbrType is None:
        dbrType = libca.ca_field_type(chid)

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
        if isinstance(value, basestring) and dbrType == DBR_STRING:
            value_count = 1

   # setup c value
    if value_count == 1:
        cvalue = ffi.new(DBR_TYPE_STRING[dbrType]+'*', value)
    else:
        cvalue = ffi.new(DBR_TYPE_STRING[dbrType]+'[]', value)

    # the actual count requested is the minimum of all three
    count = min(count, element_count, value_count)

    if callback == None or not callable(callback):
        libca.ca_array_put(dbrType, count, chid, cvalue)
    else:
        put_callback = ffi.new_handle((callback,args,))
        __channels[chid]['callbacks'].add(put_callback)
        libca.ca_array_put_callback(dbrType, count, chid, cvalue, _putCB, put_callback)


def create_subscription(chid, dbrType, count, mask, callback, *args):
    """
    Register a state change subscription and specify a call back function to be invoked
    whenever the process variable undergoes significant state changes.

    :param chid: Channel identifier
    :param value: A scalar or array value to be written to the channel
    :param dbrType: The external type of the supplied value to be written.
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

    :param callback: User supplied callback function to be run when requested operation completes.
    :param args: User supplied variable retained and then passed back to user supplied function above
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
    until one of ca_clear_channel or ca_clear_subscription is called.

    Subscriptions may be installed or canceled against both connected and disconnected channels.
    The specified USERFUNC is called once immediately after the subscription is installed
    with the process variable's current state if the process variable is connected.
    Otherwise, the specified USERFUNC is called immediately after establishing a connection
    (or reconnection) with the process variable. The specified USERFUNC is called immediately
    with the process variable's current state from within ca_create_subscription()
    if the client and the process variable share the same address space.

    If a subscription is installed on a channel in a disconnected state
    then the requested count will be set to the native maximum element count of the channel
    if the requested count is larger.

    All subscription requests such as the above are accumulated (buffered)
    and not forwarded to the IOC until one of ca_flush_io, ca_pend_io, ca_pend_event, or ca_sg_pend are called.
    This allows several requests to be efficiently sent over the network in one message.

    If at any time after subscribing, read access to the specified process variable is lost,
    then the call back will be invoked immediately indicating that read access was lost via the status argument.
    When read access is restored normal event processing will resume starting always
    with at least one update indicating the current state of the channel.

    """
    if dbrType is None:
        dbrType = libca.ca_field_type(chid)

    element_count = libca.ca_element_count(chid)
    if count is None or count < 0 or count > element_count:
        count = element_count

    if mask is None:
        mask = DBE_VALUE | DBE_ALARM

    pevid = ffi.new('evid *')

    monitor_callback = ffi.new_handle((callback,args,))

    status = libca.ca_create_subscription(dbrType, count, chid, mask, _eventCB, monitor_callback, pevid)

    evid = pevid[0]

    if evid != ffi.NULL:
        __channels[chid]['monitors'][evid] = monitor_callback

    return evid


def clear_subscription(evid):
    """
    Cancel a subscription.

    :param evid: event id returned by :meth:`create_subscription`
    :return:
                - ECA_NORMAL - Normal successful completion
                - ECA_BADCHID - Corrupted CHID

    All cancel-subscription requests such as the above are accumulated (buffered) and not forwarded to the server
    until one of ca_flush_io, ca_pend_io, ca_pend_event, or ca_sg_pend are called.
    This allows several requests to be efficiently sent together in one message.

    """
    status = libca.ca_clear_subscription(evid)
    del __channels[chid]['monitors'][evid]

    return status


def clear_channel(chid):
    """
    Shutdown and reclaim resources associated with a channel created by ca_create_channel().

    :param chid: channel identifier
    :return:
                - ECA_NORMAL - Normal successful completion
                - ECA_BADCHID - Corrupted CHID

    All remote operation requests such as the above are accumulated (buffered) and not forwarded to the IOC
    until one of ca_flush_io, ca_pend_io, ca_pend_event, or ca_sg_pend are called.
    This allows several requests to be efficiently sent over the network in one message.

    Clearing a channel does not cause its disconnect handler to be called,
    but clearing a channel does shutdown and reclaim any channel state change event subscriptions (monitors)
    registered with the channel.

    """
    # clear all subscriptions
    for evid in __channels[chid]['monitors'].keys():
        status = clear_subscription(evid)

    status = libca.ca_clear_channel(chid)
    return status



pend_event = libca.ca_pend_event
pend_io = libca.ca_pend_io
def poll():
    libca.ca_pend_event(1e-12)


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



if __name__ == '__main__':

    def exceptionCB(epicsArgs, userArgs):
        print('exception callback')
        print('    ', userArgs)
        print('    ', message(epicsArgs['stat']))


    def connectCB(epicsArgs, userArgs):
        print('connect callback')
        print('    ', epicsArgs)
        print('    ', userArgs)


    def putCB(epicsArgs, userArgs):
        print('put callback')
        print('    ', epicsArgs)
        print('    ', userArgs)


    def getCB(epicsArgs, userArgs):
        print('get callback')
        print('    ', epicsArgs)
        print('    ', userArgs)


    def monitorCB(epicsArgs, userArgs):
        print('monitor callback')
        print('    ', epicsArgs)
        print('    ', userArgs)

    add_exception_event(exceptionCB)

    chid = create_channel('cacalc', callback=connectCB)
    status = pend_event(2)


    evid = create_subscription(chid, None, None, None, monitorCB, 1, 2, 3)
    pend_event(1)

    put(chid, [60, 50, 40], None, None, putCB, 1, 2, 3)
    pend_event(2)

    get(chid, None, None, getCB, 1, 2, 3)
    pend_event(2)

    status = clear_channel(chid)
