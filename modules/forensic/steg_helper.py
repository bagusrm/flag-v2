import os
from core.base_tool import BaseTool, register_tool
from core.exceptions import ExecutionError

@register_tool
class StegHelperTool(BaseTool):
    name = 'steg_helper'
    category = 'forensic'
    description = 'Basic steganography detection helper'
    tags = ['forensic', 'stego', 'analysis']
    
    def _setup_options(self):
        self.add_option('FILE', 'Path to file', required=True)
    
    def run(self) -> dict:
        file_path = self.get_option('FILE')
        
        if not os.path.exists(file_path):
            raise ExecutionError(f"File not found: {file_path}")
            
        with open(file_path, 'rb') as f:
            header = f.read(16)
            
        file_size = os.path.getsize(file_path)
        
        indicators = []
        suggestions = []
        
        if header.startswith(b'\xff\xd8\xff'):
            file_type = 'JPEG'
            suggestions.extend(['steghide', 'stegseek', 'jsteg', 'exiftool'])
            indicators.append('Check for hidden data after FFD9 (EOF)')
        elif header.startswith(b'\x89PNG\r\n\x1a\n'):
            file_type = 'PNG'
            suggestions.extend(['zsteg', 'stegsolve', 'pngcheck'])
            indicators.append('Check for suspicious chunks or LSB steganography')
        elif header.startswith(b'RIFF') and len(header) >= 12 and header[8:12] == b'WAVE':
            file_type = 'WAV'
            suggestions.extend(['steghide', 'Sonic Visualiser', 'Audacity'])
            indicators.append('Check for LSB steganography or spectrogram secrets')
        elif header.startswith(b'%PDF'):
            file_type = 'PDF'
            suggestions.extend(['peepdf', 'pdf-parser'])
            indicators.append('Check for hidden streams or white text')
        else:
            file_type = 'Unknown/Other'
            suggestions.extend(['binwalk', 'strings', 'xxd'])
            
        # Common checks
        if file_size > 10 * 1024 * 1024:
            indicators.append(f'File is relatively large ({file_size} bytes). Could hide data.')
            
        return {
            'status': 'success', 
            'result': {
                'file_type': file_type,
                'stego_indicators': indicators,
                'suggested_tools': suggestions
            }
        }
