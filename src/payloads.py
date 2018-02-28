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