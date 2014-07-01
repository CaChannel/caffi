Channel Access Guidelines
=========================
.. note:: The original text is from `Channel Access Reference Manual <http://www.aps.anl.gov/epics/base/R3-15/0-docs/CAref.html>`_
         But C function names are adapted to Python functions.


Flushing and Blocking
---------------------
Significant performance gains can be realized when the CA client library doesn't wait for
a response to return from the server after each request.
All requests which require interaction with a CA server are accumulated (buffered) and not forwarded to the IOC
until one of :func:`caffi.ca.flush_io`, :func:`caffi.ca.pend_io`, :func:`caffi.ca.pend_event`, or :func:`caffi.ca.sg_pend`
are called allowing several operations to be efficiently sent over the network together.


Status Codes
------------
If successful, the functions return the status code ECA_NORMAL.
Unsuccessful status codes returned from the client library are listed with each function.

Operations that appear to be valid to the client can still fail in the server.
Writing the string "off" to a floating point field is an example of this type of error.
If the server for a channel is located in a different address space than the client then
the operations that communicate with the server return status indicating the validity of the request and
whether it was successfully enqueued to the server, but communication of completion status is deferred
until a user callback is called, or lacking that an exception handler is called.



User Supplied Callback Functions
--------------------------------
Certain CA client initiated requests asynchronously execute an application supplied call back in the client process
when a response arrives. The functions :func:`caffi.ca.put`, :func:`caffi.ca.get` and :func:`caffi.ca.create_subscription`
all request notification of asynchronous completion via this mechanism.

A dict, *epics_arg* and a tuple, *user_arg* are passed to the application supplied callback.
In this dict the *value* field is a dict containing any data that might be returned.
The *status* field will be set to one of the CA error codes and will indicate the status of the operation performed in the IOC.
If the status field isn't set to ECA_NORMAL or data isn't normally returned from the operation (i.e. put call back)
then you should expect that the *value* field will be set to None.
The fields *chid* and *type* are set to the values specified when the request was made by the application.


Channel Access Exceptions
-------------------------
When the server detects a failure, and there is no client call back function attached to the request,
an exception handler is executed in the client.
The default exception handler prints a message on the console and exits if the exception condition is severe.
Certain internal exceptions within the CA client library, and failures detected by the SEVCHK macro may also cause the exception handler to be invoked.
To modify this behavior see :func:`caffi.ca.add_exception_event`.


Server and Client Share the Same Address Space on The Same Host
---------------------------------------------------------------
If the Process Variable's server and it's client are collocated within the same memory address space and the same host
then the operations bypass the server and directly interact with the server tool component (commonly the IOC's function block database).
In this situation the functions frequently return the completion status of the requested operation directly to the caller
with no opportunity for asynchronous notification of failure via an exception handler.
Likewise, callbacks may be directly invoked by the CA library functions that request them.


Arrays
------
For functions that require an argument specifying the number of array elements,
no more than the process variable's maximum native element count may be requested.
The process variable's maximum native element count is available from :func:`caffi.ca.element_count` when the channel is connected.
If fewer elements than the process variable's native element count are requested, the requested values will be fetched beginning at element zero.
By default CA limits the number of elements in an array to be no more than approximately 16k divided by the size of one element in the array.
The maximum array size may be configured in the client and in the server, by setting *EPICS_CA_MAX_ARRAY_BYTES*


Connection Management
---------------------
Application programs should assume that CA servers may be restarted, and that network connectivity is transient.
When you create a CA channel its initial connection state will most commonly be disconnected.
If the Process Variable's server is available the library will immediately initiate the necessary actions to make a connection with it.
Otherwise, the client library will monitor the state of servers on the network and
connect or reconnect with the process variable's server as it becomes available.
After the channel connects the application program can freely perform IO operations through the channel,
but should expect that the channel might disconnect at any time due to network connectivity disruptions or server restarts.

Three methods can be used to determine if a channel is connected: the application program might call :func:`caffi.ca.state`
to obtain the current connection state, block in :func:`caffi.ca.pend_io` until the channel connects,
or install a connection callback handler when it calls :func:`caffi.ca.create_channel`.
The :func:`caffi.ca.pend_io` approach is best suited to simple command line programs with short runtime duration,
and the connection callback method is best suited to toolkit components with long runtime duration.
Use of :func:`caffi.ca.state` is appropriate only in programs that prefer to poll for connection state changes
instead of opting for asynchronous notification.
The :func:`caffi.ca.pend_io` function blocks only for channels created specifying no callback function.
The user's connection state change function will be run immediately from within :func:`caffi.ca.create_channel`
if the CA client and CA server are both hosted within the same address space (within the same process).



Thread Safety and Preemptive Callback to User Code
--------------------------------------------------
When the client library is initialized the programmer may specify if preemptive callback is to be enabled.
Preemptive callback is disabled by default. If preemptive callback is enabled,
then the user's callback functions might be called by CA's auxiliary threads
when the main initiating channel access thread is not inside of a function in the channel access client library.
Otherwise, the user's callback functions will be called only when the main initiating channel access thread is executing inside of the CA client library.
When the CA client library invokes a user's callback function, it will always wait for the current callback to complete prior to executing another callback function.
Programmers enabling preemptive callback should be familiar with using mutex locks to create a reliable multi-threaded program.
If a GUI toolkit is involved, this means the callback is inside a non GUI thread.
Please refer to your GUI toolkits' document, if you want to update GUI inside the callback.


CA Client Contexts and Application Specific Auxiliary Threads
-------------------------------------------------------------
It is often necessary for several CA client side tools running in the same address space (process) to be independent of each other.
For example, the database CA links and the sequencer are designed to not use the same CA client library threads, network circuits, and data structures.
Each thread that calls :func:`caffi.ca.create_context` for the first time either directly or
implicitly when calling any CA library function for the first time, creates a CA client library context.

A CA client library context contains all of the threads, network circuits, and data structures required to
connect and communicate with the channels that a CA client application has created.
The priority of auxiliary threads spawned by the CA client library are at fixed offsets from the priority of the thread that called :func:`caffi.ca.create_context`.
An application specific auxiliary thread can join a CA context by calling :func:`caffi.ca.attach_context`
using the CA context identifier that was returned from :func:`caffi.ca.current_context`
when it is called by the thread that created the context which needs to be joined.
A context which is to be joined must be preemptive - it must be created using *create_context(True)*.
It is not possible to attach a thread to a non-preemptive CA context created explicitly or implicitly with *create_context(False)*.
Once a thread has joined with a CA context it need only make ordinary function calls to use the context.

A CA client library context can be shut down and cleaned up,
after destroying any channels or application specific threads that are attached to it, by calling :func:`caffi.ca.destroy_context`.
The context may be created and destroyed by different threads as long as they are both part of the same context.


Polling the CA Client Library From Single Threaded Applications
---------------------------------------------------------------
If preemptive call back is not enabled, then for proper operation CA must periodically be polled to take care of background activity.
This requires that your application must either wait in one of :func:`caffi.ca.pend_event`, :func:`caffi.ca.pend_io`,
or :func:`caffi.ca.sg_block` or alternatively it must call :func:`caffi.ca.poll` at least every 100 milli-seconds.

