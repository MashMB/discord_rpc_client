"""
File name: payloads.py
Author: Maciej Bedra

File that contains description of payloads that
can be send to Discord app via Discrod IPC socket.
"""

# Payload for handshaking
handshake = {
	"v": 1,
	"client_id": None
}