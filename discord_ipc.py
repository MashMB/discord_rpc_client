"""
File name: ipc.py
Author: Maciej Bedra

Simple Discord IPC wrapper that gives opportunity 
to use Discord Rich Presence.
"""

import logging
import os

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
		self.soc = None
		self.pid = os.getpid()