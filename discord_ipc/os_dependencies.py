"""
File name: os_dependencies.py
Author: Maciej Bedra

File that contains expected paths to IPC 
sockets on specific platforms.
"""

# Path variations for specific platforms
paths = {
	"windows": "\\\\?\\pipe",
	"linux": {
		"XDG_RUNTIME_DIR",
		"TMPDIR",
		"TMP",
		"TEMP"
	},
	"darwin": {
		"XDG_RUNTIME_DIR",
		"TMPDIR",
		"TMP",
		"TEMP"
	}
}