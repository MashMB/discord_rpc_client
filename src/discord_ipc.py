"""
File name: discord_ipc.py
Author: Maciej Bedra

Simple Discord IPC wrapper that gives opportunity 
to use Discord Rich Presence.
"""

import logging
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