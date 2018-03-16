Discord Rich Presence Client
============================

Main entry point.

.. py:function:: main()

	Short example how to set Discord Rich Presence 
	via Discord IPC wrapper.

	Create instance of DiscordIPC class. Where **ClientID** paste your token generated on Discord website (developers section).

	.. code-block:: python

		ipc = discord_ipc.DiscordIPC("ClientID")

	Connect to Discord.

	.. code-block:: python

		ipc.connect()

	Send Discord Rich Presence status to Discord just change method parameters.

	.. code-block:: python

		# activity_details = description of main user activity
		# activity_state = additional description of user activity
		ipc.send_simple_rich_presence("activity_details", "activity_state")

	There is also support for complex Discord Rich Presence payload (changing images, not only texts).

	.. code-block:: python

		# Replace line:
		# ipc.send_simple_rich_presence("activity_details", "activity_state") #
		# with:
		# ipc.send_complex_rich_presence("large_text", "large_image", "small_text", "small_image", "activity_details", "activity_state") #
		# large_text = text that will be displayed on large image hover
		# large_image = name of large image file, seted on Discord developers website (will display as application logo)
		# small_text = text that will be displayed on small image hover
		# small_image = name of small image file, seted on Discord developers website (will display in right bottom corner of large image)
		# activity_details = description of main user activity
		# activity_state = additional description of user activity

	Give program some time to see the changes in Discord.

	.. code-block:: python

		time.sleep(30)

	Disconnect from Discord.

	.. code-block:: python

		ipc.disconnect()