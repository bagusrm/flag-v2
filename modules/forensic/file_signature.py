import os
from core.base_tool import BaseTool, register_tool
from core.exceptions import ExecutionError

@register_tool
class FileSignatureTool(BaseTool):
    name = 'file_signature'
    category = 'forensic'
    description = 'Detect file type via magic bytes'
    tags = ['forensic', 'magic', 'signature']
    
    SIGNATURES = [
        (b'\x89PNG\r\n\x1a\n', 0, 'PNG'),
        (b'\xff\xd8\xff\xe0', 0, 'JPEG'),
        (b'\xff\xd8\xff\xe1', 0, 'JPEG (EXIF)'),
        (b'\xff\xd8\xff\xdb', 0, 'JPEG'),
        (b'GIF87a', 0, 'GIF'),
        (b'GIF89a', 0, 'GIF'),
        (b'BM', 0, 'BMP'),
        (b'II*\x00', 0, 'TIFF (Little Endian)'),
        (b'MM\x00*', 0, 'TIFF (Big Endian)'),
        (b'%PDF-', 0, 'PDF'),
        (b'PK\x03\x04', 0, 'ZIP'),
        (b'Rar!\x1a\x07\x00', 0, 'RAR v4'),
        (b'Rar!\x1a\x07\x01\x00', 0, 'RAR v5'),
        (b'7z\xbc\xaf\x27\x1c', 0, '7Z'),
        (b'\x1f\x8b', 0, 'GZIP'),
        (b'BZh', 0, 'BZIP2'),
        (b'\xfd7zXZ\x00', 0, 'XZ'),
        (b'ustar', 257, 'TAR'),
        (b'\x7fELF', 0, 'ELF'),
        (b'MZ', 0, 'PE/MZ'),
        (b'\xfe\xed\xfa\xce', 0, 'Mach-O 32-bit'),
        (b'\xfe\xed\xfa\xcf', 0, 'Mach-O 64-bit'),
        (b'\xca\xfe\xba\xbe', 0, 'Java Class'),
        (b'dex\n', 0, 'DEX'),
        (b'SQLite format 3\x00', 0, 'SQLite'),
        (b'\xd4\xc3\xb2\xa1', 0, 'PCAP (Little Endian)'),
        (b'\xa1\xb2\xc3\xd4', 0, 'PCAP (Big Endian)'),
        (b'\n\x0d\x0d\n', 0, 'PCAPNG'),
        (b'OggS', 0, 'OGG'),
        (b'ID3', 0, 'MP3'),
        (b'fLaC', 0, 'FLAC'),
        (b'RIFF', 0, 'WAV/AVI (RIFF)'), # Followed by WAVE or AVI
        (b'ftypisom', 4, 'MP4'),
        (b'ftypmp42', 4, 'MP4'),
        (b'FLV\x01', 0, 'FLV'),
        (b'8BPS', 0, 'PSD'),
        (b'\x00asm', 0, 'WASM')
    ]
    
    def _setup_options(self):
        self.add_option('FILE', 'Path to file', required=True)
    
    def run(self) -> dict:
        file_path = self.get_option('FILE')
        
        if not os.path.exists(file_path):
            raise ExecutionError(f"File not found: {file_path}")
            
        with open(file_path, 'rb') as f:
            content = f.read(512)
            
        detected = []
        for sig, offset, name in self.SIGNATURES:
            if len(content) >= offset + len(sig):
                if content[offset:offset+len(sig)] == sig:
                    detected.append({
                        'type': name,
                        'magic_hex': sig.hex(),
                        'offset': offset
                    })
                    
        # Check RIFF sub-types
        if any(d['type'] == 'WAV/AVI (RIFF)' for d in detected) and len(content) >= 12:
            sub_type = content[8:12]
            if sub_type == b'WAVE':
                detected.append({'type': 'WAV', 'magic_hex': b'RIFF....WAVE'.hex(), 'offset': 0})
            elif sub_type == b'AVI ':
                detected.append({'type': 'AVI', 'magic_hex': b'RIFF....AVI '.hex(), 'offset': 0})
                
        return {
            'status': 'success', 
            'result': {
                'detected': detected,
                'file_size': os.path.getsize(file_path),
                'header_hex': content[:16].hex()
            }
        }
