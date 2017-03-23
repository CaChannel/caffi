#ifdef _WIN32
#include <windows.h>
#pragma warning( disable: 4047 4113 4133 )
#define load_library LoadLibrary
#define free_library FreeLibrary
#define find_symbol GetProcAddress
#define EXPORTAPI __declspec(dllexport)
#else
#include <stdio.h>
#include <dlfcn.h>
#define load_library(LIBNAME) dlopen(LIBNAME, RTLD_LAZY|RTLD_GLOBAL)
#define free_library dlclose
#define find_symbol dlsym
#define EXPORTAPI
#endif

/* database field types */
#define DBF_STRING	0
#define	DBF_INT		1
#define	DBF_SHORT	1
#define	DBF_FLOAT	2
#define	DBF_ENUM	3
#define	DBF_CHAR	4
#define	DBF_LONG	5
#define	DBF_DOUBLE	6
#define DBF_NO_ACCESS	7
#define	LAST_TYPE	DBF_DOUBLE
#define	VALID_DB_FIELD(x)	((x >= 0) && (x <= LAST_TYPE))
#define	INVALID_DB_FIELD(x)	((x < 0) || (x > LAST_TYPE))

/* data request buffer types */
#define DBR_STRING	DBF_STRING	
#define	DBR_INT		DBF_INT		
#define	DBR_SHORT	DBF_INT		
#define	DBR_FLOAT	DBF_FLOAT	
#define	DBR_ENUM	DBF_ENUM
#define	DBR_CHAR	DBF_CHAR
#define	DBR_LONG	DBF_LONG
#define	DBR_DOUBLE	DBF_DOUBLE
#define DBR_STS_STRING	7
#define	DBR_STS_SHORT	8
#define	DBR_STS_INT	DBR_STS_SHORT	
#define	DBR_STS_FLOAT	9
#define	DBR_STS_ENUM	10
#define	DBR_STS_CHAR	11
#define	DBR_STS_LONG	12
#define	DBR_STS_DOUBLE	13
#define	DBR_TIME_STRING	14
#define	DBR_TIME_INT	15
#define	DBR_TIME_SHORT	15
#define	DBR_TIME_FLOAT	16
#define	DBR_TIME_ENUM	17
#define	DBR_TIME_CHAR	18
#define	DBR_TIME_LONG	19
#define	DBR_TIME_DOUBLE	20
#define	DBR_GR_STRING	21
#define	DBR_GR_SHORT	22
#define	DBR_GR_INT	DBR_GR_SHORT	
#define	DBR_GR_FLOAT	23
#define	DBR_GR_ENUM	24
#define	DBR_GR_CHAR	25
#define	DBR_GR_LONG	26
#define	DBR_GR_DOUBLE	27
#define	DBR_CTRL_STRING	28
#define DBR_CTRL_SHORT	29
#define DBR_CTRL_INT	DBR_CTRL_SHORT	
#define	DBR_CTRL_FLOAT	30
#define DBR_CTRL_ENUM	31
#define	DBR_CTRL_CHAR	32
#define	DBR_CTRL_LONG	33
#define	DBR_CTRL_DOUBLE	34
#define DBR_PUT_ACKT	DBR_CTRL_DOUBLE + 1
#define DBR_PUT_ACKS    DBR_PUT_ACKT + 1
#define DBR_STSACK_STRING DBR_PUT_ACKS + 1
#define DBR_CLASS_NAME DBR_STSACK_STRING + 1
#define	LAST_BUFFER_TYPE	DBR_CLASS_NAME
#define	VALID_DB_REQ(x)	((x >= 0) && (x <= LAST_BUFFER_TYPE))
#define	INVALID_DB_REQ(x)	((x < 0) || (x > LAST_BUFFER_TYPE))

