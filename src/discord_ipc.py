"""
File name: discord_ipc.py
Author: Maciej Bedra

Simple Discord IPC wrapper that gives opportunity 
to use Discord Rich Presence for example.
"""

import logging

logger = logging.getLogger(__name__)
logging.basicConfig(format = "%(asctime)s: [%(levelname)s]: %(message)s", datefmt = "%d.%m.%Y (%H:%M:%S)", level = logging.DEBUG)