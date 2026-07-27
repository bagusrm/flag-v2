"""
Utility functions for the FLAG CTF Framework.
"""
import base64
import math
import re
import string
import datetime
from pathlib import Path
from typing import Union, List, Optional

def read_file_bytes(path: Union[str, Path]) -> bytes:
    """Reads file content as bytes."""
    with open(path, 'rb') as f:
        return f.read()

def read_file_text(path: Union[str, Path]) -> str:
    """Reads file content as text (UTF-8)."""
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def write_file(path: Union[str, Path], data: Union[str, bytes]) -> None:
    """Writes text or bytes to a file, creating parent directories as needed."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(data, str):
        with open(path, 'w', encoding='utf-8') as f:
            f.write(data)
    else:
        with open(path, 'wb') as f:
            f.write(data)

def is_hex_string(s: str) -> bool:
    """Checks if a string is a valid hexadecimal string."""
    s = s.strip()
    if not s:
        return False
    # Check if length is even and only contains hex digits
    if len(s) % 2 != 0:
        return False
    return all(c in string.hexdigits for c in s)

def is_base64_string(s: str) -> bool:
    """Checks if a string is a valid base64 encoded string."""
    s = s.strip()
    if not s or len(s) % 4 != 0:
        return False
    try:
        base64.b64decode(s, validate=True)
        return True
    except Exception:
        return False

def is_printable(s: str) -> bool:
    """Checks if a string contains only printable characters."""
    return all(c in string.printable for c in s)

def safe_decode(data: bytes, encodings: Optional[List[str]] = None) -> str:
    """Attempts to decode bytes using a list of encodings."""
    if encodings is None:
        encodings = ['utf-8', 'latin-1', 'ascii']
    for enc in encodings:
        try:
            return data.decode(enc)
        except UnicodeDecodeError:
            continue
    return str(data)  # Fallback

def format_hex_dump(data: bytes, width: int = 16) -> str:
    """Formats bytes into a standard hex dump."""
    output = []
    for i in range(0, len(data), width):
        chunk = data[i:i+width]
        hex_str = ' '.join(f'{b:02x}' for b in chunk)
        ascii_str = ''.join(chr(b) if 32 <= b <= 126 else '.' for b in chunk)
        output.append(f'{i:08x}  {hex_str:<{width*3}} |{ascii_str}|')
    return '\n'.join(output)

def calculate_entropy(data: bytes) -> float:
    """Calculates the Shannon entropy of the given bytes."""
    if not data:
        return 0.0
    entropy = 0.0
    for i in range(256):
        p_i = data.count(i) / len(data)
        if p_i > 0:
            entropy += - p_i * math.log2(p_i)
    return entropy

def human_readable_size(size: int) -> str:
    """Converts a size in bytes to a human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            return f"{size:.2f} {unit}"
        size /= 1024.0
    return f"{size:.2f} PB"

def truncate_string(s: str, max_len: int = 100) -> str:
    """Truncates a string to a maximum length, adding ellipsis if truncated."""
    if len(s) <= max_len:
        return s
    return s[:max_len-3] + "..."

def strip_ansi(s: str) -> str:
    """Removes ANSI escape sequences from a string."""
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', s)

def ensure_dir(path: Union[str, Path]) -> Path:
    """Ensures a directory exists, creating it if necessary."""
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p

def get_file_type(path: Union[str, Path]) -> str:
    """Attempts to guess the file type using magic bytes."""
    try:
        with open(path, 'rb') as f:
            header = f.read(8)
        if header[:4] == b'\x7fELF':
            return 'ELF Executable'
        elif header[:2] == b'MZ':
            return 'PE Executable'
        elif header[:8] == b'\x89PNG\r\n\x1a\n':
            return 'PNG Image'
        elif header[:3] == b'\xff\xd8\xff':
            return 'JPEG Image'
        elif header[:4] == b'%PDF':
            return 'PDF Document'
        elif header[:4] == b'PK\x03\x04':
            return 'ZIP Archive'
        elif header[:3] == b'GIF':
            return 'GIF Image'
        elif header[:4] == b'RIFF':
            return 'RIFF (WAV/AVI)'
        else:
            return 'Unknown/Binary'
    except Exception:
        return 'Unknown'

def timestamp_now() -> str:
    """Returns the current timestamp as a string."""
    return datetime.datetime.now().isoformat()
