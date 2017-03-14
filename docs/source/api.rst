Module :mod:`caffi.ca`
======================

.. automodule:: caffi.ca

Context
-------
.. autofunction:: create_context
.. autofunction:: destroy_context
.. autofunction:: attach_context
.. autofunction:: current_context
.. autofunction:: show_context

Channel
-------
.. autofunction:: create_channel
.. autofunction:: clear_channel

Operation
---------
.. autofunction:: create_subscription
.. autofunction:: clear_subscription
.. autofunction:: get
.. autofunction:: put

Execution
---------
.. autofunction:: pend
.. autofunction:: pend_io
.. autofunction:: pend_event
.. autofunction:: poll
.. autofunction:: flush_io
.. autofunction:: test_io

Information
-----------
.. autofunction:: field_type
.. autofunction:: element_count
.. autofunction:: name
.. autofunction:: state
.. autofunction:: message
.. autofunction:: host_name
.. autofunction:: read_access
.. autofunction:: write_access

Synchronous
-----------
.. autofunction:: sg_create
.. autofunction:: sg_delete
.. autofunction:: sg_get
.. autofunction:: sg_put
.. autofunction:: sg_block
.. autofunction:: sg_test
.. autofunction:: sg_reset

Misc
----
.. autofunction:: add_exception_event
.. autofunction:: replace_access_rights_event


Module :mod:`caffi.dbr`
=======================

.. module:: caffi.dbr

.. autoclass:: DBF
   :inherited-members:

    .. automethod:: toSTS
    .. automethod:: toTIME
    .. automethod:: toGR
    .. automethod:: toCTRL

.. autoclass:: DBR

    .. automethod:: isSTRING
    .. automethod:: isSHORT
    .. automethod:: isFLOAT
    .. automethod:: isENUM
    .. automethod:: isCHAR
    .. automethod:: isLONG
    .. automethod:: isDOUBLE
    .. automethod:: isPlain
    .. automethod:: isSTS
    .. automethod:: isTIME
    .. automethod:: isGR
    .. automethod:: isCTRL

.. autoclass:: DBRValue

    .. automethod:: get

.. autofunction:: format_dbr


Module :mod:`caffi.constants`
=============================

.. automodule:: caffi.constants

.. autoclass:: ChannelState
   :inherited-members:

.. autoclass:: DBE
   :inherited-members:

.. autoclass:: CA_PRIORITY

.. autoclass:: CA_OP
   :inherited-members:

.. autoclass:: ECA
   :inherited-members:

   .. automethod:: message

.. autoclass:: AlarmSeverity

.. autoclass:: AlarmCondition
