OS Dependencies
===============

File that contains expected localizations to 
Discord IPC socket on specific platforms.

===================
Supported platforms
===================

.. code-block:: python

	supported = ["windows", "linux", "darwin"]

==========================================================================
Localizations for specific platforms where Discord IPC socket can be found
==========================================================================

.. code-block:: python

	localizations = {
		"windows": "\\\\?\\pipe",
		"unix": {
			"XDG_RUNTIME_DIR",
			"TMPDIR",
			"TMP",
			"TEMP"
		}
	}

====================
Expected socket name
====================

.. code-block:: python

	socket_name = ["discord-ipc-0"]