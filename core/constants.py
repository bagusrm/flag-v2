"""
Constants for the FLAG CTF Framework.
"""

VERSION = '2.0.0'
APP_NAME = 'CTF'
FULL_NAME = 'CAPTURE THE FLAG'
AUTHOR = 'CTF Team'

BANNER = """[bold cyan]
  ____    _    ____ _____ _   _ ____  _____   THE
 / ___|  / \\  |  _ \\_   _| | | |  _ \\| ____|  
| |     / _ \\ | |_) || | | | | | |_) |  _|    
| |___ / ___ \\|  __/ | | | |_| |  _ <| |___   
 \\____/_/   \\_\\_|    |_|  \\___/|_| \\_\\_____|  
                                              
 _____ _        _    ____                     
|  ___| |      / \\  / ___|                    
| |_  | |     / _ \\| |  _                     
|  _| | |___ / ___ \\ |_| |                    
|_|   |_____/_/   \\_\\____|                    
[/bold cyan][bold red]
      -= CTF Framework v2.0.0 =-
[/bold red]"""

DEFAULT_PROMPT = 'CTF'
HISTORY_FILE = '.ctf_history'
SESSION_DIR = 'sessions'
LOG_DIR = 'logs'
CONFIG_FILE = 'config/settings.yaml'

CATEGORIES = ['crypto', 'forensic', 'reverse', 'pwn', 'web', 'osint', 'stego', 'misc']

CATEGORY_DESCRIPTIONS = {
    'crypto': 'Cryptography challenges involving encryption, hashing, and encoding.',
    'forensic': 'Digital forensics tasks such as memory, network, and file analysis.',
    'reverse': 'Reverse engineering binaries to understand their behavior.',
    'pwn': 'Binary exploitation and memory corruption challenges.',
    'web': 'Web application security vulnerabilities.',
    'osint': 'Open Source Intelligence gathering.',
    'stego': 'Steganography challenges hiding data within other media.',
    'misc': 'Miscellaneous challenges that do not fit into other categories.'
}

CATEGORY_ICONS = {
    'crypto': '🔐',
    'forensic': '🔍',
    'reverse': '⚙️',
    'pwn': '💥',
    'web': '🌐',
    'osint': '👁️',
    'stego': '🖼️',
    'misc': '🧩'
}
