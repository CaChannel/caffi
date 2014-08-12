Module :mod:`caffi.ca`
======================

.. automodule:: caffi.ca

Context
----------
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
.. autofunction:: pend_io
.. autofunction:: pend_event
.. autofunction:: poll
.. autofunction:: flush_io

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


Module :mod:`caffi.dbr`
=======================

.. module:: caffi.dbr

.. autoclass:: DBF

.. autoclass:: DBR

.. autoclass:: DBRValue

    .. automethod:: get

.. autofunction:: format_dbr


Module :mod:`caffi.constants`
=============================

.. automodule:: caffi.constants

.. autoclass:: ChannelState

.. autoclass:: CA_OP

.. autoclass:: ECA

.. autoclass:: AlarmSeverity

.. autoclass:: AlarmCondition