EXPORTAPI const char *dbf_text[] = {
	"TYPENOTCONN",
	"DBF_STRING",
	"DBF_SHORT",
	"DBF_FLOAT",
	"DBF_ENUM",
	"DBF_CHAR",
	"DBF_LONG",
	"DBF_DOUBLE",
	"DBF_NO_ACCESS"
};
EXPORTAPI char *dbf_text_invalid = "DBF_invalid";
EXPORTAPI short dbf_text_dim = (sizeof dbf_text)/(sizeof (char *));

EXPORTAPI const char *dbr_text[] = {
    "DBR_STRING",
    "DBR_SHORT",
    "DBR_FLOAT",
    "DBR_ENUM",
    "DBR_CHAR",
    "DBR_LONG",
    "DBR_DOUBLE",
    "DBR_STS_STRING",
    "DBR_STS_SHORT",
    "DBR_STS_FLOAT",
    "DBR_STS_ENUM",
    "DBR_STS_CHAR",
    "DBR_STS_LONG",
    "DBR_STS_DOUBLE",
    "DBR_TIME_STRING",
    "DBR_TIME_SHORT",
    "DBR_TIME_FLOAT",
    "DBR_TIME_ENUM",
    "DBR_TIME_CHAR",
    "DBR_TIME_LONG",
    "DBR_TIME_DOUBLE",
    "DBR_GR_STRING",
    "DBR_GR_SHORT",
    "DBR_GR_FLOAT",
    "DBR_GR_ENUM",
    "DBR_GR_CHAR",
    "DBR_GR_LONG",
    "DBR_GR_DOUBLE",
    "DBR_CTRL_STRING",
    "DBR_CTRL_SHORT",
    "DBR_CTRL_FLOAT",
    "DBR_CTRL_ENUM",
    "DBR_CTRL_CHAR",
    "DBR_CTRL_LONG",
    "DBR_CTRL_DOUBLE",
    "DBR_PUT_ACKT",
    "DBR_PUT_ACKS",
    "DBR_STSACK_STRING",
    "DBR_CLASS_NAME"
};
EXPORTAPI const char *dbr_text_invalid = "DBR_invalid";
EXPORTAPI const short dbr_text_dim = (sizeof dbr_text) / (sizeof (char *)) + 1;


void *libca = NULL;
EXPORTAPI unsigned short dbr_size[LAST_BUFFER_TYPE+1];
EXPORTAPI unsigned short dbr_value_size[LAST_BUFFER_TYPE+1];
EXPORTAPI unsigned short dbr_value_offset[LAST_BUFFER_TYPE+1];

#ifdef _WIN32
BOOL WINAPI DllMain(HINSTANCE hinstDLL, DWORD fdwReason, LPVOID lpvReserved)
{
    char buffer[100];
    unsigned short * array;
    int i;

    if (libca== NULL && fdwReason == DLL_PROCESS_ATTACH) {
        libca = load_library("ca.dll");

        if (libca == NULL) {
            FormatMessage(
                    FORMAT_MESSAGE_FROM_SYSTEM,
                    NULL,
                    GetLastError(),
                    0,
                    buffer,
                    sizeof(buffer)-1,
                    NULL);
            printf("%s\n", buffer);
            return FALSE;
        }

        array = (unsigned short *)find_symbol(libca, "dbr_size");
        for (i=0; i<= LAST_BUFFER_TYPE; i++)
            dbr_size[i] = array[i];

        array = (unsigned short *)find_symbol(libca, "dbr_value_size");
        for (i=0; i<= LAST_BUFFER_TYPE; i++)
            dbr_value_size[i] = array[i];


        array = (unsigned short *)find_symbol(libca, "dbr_value_offset");
        for (i=0; i<= LAST_BUFFER_TYPE; i++)
            dbr_value_offset[i] = array[i];

        return TRUE;
    }
}
#else
__attribute__((constructor)) void load_ca(void) {
    unsigned short * array;
    int i;
    
    libca = load_library("libca.so");

    array = (unsigned short *)find_symbol(libca, "dbr_size");
    for (i=0; i<= LAST_BUFFER_TYPE; i++)
        dbr_size[i] = array[i];

    array = (unsigned short *)find_symbol(libca, "dbr_value_size");
    for (i=0; i<= LAST_BUFFER_TYPE; i++)
        dbr_value_size[i] = array[i];


    array = (unsigned short *)find_symbol(libca, "dbr_value_offset");
    for (i=0; i<= LAST_BUFFER_TYPE; i++)
        dbr_value_offset[i] = array[i];
}
#endif

