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
import platform
import sys

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
		self.ipc_socket = self.get_ipc_socket()

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
		encoded_data = struct.pack("<ii" + opcode, len(payload)) + payload.encode("utf-8")
		logger.info("Data encoded")
		logger.debug("Encoded data: " + str(encoded_data))
		self.ipc_socket.write(encoded_data)
		self.ipc_socket.flush()
		logger.info("Data sent")