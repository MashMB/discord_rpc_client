"""
File name: discord_rpc_client.py
Author: Maciej Bedra

Main entry point.
"""

import discord_ipc

def main():
	ipc = discord_ipc.DiscordIPC("ClientID")

if __name__ == "__main__":
	main()