typedef void *chid;
typedef chid                    chanId; /* for when the structures field name is "chid" */
typedef long                    chtype;
typedef void  *evid;
typedef double                  ca_real;

/* arguments passed to user connection handlers */
struct  connection_handler_args {
    chanId  chid;  /* channel id */
    long    op;    /* one of CA_OP_CONN_UP or CA_OP_CONN_DOWN */
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

typedef unsigned CA_SYNC_GID;

typedef unsigned capri; 

/*
 *  External OP codes for CA operations
 */
#define CA_OP_GET             0
#define CA_OP_PUT             1
#define CA_OP_CREATE_CHANNEL  2
#define CA_OP_ADD_EVENT       3
#define CA_OP_CLEAR_EVENT     4
#define CA_OP_OTHER           5

/* 
 * used with connection_handler_args 
 */
#define CA_OP_CONN_UP       6
#define CA_OP_CONN_DOWN     7

/* depricated */
#define CA_OP_SEARCH        2


/*
 * Context
 */
enum ca_preemptive_callback_select 
{ ca_disable_preemptive_callback, ca_enable_preemptive_callback };

EXPORTAPI int ca_context_create (enum ca_preemptive_callback_select select)
{
    static int(*pFunc)(enum ca_preemptive_callback_select) = NULL;
    
    if (pFunc == NULL)
        pFunc = find_symbol(libca, "ca_context_create");

    return pFunc(select);
}

EXPORTAPI void ca_context_destroy ()
{
    static void(*pFunc)() = NULL;
    
    if (pFunc == NULL)
        pFunc = find_symbol(libca, "ca_context_destroy");

    pFunc();
}

EXPORTAPI void ca_detach_context ()
{
    static void(*pFunc)() = NULL;
    
    if (pFunc == NULL)
        pFunc = find_symbol(libca, "ca_detach_context");

    pFunc();
}

EXPORTAPI struct ca_client_context * ca_current_context ()
{
    static struct ca_client_context*(*pFunc)() = NULL;

    if (pFunc == NULL)
        pFunc = find_symbol(libca, "ca_current_context");

    return pFunc();
}

EXPORTAPI int ca_attach_context( struct ca_client_context * context)
{
    static int(*pFunc)(struct ca_client_context *) = NULL;

    if (pFunc == NULL)
        pFunc = find_symbol(libca, "ca_attach_context");

    return pFunc(context);
}

EXPORTAPI int ca_context_status (struct ca_client_context * context, unsigned level)
{
    static int(*pFunc)(struct ca_client_context *, unsigned) = NULL;

    if (pFunc == NULL)
        pFunc = find_symbol(libca, "ca_context_status");

    return pFunc(context, level);
}

/*
 * Channel
 */
EXPORTAPI int ca_create_channel
(
        const char     *PROCESS_VARIABLE_NAME, 
        caCh           *USERFUNC, 
        void           *PUSER,
        capri          priority,
        chid           *PCHID
) {
    static int(*pFunc)(const char *, caCh *, void *, capri, chid *) = NULL;
    
    if (pFunc == NULL)
        pFunc = find_symbol(libca, "ca_create_channel");

    return pFunc(PROCESS_VARIABLE_NAME, USERFUNC, PUSER, priority, PCHID);
}

EXPORTAPI int ca_change_connection_event
(
     chid       chan,
     caCh *     pfunc
) {
    static int(*pFunc)(chid, caCh *) = NULL;

    if (pFunc == NULL)
        pFunc = find_symbol(libca, "ca_change_connection_event");

    return pFunc(chan, pfunc);
}

EXPORTAPI int ca_replace_access_rights_event (
     chid   chan,
     caArh  *pfunc
) {
    static int(*pFunc)(chid, caArh *) = NULL;

    if (pFunc == NULL)
        pFunc = find_symbol(libca, "ca_replace_access_rights_event");

    return pFunc(chan, pfunc);
}

typedef void caExceptionHandler (struct exception_handler_args);
EXPORTAPI int ca_add_exception_event
(
     caExceptionHandler *pfunc,
     void               *pArg
) {
    static int(*pFunc)(caExceptionHandler *, void *) = NULL;

    if (pFunc == NULL)
        pFunc = find_symbol(libca, "ca_add_exception_event");

    return pFunc(pfunc, pArg);
}

EXPORTAPI int ca_clear_channel
(
     chid   chanId
) {
    static int(*pFunc)(chid) = NULL;

    if (pFunc == NULL)
        pFunc = find_symbol(libca, "ca_clear_channel");

    return pFunc(chanId);
}

EXPORTAPI int ca_array_put
(
     chtype         type,   
     unsigned long  count,   
     chid           chanId,
     const void *   pValue
) {
    static int(*pFunc)(chtype, unsigned long, chid, const void *) = NULL;

    if (pFunc == NULL)
        pFunc = find_symbol(libca, "ca_array_put");

    return pFunc(type, count, chanId, pValue);
}

EXPORTAPI int ca_array_put_callback
(
     chtype                 type,   
     unsigned long          count,   
     chid                   chanId,
     const void *           pValue,
     caEventCallBackFunc *  pfunc,
     void *                 pArg
) {
    static int(*pFunc)(chtype, unsigned long, chid, const void *, caEventCallBackFunc *, void *) = NULL;

    if (pFunc == NULL)
        pFunc = find_symbol(libca, "ca_array_put_callback");

    return pFunc(type, count, chanId, pValue, pfunc, pArg);
}

EXPORTAPI int ca_array_get
(
     chtype         type,   
     unsigned long  count,   
     chid           chanId,
     void *         pValue
) {
    static int(*pFunc)(chtype, unsigned long, chid, void *) = NULL;

    if (pFunc == NULL)
        pFunc = find_symbol(libca, "ca_array_get");

    return pFunc(type, count, chanId, pValue);
}

EXPORTAPI int ca_array_get_callback
(
     chtype                 type,   
     unsigned long          count,   
     chid                   chanId,
     caEventCallBackFunc *  pfunc,
     void *                 pArg
) {
    static int(*pFunc)(chtype, unsigned long, chid, caEventCallBackFunc *, void *) = NULL;

    if (pFunc == NULL)
        pFunc = find_symbol(libca, "ca_array_get_callback");

    return pFunc(type, count, chanId, pfunc, pArg);
}

EXPORTAPI int ca_create_subscription
(
     chtype                 type,   
     unsigned long          count,   
     chid                   chanId,
     long                   mask,
     caEventCallBackFunc *  pfunc,
     void *                 pArg,
     evid *                 pEventID
) {
    static int(*pFunc)(chtype, unsigned long, chid, long, caEventCallBackFunc *, void *, evid *) = NULL;

    if (pFunc == NULL)
        pFunc = find_symbol(libca, "ca_create_subscription");

    return pFunc(type, count, chanId, mask, pfunc, pArg, pEventID);
}

EXPORTAPI int ca_clear_subscription( evid eventID ) {
    static int(*pFunc)(evid) = NULL;

    if (pFunc == NULL)
        pFunc = find_symbol(libca, "ca_clear_subscription");

    return pFunc(eventID);
}

EXPORTAPI chid ca_evid_to_chid ( evid id ) 
{
    static chid(*pFunc)(evid) = NULL;

    if (pFunc == NULL)
        pFunc = find_symbol(libca, "ca_evid_to_chid");

    return pFunc(id);
}

/*
 * Operation
 */
EXPORTAPI int ca_pend_event(ca_real timeOut)
{
    static int(*pFunc)(ca_real) = NULL;

    if (pFunc == NULL)
        pFunc = find_symbol(libca, "ca_pend_event");

    return pFunc(timeOut);
}

EXPORTAPI int ca_pend_io(ca_real timeOut)
{
    static int(*pFunc)(ca_real) = NULL;

    if (pFunc == NULL)
        pFunc = find_symbol(libca, "ca_pend_io");

    return pFunc(timeOut);
}

EXPORTAPI int ca_pend(ca_real timeOut, int early)
{
    static int(*pFunc)(ca_real, int) = NULL;

    if (pFunc == NULL)
        pFunc = find_symbol(libca, "ca_pend");

    return pFunc(timeOut, early);
}

EXPORTAPI int ca_flush_io()
{
    static int(*pFunc)() = NULL;

    if (pFunc == NULL)
        pFunc = find_symbol(libca, "ca_flush_io");

    return pFunc();
}
/*
 * Information
 */
EXPORTAPI short ca_field_type (chid chan)
{
    static short(*pFunc)(chid) = NULL;

    if (pFunc == NULL)
        pFunc = find_symbol(libca, "ca_field_type");

    return pFunc(chan);
}

EXPORTAPI unsigned long ca_element_count (chid chan)
{
    static unsigned long(*pFunc)(chid) = NULL;

    if (pFunc == NULL)
        pFunc = find_symbol(libca, "ca_element_count");

    return pFunc(chan);
}

EXPORTAPI const char * ca_name (chid chan)
{
    static char *(*pFunc)(chid) = NULL;

    if (pFunc == NULL)
        pFunc = find_symbol(libca, "ca_name");

    return pFunc(chan);
}

EXPORTAPI void ca_set_puser (chid chan, void *puser)
{
    static void(*pFunc)(chid, void *) = NULL;

    if (pFunc == NULL)
        pFunc = find_symbol(libca, "ca_set_puser");

    pFunc(chan, puser);
}

EXPORTAPI void * ca_puser (chid chan)
{
    static void *(*pFunc)(chid) = NULL;

    if (pFunc == NULL)
        pFunc = find_symbol(libca, "ca_puser");

    return pFunc(chan);
}

EXPORTAPI unsigned ca_read_access (chid chan)
{
    static unsigned(*pFunc)(chid) = NULL;

    if (pFunc == NULL)
        pFunc = find_symbol(libca, "ca_read_access");

    return pFunc(chan);
}


EXPORTAPI unsigned ca_write_access (chid chan)
{
    static unsigned(*pFunc)(chid) = NULL;

    if (pFunc == NULL)
        pFunc = find_symbol(libca, "ca_write_access");

    return pFunc(chan);
}


enum channel_state {cs_never_conn, cs_prev_conn, cs_conn, cs_closed};
EXPORTAPI enum channel_state ca_state (chid chan)
{
    static enum channel_state (*pFunc)(chid) = NULL;

    if (pFunc == NULL)
        pFunc = find_symbol(libca, "ca_state");

    return pFunc(chan);
}

EXPORTAPI unsigned ca_get_host_name ( chid pChan, char *pBuf, unsigned bufLength )
{
    static unsigned(*pFunc)(chid, char*, unsigned) = NULL;

    if (pFunc == NULL)
        pFunc = find_symbol(libca, "ca_get_host_name");

    return pFunc(pChan, pBuf, bufLength);
}

EXPORTAPI const char * ca_message(long ca_status)
{
    static const char *(*pFunc)(long) = NULL;

    if (pFunc == NULL)
        pFunc = find_symbol(libca, "ca_message");

    return pFunc(ca_status);
}
