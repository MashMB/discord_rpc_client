"""
File name: ipc.py
Author: Maciej Bedra

Simple Discord IPC wrapper that gives opportunity 
to use Discord Rich Presence.
"""

import logging
import os
import os_dependencies
import platform
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
			logger.info("Searching for valid IPC sockets path...")

			# Other Discord IPC socket localization on different platofrms
			if system_name == os_dependencies.supported[0] :
				pipe = os_dependencies.paths["windows"] + "\\" + os_dependencies.sockets_names["discord"]
			else:
				for path in os_dependencies.paths["unix"]:
					if os.environ.get(path, None) != None:
						pipe = os.environ.get(path) + "/" + os_dependencies.sockets_names["discord"]
						break

				if pipe == None:
					pipe = "/tmp" + os_dependencies.sockets_names["discord"]

			logger.info("IPC socket found ")
			logger.debug("IPC socket path: " + pipe)

		else:
			# If platform is not supported, end program
			logger.info("Unsupported OS")
			sys.exit()

		return pipe