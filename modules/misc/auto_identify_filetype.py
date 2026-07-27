import os
from core.base_tool import BaseTool, register_tool
from core.exceptions import ExecutionError
from core.utils import read_file_bytes

@register_tool
class AutoIdentifyFiletype(BaseTool):
    name = 'auto_identify_filetype'
    category = 'misc'
    description = 'Automatic file type identification using magic bytes and extension checking'
    tags = ['automation', 'filetype', 'magic']

    def _setup_options(self):
        self.add_option('FILE', 'Path to the file', required=True)

    def run(self) -> dict:
        file_path = self.get_option('FILE')
        if not os.path.isfile(file_path):
            raise ExecutionError(f"File not found: {file_path}")

        try:
            data = read_file_bytes(file_path)
            # Only need first few bytes for magic check
            head = data[:32]
        except Exception as e:
            raise ExecutionError(f"Failed to read file: {e}")

        # Magic bytes dictionary
        magic_db = {
            b'\\x7fELF': 'ELF Executable',
            b'MZ': 'PE Executable',
            b'\\x89PNG\\x0d\\x0a\\x1a\\x0a': 'PNG Image',
            b'\\xff\\xd8\\xff': 'JPEG Image',
            b'PK\\x03\\x04': 'ZIP Archive',
            b'%PDF': 'PDF Document',
            b'Rar!\\x1a\\x07\\x00': 'RAR Archive',
            b'7z\\xbc\\xaf\\x27\\x1c': '7z Archive',
            b'ID3': 'MP3 Audio',
            b'OggS': 'Ogg Audio/Video'
        }

        identified_type = 'Unknown'
        for magic, desc in magic_db.items():
            if head.startswith(magic):
                identified_type = desc
                break

        ext = os.path.splitext(file_path)[1].lower().replace('.', '')
        
        # Mismatch detection logic
        mismatch = False
        ext_map = {
            'ELF Executable': ['elf', 'bin', ''],
            'PE Executable': ['exe', 'dll'],
            'PNG Image': ['png'],
            'JPEG Image': ['jpg', 'jpeg'],
            'ZIP Archive': ['zip', 'docx', 'xlsx', 'pptx', 'apk'],
            'PDF Document': ['pdf'],
            'RAR Archive': ['rar'],
            '7z Archive': ['7z'],
            'MP3 Audio': ['mp3'],
            'Ogg Audio/Video': ['ogg']
        }
        
        if identified_type != 'Unknown':
            allowed_exts = ext_map.get(identified_type, [])
            if ext and allowed_exts and ext not in allowed_exts:
                mismatch = True

        return {
            'status': 'success',
            'file': file_path,
            'extension': ext,
            'identified_type': identified_type,
            'mismatch_detected': mismatch,
            'head_bytes_hex': head.hex()
        }
