Payloads
========

File that contains templates of payloads that
can be send to Discord app via Discrod IPC socket.

================================
Payload template for handshaking
================================

.. code-block:: python

	handshake = {
		"v": 1,
		"client_id": None
	}

====================================
Json template for rpc assets section
====================================

.. code-block:: python

	rpc_assets = {
		"large_text": None,
		"large_image": None,
		"small_text": None,
		"small_image": None
	}

========================================
Json template for rpc timestamps section
========================================

.. code-block:: python

	rpc_timestamps = {
		"start": None
	}

=====================================================
Json template for rpc complex (full) activity section
=====================================================

.. code-block:: python

	rpc_complex_activity = {
		"details": None,
		"state": None,
		"timestamps": rpc_timestamps,
		"assets": rpc_assets
	}

=============================================
Json template for rpc simple activity section
=============================================

.. code-block:: python

	rpc_simple_activity = {
		"details": None,
		"state": None,
		"timestamps": rpc_timestamps
	}

==================================
Json template for rpc args section
==================================

.. code-block:: python

	rpc_args = {
		"activity": None,
		"pid": None
	}

==========================================
Payload template for Discord Rich Presence
==========================================

.. code-block:: python

	rpc = {
		"cmd": "SET_ACTIVITY",
		"args": rpc_args,
		"nonce": None
	}