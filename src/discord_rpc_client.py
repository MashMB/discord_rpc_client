"""
File name: discord_rpc_client.py
Author: Maciej Bedra

Main entry point.
"""

import discord_ipc
import time

def main():
	"""
	Short example how to set Discord Rich Presence 
	via Discord IPC wrapper.
	"""

	"""
	Create instance of DiscordIPC class.
	Where ClientID paste your token generated
	on Discord website (developers section).
	"""
	ipc = discord_ipc.DiscordIPC("ClientID")
	ipc.connect()
	time.sleep(5)

	"""
	Send Discord Rich Presence status to Discord 
	just change method parameters.

	activity_details = description of main user activity

	activity_state = additional description of user activity
	"""
	ipc.send_simple_rich_presence("activity_details", "activity_state")
	time.sleep(30)
	ipc.disconnect()

	"""
	There is also support for complex Discord Rich Presence payload
	(changing images, not only texts) just replace this line:

	# ipc.send_simple_rich_presence("activity_details", "activity_state") #

	with this line:
		
	# ipc.send_complex_rich_presence("large_text", "large_image", "small_text", "small_image", "activity_details", "activity_state") #

	large_text = text that will be displayed on large image hover

	large_image = name of large image file, seted on Discord website 
	(developers  section, will display as application logo)

	small_text = text that will be displayed on small image hover

	small_image = name of small image file, seted on Discord website 
	(developers section, will display in right bottom corner of large image)

	activity_details = description of main user activity

	activity_state = additional description of user activity
	"""

if __name__ == "__main__":
	main()