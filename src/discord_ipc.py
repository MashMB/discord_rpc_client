"""
File name: discord_ipc.py
Author: Maciej Bedra

Simple Discord IPC wrapper that gives opportunity 
to use Discord Rich Presence for example.
"""

import asyncio
import json
import logging
import os
import os_dependencies
import payloads
import platform
import struct
import sys
import time
import threading
import uuid

# Configuring logger
logger_level = "INFO" # DEBUG or INFO

logger = logging.getLogger(__name__)

# logging.DEBUG level will be used to analyse errors
# it will generate file with logs for developer to fix bugs
# do not use logging.DEBUG level if it is not necessary
if logger_level == "DEBUG":
	logger.setLevel(logging.DEBUG)
	handler = logging.FileHandler("discord_ipc.log")
	handler.setLevel(logging.DEBUG)
	log_format = logging.Formatter("%(asctime)s: [%(levelname)s]: %(message)s", datefmt = "%d.%m.%Y (%H:%M:%S)")
	handler.setFormatter(log_format)
	logger.addHandler(handler)
else:
	logging.basicConfig(format = "%(asctime)s: [%(levelname)s]: %(message)s", datefmt = "%d.%m.%Y (%H:%M:%S)", level = logging.INFO)

class DiscordIPC:
	"""
	Connecting to Discord app installed locally,
	sending commands, handling responses.
	"""

	def __init__(self, client_id):
		"""
		DiscordIPC constructor.

		:param client_id: unique Discord client ID generated 
		for application created in Discord web panel for developers
		:type client_id: string
		"""

		self.client_id = client_id
		self.is_connected = False
		self.system_name = self.get_system_name()
		self.ipc_socket = self.get_ipc_socket()
		self.pid = os.getpid()
		self.discord_listener = threading.Thread(name = "discord_listener", target = self.keep_conncetion_alive)
		self.start_activity_time = None
		self.event_loop = None
		self.pipe_writer = None
		self.pipe_reader = None

	def get_current_time(self):
		"""
		Get current time from system clock.

		:returns: current time from system clock in seconds
		:rtype: float
		"""

		return time.time()

	def get_system_name(self):
		"""
		Getting system name and checking 
		if running OS is supported. Supported OS:
		Windows, Linux, MacOS.

		:returns: running OS name (lowercase)
		:rtype: string
		"""

		logger.info("Recognizing running OS...")
		# Get system name
		system_name = platform.system()
		logger.info("Running OS: " + system_name)
		# Format system name string for next operations
		system_name = system_name.lower()

		# If OS is supported, return name
		if system_name in os_dependencies.supported:
			return system_name
		else:
			# Unsupported OS warning for user
			logger.warning("Unsupported OS")
			sys.exit()

	def get_ipc_socket(self):
		"""
		Searching for Discord IPC socket. Different localizations
		to search for on different platforms.

		:returns: path to Discord IPC socket
		:rtype: string
		"""

		logger.info("Searching for Discord IPC socket...")
		ipc_socket = None # Variable for path to Discord IPC socket

		# Different Discord IPC socket localization on different platforms
		if self.system_name == os_dependencies.supported[0]:
			ipc_socket = os_dependencies.localizations["windows"] + "\\" + os_dependencies.socket_name[0]
		else:
			for path in os_dependencies.localizations["unix"]:
					if os.environ.get(path, None) != None:
						ipc_socket = os.environ.get(path) + "/" + os_dependencies.socket_name[0]
						break

			if ipc_socket == None:
				ipc_socket = "/tmp" + os_dependencies.socket_name[0]

		logger.info("Discord IPC socket found")
		logger.debug("Path to Discord IPC socket: " + ipc_socket)

		return ipc_socket

	def generate_uuid(self):
		"""
		Generating unique uuid.

		:returns: unique uuid
		:rtype: uuid
		"""

		return uuid.uuid4()

	def connect(self):
		"""
		Trying connect to Discord. Connection is established
		when Discord recives initial message and responses
		for the message.
		"""

		if not self.is_connected:

			try:
				logger.info("Trying connect to Discord...")
				# Start activity timer when trying to connect to Discord
				self.start_activity_time = self.get_current_time()

				# Create main event loop
				if self.system_name == os_dependencies.supported[0]:
					self.event_loop = asyncio.ProactorEventLoop()
				else:
					self.event_loop = asyncio.get_event_loop()

				# Send inital message and wait for response
				self.event_loop.run_until_complete(self.handshake())
				# Keep connection alive when handshake passes
				self.discord_listener.start()
				logger.info("Keeping connection alive...")
			except Exception:
				logger.error("Can not connect to Discord (probably Discord app is not opened)")
				sys.exit()
				
		else:
			logger.warning("Already connected to Discord")

	def disconnect(self):
		"""
		Disconnecting from Discord by terminating
		asynchronous methods and Thread that
		keeps connection alive, reseting all components.
		"""

		logger.info("Disconnecting from Discord...")
		self.pipe_writer.close()
		self.event_loop.run_until_complete(self.proper_close())
		self.event_loop.close()
		self.is_connected = False
		self.pipe_writer = None
		self.pipe_reader = None
		self.event_loop = None
		self.start_activity_time = None
		logger.info("Disconncted")

	async def handshake(self):
		"""
		Handshaking with Discord (negotiation between two 
		communicating participants) in asynchronous way.
		"""

		logger.info("Trying to handshake with Discord...")

		# Different pipe support on different platform
		if self.system_name == os_dependencies.supported[0]:
			logger.debug("Creating pipe connection with Discord IPC socket...")
			self.pipe_reader = asyncio.StreamReader(loop = self.event_loop)
			self.pipe_writer, protocol = await self.event_loop.create_pipe_connection(lambda: asyncio.StreamReaderProtocol(self.pipe_reader, loop = self.event_loop), self.ipc_socket)
		else:
			logger.debug("Openning unix connection with Discord IPC socket...")
			self.pipe_reader, self.pipe_writer = await asyncio.open_unix_connection(self.ipc_socket, loop = self.event_loop)

		payloads.handshake["client_id"] = self.client_id
		# Sending initial payload
		self.send_data(0, payloads.handshake)
		# Connection is established only if Discord app responses for initial payload
		await self.read_data()
		self.is_connected = True
		logger.info("Connection with Discord established")

	def keep_conncetion_alive(self):
		"""
		Keeping connection alive. No timeout
		functions for fast terminating.
		"""

		while self.is_connected:
			pass

	async def proper_close(self):
		"""
		Using asyncio.ProactorEventLoop() on Windows
		causes some errors while terminationg pipe connection and
		after that immediately closing main event loop. This
		easy hack repairs it.
		"""

		pass

	async def read_data(self):
		"""
		Reciving and decoding data from Discord
		in asynchronous way.
		"""

		logger.info("Getting data from Discord...")

		try:
			# Read data from Discord IPC socket
			recived_data = await self.pipe_reader.read(1024)
			logger.info("Data recived")
			logger.debug("Recived data: " + str(recived_data))
			logger.info("Decoding recived data...")
			decoded_header = struct.unpack("<ii", recived_data[:8])
			# Decoding data in json format
			decoded_data = json.loads(recived_data[8:].decode("utf-8"))
			logger.info("Recived data decoded")
			logger.debug("Decoded data: " + "(" + str(decoded_header[0]) + ", " + str(decoded_header[1]) + ")" + str(decoded_data))
		except Exception:
			logger.error("Cannot get data from Discord")

	def send_data(self, opcode, payload):
		"""
		Encoding data to send and 
		sending encoded data to Discord app
		via Discord IPC socket.

		:param opcode: Discord opcode that defines payload type
		:type op: int
		:param payload: data that will be send to Discord app
		(Discord commands) in proper appearance described
		on Discord website - developers section
		:type payload: string
		"""

		logger.info("Trying to send payload to Discord...")
		logger.debug("Orginal data: " + "(" + str(opcode) + ", " + str(len(payload)) + ")" + str(payload))
		logger.info("Encoding data to send...")
		# Payload in json appearance
		payload = json.dumps(payload)
		# Encoding packet with header creation
		encoded_data = struct.pack("<ii", opcode, len(payload)) + payload.encode("utf-8")
		logger.info("Data encoded")
		logger.debug("Encoded data: " + str(encoded_data))
		self.pipe_writer.write(encoded_data)
		logger.info("Data sent")

	def send_simple_rich_presence(self, activity_details, activity_state):
		"""
		Creating and sending simple Discord Rich Presence payload to Discord.

		:param activity_details: main description of activity
		:type activity_details: string
		:param activity_state: additional description of activity
		:type activity_state: string
		"""
		
		logger.info("Creating Discord Rich Presence payload...")

		# Setting start time for Discord Rich Presence timer
		payloads.rpc_timestamps["start"] = self.start_activity_time

		# Setting user activity details
		payloads.rpc_simple_activity["details"] = activity_details
		payloads.rpc_simple_activity["state"] = activity_state

		# Setting proper activity type for payload args
		payloads.rpc_args["activity"] = payloads.rpc_simple_activity

		# Setting pid of running process
		payloads.rpc_args["pid"] = self.pid

		# Setting unique uuid for payload
		id = str(self.generate_uuid())
		payloads.rpc["nonce"] = id

		logger.info("Payload created")

		# Sending ready Discord Rich Presence payload
		self.send_data(1, payloads.rpc)
		self.event_loop.run_until_complete(self.read_data())

	def send_complex_rich_presence(self, large_text, large_image, small_text, small_image, activity_details, activity_state):
		"""
		Creating and sending complex (full) Discord Rich Presence payload to Discord.

		:param large_text: text to display when large image is hovered
		:type large_text: string
		:param large_image: name of large image asset seted on Discord developers website
		:type large_image: string
		:param small_text: text to display when small image is hovered
		:type small_text: string
		:param small_image: name of small image asset seted on Discord developers website
		:type small_image: string
		:param activity_details: main description of activity
		:type activity_details: string
		:param activity_state: additional description of activity
		:type activity_state: string
		"""
		
		logger.info("Creating Discord Rich Presence payload...")

		# Setting assets
		payloads.rpc_assets["large_text"] = large_text
		payloads.rpc_assets["large_image"] = large_image
		payloads.rpc_assets["small_text"] = small_text
		payloads.rpc_assets["small_image"] = small_image

		# Setting start time for Discord Rich Presence timer
		payloads.rpc_timestamps["start"] = self.start_activity_time

		# Setting user activity details
		payloads.rpc_complex_activity["details"] = activity_details
		payloads.rpc_complex_activity["state"] = activity_state

		# Setting proper activity type for payload args
		payloads.rpc_args["activity"] = payloads.rpc_complex_activity

		# Setting pid of running process
		payloads.rpc_args["pid"] = self.pid

		# Setting unique uuid for payload
		id = str(self.generate_uuid())
		payloads.rpc["nonce"] = id

		logger.info("Payload created")

		# Sending ready Discord Rich Presence payload
		self.send_data(1, payloads.rpc)
		self.event_loop.run_until_complete(self.read_data())