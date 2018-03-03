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
import uuid

# Configuring logger
logging.basicConfig(format = "%(asctime)s: [%(levelname)s]: %(message)s", datefmt = "%d.%m.%Y (%H:%M:%S)", level = logging.DEBUG)
logger = logging.getLogger(__name__)

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
		self.pid = os.getpid()
		self.event_loop = None
		self.ipc_socket = None
		self.pipe_writer = None
		self.pipe_reader = None

	def get_current_time(self):
		"""
		Get current time from system clock.

		:returns: current time from system clock in seconds
		:rtype: float
		"""

		return time.time()

	def get_system_property(self):
		"""
		Recognizing running OS on user platform and searching for path
		to Discord IPC socket. Supported platforms: Windows, Linux, MacOS.

		:returns: path to Discord IPC socket
		:rtype: string
		"""

		pipe = None # Variable for Discord IPC socket path
		logger.info("Recognizing OS...")
		system_name = platform.system() # Getting system name
		logger.info("Running OS: " + system_name)
		system_name = system_name.lower()

		# If platform is supported
		if system_name in os_dependencies.supported:
			logger.info("Supported OS")
			logger.info("Searching for valid Discord IPC socket path...")

			# Other Discord IPC socket localization on different platforms
			if system_name == os_dependencies.supported[0] :
				pipe = os_dependencies.localizations["windows"] + "\\" + os_dependencies.socket_name[0]
			else:
				for path in os_dependencies.localizations["unix"]:
					if os.environ.get(path, None) != None:
						pipe = os.environ.get(path) + "/" + os_dependencies.socket_name[0]
						break

				if pipe == None:
					pipe = "/tmp" + os_dependencies.socket_name[0]

			logger.info("Discord IPC socket found")
			logger.debug("Discord IPC socket path: " + pipe)

		else:
			# If platform is not supported, end program
			logger.info("Unsupported OS")
			sys.exit()

		return pipe

	def generate_uuid(self):
		"""
		Generating unique uuid.

		:returns: unique uuid
		:rtype: uuid
		"""

		return uuid.uuid4()

	def connect(self):
		"""
		Method that attempts establish connection to Discord.
		"""

		# If there is no connection
		if not self.is_connected:
			logger.info("Trying to connect to Discord...")
			# Open network socket
			self.soc = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

			try:
				# Connect via pipe
				self.soc.connect(self.pipe)
				self.is_connected = True
				logger.info("Connection command executed")
				# Firstly try to handshake
				self.handshake()
				# Start listening for messages from Discord
				self.listener.start()
				logger.info("Discord messages listener started")
			except ConnectionRefusedError:
				# If can not connect to Discord, log it
				logger.error("Can not connect to Discord (probably Discord app is not opened)")
				sys.exit()

		else:
			logger.info("Already connected")

	def disconnect(self):
		"""
		Disconnecting from Discord by closing network socket
		and terminating Discord messages listener (thread)
		"""

		logger.info("Trying to disconnect from Discord...")
		# Set connection status
		self.is_connected = False
		# Close socket immediately for sending and reciving data
		self.soc.shutdown(socket.SHUT_RDWR)
		self.soc.close()
		self.soc = None
		logger.debug("Socket closed")
		# Terminate listener Thread
		self.listener.join(1.0)
		logger.debug("Discord messages listener terminated")
		logger.info("Disconnected from Discord")

	def handshake(self):
		"""
		Handshaking with Discord (negotiation between two 
		communicating participants).
		"""

		logger.info("Handshaking with Discord...")
		# Get payload template and rewrite empty client ID
		payloads.handshake["client_id"] = self.client_id
		self.send_data(0, payloads.handshake)

	def read_data(self):
		"""
		Reciving and decoding data from Discord
		via thread to keep connection alive.
		"""

		# Recive date while connection is keep alive
		while self.is_connected:
			try:
				logger.info("Waiting for data from Discord...")
				# Recive data on network socket
				recived_data = self.soc.recv(1024)

				# When recived data is not empty
				if str(recived_data) != "b\'\'":
					logger.info("Data recived")
					logger.debug("Recived encoded data: " + str(recived_data))
					logger.info("Decoding recived data...")
					# Decode packet header
					decoded_header = struct.unpack("<ii", recived_data[:8])
					# Decode packet (json format)
					decoded_data = json.loads(recived_data[8:].decode("utf-8"))
					opcode = decoded_header[0]
					data_length = decoded_header[1]
					logger.debug("Recived decoded data: " + str(opcode) + " " + str(data_length) + repr(decoded_data))
					logger.info("Recived data decoded")
				else:
					logger.info("Waiting for data from Discord timeouted")
			except Exception:
				# There can be exception connected to unpacking data header
				logger.error("Recived data could not be decoded")
				break

	def send_data(self, opcode, payload):
		"""
		Encoding data to send and 
		sending encoded data to Discord app.

		:param op: Discord opcode that defines payload type
		:type op: int
		:param payload: data that will be send to Discord app
		(Discord commands) in proper appearance described
		on Discord website - developers section
		:type payload: string
		"""

		logger.info("Trying to send payload to Discord...")
		payload = json.dumps(payload) # Creating json file format from payload
		logger.info("Creating data to send...")
		# Presenting decoded data to send
		data = str(opcode) + " " + str(len(payload)) + payload
		logger.debug("Data ready to send: " + data)
		logger.info("Encoding data to send...")
		# Encoding data that will be send
		encoded_data = struct.pack("<ii", opcode, len(payload)) + payload.encode()
		logger.debug("Encoded data ready to send: " + str(encoded_data))
		# Sending data via socket created earlier (connect method)
		self.soc.send(encoded_data)
		logger.info("Data sent")

	def send_simple_rich_presence(self, activity_details, activity_state):
		"""
		Creating and sending simple Discord Rich Presence payload to Discord.

		:param activity_details: main description of activity
		:type activity_details: string
		:param activity_state: additional description of activity
		:type activity_state: string
		"""
		
		logger.info("Creating Discord Rich Presence payload")

		# Setting start time for Discord Rich Presence timer
		start_time = self.get_current_time()
		payloads.rpc_timestamps["start"] = start_time
		logger.debug("Payload timestamps -> start: " + str(start_time))

		# Setting user activity details
		payloads.rpc_simple_activity["details"] = activity_details
		logger.debug("Payload activity -> details: " + activity_details)
		payloads.rpc_simple_activity["state"] = activity_state
		logger.debug("Payload activity -> state: " + activity_state)

		# Setting proper activity type for payload args
		payloads.rpc_args["activity"] = payloads.rpc_simple_activity

		# Setting pid of running process
		payloads.rpc_args["pid"] = self.pid
		logger.debug("Payload args -> pid: " + str(self.pid))

		# Setting unique uuid for payload
		id = str(self.generate_uuid())
		payloads.rpc["nonce"] = id
		logger.debug("Payloads rpc -> nonce" + id)

		logger.info("Discord Rich Presence payload created")

		# Sending ready Discord Rich Presence payload
		self.send_data(1, payloads.rpc)

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
		
		logger.info("Creating Discord Rich Presence payload")

		# Setting assets
		payloads.rpc_assets["large_text"] = large_text
		logger.debug("Payload assets -> large_text: " + large_text)
		payloads.rpc_assets["large_image"] = large_image
		logger.debug("Payload assets -> large_image: " + large_image)
		payloads.rpc_assets["small_text"] = small_text
		logger.debug("Payload assets -> small_text: " + small_text)
		payloads.rpc_assets["small_image"] = small_image
		logger.debug("Payload assets -> small_image: " + small_image)

		# Setting start time for Discord Rich Presence timer
		start_time = self.get_current_time()
		payloads.rpc_timestamps["start"] = start_time
		logger.debug("Payload timestamps -> start: " + str(start_time))

		# Setting user activity details
		payloads.rpc_complex_activity["details"] = activity_details
		logger.debug("Payload activity -> details: " + activity_details)
		payloads.rpc_complex_activity["state"] = activity_state
		logger.debug("Payload activity -> state: " + activity_state)

		# Setting proper activity type for payload args
		payloads.rpc_args["activity"] = payloads.rpc_complex_activity

		# Setting pid of running process
		payloads.rpc_args["pid"] = self.pid
		logger.debug("Payload args -> pid: " + str(self.pid))

		# Setting unique uuid for payload
		id = str(self.generate_uuid())
		payloads.rpc["nonce"] = id
		logger.debug("Payloads rpc -> nonce" + id)

		logger.info("Discord Rich Presence payload created")

		# Sending ready Discord Rich Presence payload
		self.send_data(1, payloads.rpc)