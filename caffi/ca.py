from cffi import FFI

ffi = FFI()

# cadef.h
ffi.cdef("""
typedef void *chid;
typedef chid chanId;
typedef long chtype;
typedef unsigned capri;
typedef double ca_real;
typedef long *evid;

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
int ca_clear_subsription
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

def format_dbr(dbrType, count, dbrValue):
    value = {}
    if dbrType == DBR_DOUBLE:
        value = ffi.cast('dbr_double_t*', dbrValue)

    elif dbrType == DBR_CTRL_DOUBLE:
        v = ffi.cast('struct dbr_ctrl_double*', dbrValue)
        value['value'] = ffi.cast('dbr_double_t*', dbr_value_ptr(v, dbrType))
        value['units'] = ffi.string(v.units)
        value['precision'] = v.precision
        value['upper_disp_limit'] = v.upper_disp_limit
        value['lower_disp_limit'] = v.lower_disp_limit
        value['upper_alarm_limit'] = v.upper_alarm_limit
        value['upper_warning_limit'] = v.upper_warning_limit
        value['lower_alarm_limit'] = v.lower_alarm_limit
        value['lower_warning_limit'] = v.lower_warning_limit
        value['upper_ctrl_limit'] = v.upper_ctrl_limit
        value['lower_ctrl_limit'] = v.lower_ctrl_limit

    return value

@ffi.callback('void(struct connection_handler_args)')
def connectCB(arg):
    args = {}
    args['chid'] = arg.chid
    args['op'] = arg.op == CA_OP_CONN_UP

@ffi.callback('void(struct exception_handler_args)')
def exceptionCB(arg):
    pass

@ffi.callback('void(struct event_handler_args)')
def eventCB(arg):
    args = {}
    args['chid'] = arg.chid
    args['type'] = arg.type
    args['count'] = arg.count
    args['status'] = arg.status
    print format_dbr(arg.type, arg.count, arg.dbr)

status = libca.ca_add_exception_event(exceptionCB, FFI.NULL)

def create_context(preemptive_callback = True):
    if preemptive_callback:
        return libca.ca_context_create(libca.ca_enable_preemptive_callback)
    else:
        return libca.ca_context_create(libca.ca_disable_preemptive_callback)


def destroy_context():
    libca.ca_context_destroy()

def create_channel(name, callback=FFI.NULL, args=FFI.NULL, priority = CA_PRIORITY_DEFAULT):
    pchid = ffi.new('chid *')
    status = libca.ca_create_channel(name, callback, args, priority, pchid)
    chid = pchid[0]
    return chid

def array_get(chid, dbrType=None, count=None):
    if count is None or count < 0:
        count = libca.ca_element_count(chid)
    if dbrType is None:
        dbrType = libca.ca_field_type(chid)

    value = ffi.new('char[]', dbr_size_n(dbrTye, count))
    libca.ca_array_get(DBR_CTRL_DOUBLE, count, chid, value)
    return value

def array_get_callback(chid, dbrType=None, count=None, callback=FFI.NULL, args=FFI.NULL):
    if count is None or count < 0:
        count = libca.ca_element_count(chid)
    if dbrType is None:
        dbrType = libca.ca_field_type(chid)

    libca.ca_array_get_callback(dbrType, count, chid, callback, args)

def array_put(chid, value, dbrType=None, count=None, callback=FFI.NULL, args=FFI.NULL):
    if count is None or count < 0:
        count = libca.ca_element_count(chid)
    if dbrType is None:
        dbrType = libca.ca_field_type(chid)

    libca.ca_array_put_callback(dbrType, count, chid, value, callback, args)

def clear_channel(chid):
    libca.ca_clear_channel(chid)



if __name__ == '__main__':

    chid = create_channel('cawave', callback=connectCB)
    status = libca.ca_pend_event(2)
    print libca.ca_message(status)

    array_get_callback(chid, dbrType=DBR_CTRL_DOUBLE, callback=eventCB)
    libca.ca_pend_event(3)

    v = ffi.new('double[12]', [1, 2, 3])
    array_put(chid, v, callback=eventCB)
    libca.ca_pend_event(3)

