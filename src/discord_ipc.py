"""
File name: discord_ipc.py
Author: Maciej Bedra

Simple Discord IPC wrapper that gives opportunity 
to use Discord Rich Presence.
"""

import json
import logging
import os
import os_dependencies
import payloads
import platform
import struct
import sys
import threading
import time
import uuid

logger = logging.getLogger(__name__)
logging.basicConfig(format = "%(asctime)s: [%(levelname)s]: %(message)s", datefmt = "%d.%m.%Y (%H:%M:%S)", level = logging.DEBUG)

class DiscordIPC:
	"""
	Connecting to Discord app installed locally,
	sending commands, handling responses.
	"""

	def __init__(self, client_id):
		"""
		DiscordIPC constructor.

		:param client_id: unique Discord client ID generated on 
		Discord website (developers section)
		:type client_id: string
		"""

		try:
			self.system_name = self.get_system_name()
		except Exception:
			logger.warning("Unsupported OS")
			sys.exit(1)

		self.client_id = client_id
		self.is_connected = False
		self.start_activity_time = None
		self.pipe = None
		self.ipc_socket = self.get_ipc_socket()
		self.pid = os.getpid()

	def get_current_time(self):
		"""
		Get current time from system clock.

		:returns: current time from system clock in seconds
		:rtype: float
		"""

		return time.time()

	def get_ipc_socket(self):
		"""
		Searching for Discord IPC socket. Different localizations
		to search for on different platforms.

		:returns: path to Discord IPC socket
		:rtype: string
		"""

		logger.info("Searching for Discord IPC socket...")
		ipc_socket = None

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

	def get_system_name(self):
		"""
		Getting system name and checking if running OS
		is supported. Supported OS: Windows, Linux MacOS.

		:returns: running OS name (lowercase)
		:rtype: string
		:raise Exception: if running OS is not included in supported
		OS list, raise the Exception
		"""

		logger.info("Recognizing running OS...")
		system_name = platform.system()
		logger.info("Running OS: " + system_name)
		system_name = system_name.lower()
		
		if system_name in os_dependencies.supported:
			logger.info("Supported OS")
			return system_name
		else:
			raise Exception("Unsupported OS")

	def connect(self):
		"""
		Trying to connect to Discord. Connection will be
		established only when handshake (initial message 
		from client and response from Discord) passes.
		"""

		if not self.is_connected:
			logger.info("Trying to connect to Discord...")
			
			try:
				self.pipe = open(self.ipc_socket, "w+b")
			except Exception:
				logger.error("Cannot connect to Discord (probably Discord app is not opened)")
				sys.exit(1)

			logger.info("Trying to handshake with Discord...")
			payloads.handshake["client_id"] = self.client_id
			self.send_data(0, payloads.handshake)
			self.read_data()
			self.is_connected = True
			self.start_activity_time = self.get_current_time()
			logger.info("Connection with Discord established")
		else:
			logger.warning("Already connected to Discord")

	def disconnect(self):
		"""
		Disconnecting from Discord by sending close 
		signal to Discord and closing pipe connection.
		"""

		logger.info("Disconnecting from Discord...")
		self.send_data(2, {})
		self.pipe.close()
		self.is_connected = False
		self.start_activity_time = None
		logger.info("Disconnected")

	def read_data(self):
		"""
		Reciving and decoding data from Discord.
		"""

		logger.info("Getting data from Discord...")

		try:
			encoded_header = b""
			header_remaining_size = 8

			while header_remaining_size:
				encoded_header += self.pipe.read(header_remaining_size)
				header_remaining_size -= len(encoded_header)

			decoded_header = struct.unpack("<ii", encoded_header)
			encoded_data = b""
			packet_remaining_size = int(decoded_header[1])

			while packet_remaining_size:
				encoded_data += self.pipe.read(packet_remaining_size)
				packet_remaining_size -= len(encoded_data)

			logger.info("Data recived")
			logger.debug("Recived data: " + str(encoded_header) + str(encoded_data))
			logger.info("Decodnig recived data...")
			decoded_data = json.loads(encoded_data.decode("utf-8"))
			logger.info("Recived data decoded")
			logger.debug("Decoded data: (" + str(decoded_header[0]) + ", " + str(decoded_header[1]) + str(decoded_data))
		except Exception:
			logger.error("Cannot get data from Discord")
			sys.exit(1)

	def send_data(self, opcode, payload):
		"""
		Encoding data to send and sending
		encoded data to Discord app via
		Discord IPC socket.

		:param opcode: Discord opcode that defines payload type
		:type opcode: int
		:param payload: data that will be send to Discord app
		(Discord commands) in proper appearance described
		on Discord website (developers section)
		:type payload: string
		"""

		logger.info("Trying to send payload to Discord...")
		logger.debug("Orginal data: (" + str(opcode) + ", " + str(len(payload)) + ")" + str(payload))
		logger.info("Encoding data to send...")
		payload = json.dumps(payload)
		encoded_data = struct.pack("<ii", opcode, len(payload)) + payload.encode("utf-8")
		logger.info("Data encoded")
		logger.debug("Encoded data: " + str(encoded_data))

		try:
			self.pipe.write(encoded_data)
			self.pipe.flush()
			logger.info("Data sent")
		except Exception:
			logger.error("Cannot send data to Discord")
			sys.exit(1)

	def send_complex_rich_presence(self, large_text, large_image, small_text, small_image, activity_details, activity_state):
		"""
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
		self.read_data()

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
		self.read_data()