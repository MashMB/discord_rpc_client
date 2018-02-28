"""
File name: os_dependencies.py
Author: Maciej Bedra

File that contains expected paths to IPC 
sockets on specific platforms.
"""

# Supported platforms
supported = ["windows", "linux", "darwin"]

# Path variations for specific platforms
paths = {
	"windows": "\\\\?\\pipe",
	"unix": {
		"XDG_RUNTIME_DIR",
		"TMPDIR",
		"TMP",
		"TEMP"
	}
}

# Expected sockets names
sockets_names = {
	"discord": "discord-ipc-0"
}