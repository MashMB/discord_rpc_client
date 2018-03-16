Discord IPC wrapper
===================

Simple Discord IPC wrapper that gives opportunity 
to use Discord Rich Presence.

.. py:class:: DiscordIPC

	Connecting to Discord app installed locally,
	sending commands, handling responses.

	.. py:method:: __init__(self, client_id)

		DiscordIPC constructor.

		:param client_id: unique Discord client ID generated on Discord website (developers section)
		:type client_id: string

	.. py:method:: get_current_time(self)

		Get current time from system clock.

		:returns: current time from system clock in seconds
		:rtype: float

	.. py:method:: get_ipc_socket(self)

		Searching for Discord IPC socket. Different localizations
		to search for on different platforms.

		:returns: path to Discord IPC socket
		:rtype: string

	.. py:method:: generate_uuid(self)

		Generating unique uuid.

		:returns: unique uuid
		:rtype: uuid

	.. py:method:: get_system_name(self)

		Getting system name and checking if running OS
		is supported. Supported OS: Windows, Linux MacOS.

		:returns: running OS name (lowercase)
		:rtype: string
		:raise Exception: if running OS is not included in supported OS list, raise the Exception

	.. py:method:: connect(self)

		Trying to connect to Discord. Connection will be
		established only when handshake (initial message 
		from client and response from Discord) passes.

	.. py:method:: disconnect(self)

		Disconnecting from Discord by sending close 
		signal to Discord and closing pipe connection, 
		reseting varaibles.

	.. py:method:: read_data(self)

		Reciving and decoding data from Discord.

	.. py:method:: send_data(self, opcode, payload)

		Encoding data to send and sending
		encoded data to Discord app via
		Discord IPC socket.

		:param opcode: Discord opcode that defines payload type
		:type opcode: int
		:param payload: data that will be send to Discord app (Discord commands) in proper appearance described on Discord website (developers section)
		:type payload: string

	.. py:method:: send_complex_rich_presence(self, large_text, large_image, small_text, small_image, activity_details, activity_state)

		Creating and sending complex (full) Discord Rich Presence payload to Discord.

		:param large_text: text to display when large image is hovered
		:type large_text: string
		:param large_image: name of large image asset seted on Discord website (developers section)
		:type large_image: string
		:param small_text: text to display when small image is hovered
		:type small_text: string
		:param small_image: name of small image asset seted on Discord website (developers section)
		:type small_image: string
		:param activity_details: main description of activity
		:type activity_details: string
		:param activity_state: additional description of activity
		:type activity_state: string

	.. py:method:: send_simple_rich_presence(self, activity_details, activity_state)

		Creating and sending simple Discord Rich Presence payload to Discord.

		:param activity_details: main description of activity
		:type activity_details: string
		:param activity_state: additional description of activity
		:type activity_state: string