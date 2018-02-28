"""
File name: ipc.py
Author: Maciej Bedra

Simple Discord IPC wrapper that gives opportunity 
to use Discord Rich Presence for example.
"""

import json
import logging
import os
import os_dependencies
import payloads
import platform
import socket
import struct
import sys

# Configuring logger
logging.basicConfig(format = "%(asctime)s: %(levelname)s: %(message)s", datefmt = "%d.%m.%Y (%H:%M:%S)", level = logging.DEBUG)
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
		self.pipe = self.get_system_property()
		self.is_connected = False
		self.soc = None
		self.pid = os.getpid()

	def get_system_property(self):
		"""
		Recognizing running OS on user platform and searching for path
		to Discord IPC socket. Supported platforms: Windows, Linux, MacOS.

		:returns: path to Discord IPC socket
		:rtype: string
		"""

		pipe = None # variable for Discord IPC socket path
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
				pipe = os_dependencies.localizations["windows"] + "\\" + os_dependencies.socket_name["discord"]
			else:
				for path in os_dependencies.localizations["unix"]:
					if os.environ.get(path, None) != None:
						pipe = os.environ.get(path) + "/" + os_dependencies.socket_name["discord"]
						break

				if pipe == None:
					pipe = "/tmp" + os_dependencies.socket_name["discord"]

			logger.info("Discord IPC socket found")
			logger.debug("Discord IPC socket path: " + pipe)

		else:
			# If platform is not supported, end program
			logger.info("Unsupported OS")
			sys.exit()

		return pipe

	def connect(self):
		"""
		Method that attempts establish connection to Discord.
		"""

		# If there is no connection
		if not self.is_connected:
			logger.info("Trying to connect to Discord...")
			# Open network socket
			self.soc = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
			# Connect via pipe
			self.soc.connect(self.pipe)
			logger.info("Connection command executed")
			# Firstly try to handshake
			self.handshake()
		else:
			logger.info("Already connected")

	def handshake(self):
		"""
		Handshaking with Discord (negotiation between two 
		communicating participants).
		"""

		logger.info("Handshaking with Discord...")
		# Get payload template and rewrite empty client ID
		payloads.handshake["client_id"] = self.client_id
		self.send_data(0, payloads.handshake)

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