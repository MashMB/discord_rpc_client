"""
File name: payloads.py
Author: Maciej Bedra

File that contains templates of payloads that
can be send to Discord app via Discrod IPC socket.
"""

# Payload template for handshaking
handshake = {
	"v": 1,
	"client_id": None
}

# Json template for rpc assets section
rpc_assets = {
	"large_text": None,
	"large_image": None,
	"small_text": None,
	"small_image": None
}

# Json template for rpc timestamps section
rpc_timestamps = {
	"start": None
}

# Json template for rpc activity section
rpc_activity = {
	"details": None,
	"state": None,
	"timestamps": rpc_timestamps,
	"asstes": rpc_assets
}

# Json template for rpc args section
rpc_args = {
	"activity": rpc_activity,
	"pid": None
}

# Payload template for Discord Rich Presence
rpc = {
	"cmd": "SET_ACTIVITY",
	"args": rpc_args,
	"nonce": None
}