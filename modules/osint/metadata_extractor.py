import os
import struct
from core.base_tool import BaseTool, register_tool
from core.exceptions import ExecutionError

@register_tool
class MetadataExtractor(BaseTool):
    name = 'metadata_extractor'
    category = 'osint'
    description = 'Extract metadata from files (pure python)'
    tags = ['osint', 'metadata', 'exif']

    def _setup_options(self):
        self.add_option('FILE', 'Path to file', required=True)

    def run(self) -> dict:
        file_path = self.get_option('FILE')
        
        if not os.path.exists(file_path):
            raise ExecutionError(f"File not found: {file_path}")

        result = {
            'file': file_path,
            'size': os.path.getsize(file_path),
            'metadata': {},
            'message': ''
        }

        # Basic EXIF check for JPEG
        try:
            with open(file_path, 'rb') as f:
                data = f.read(1024)
                
                # Check JPEG SOI
                if data.startswith(b'\xff\xd8'):
                    result['file_type'] = 'JPEG'
                    # Look for APP1 (EXIF)
                    if b'Exif\x00\x00' in data:
                        result['metadata']['exif_present'] = True
                        result['message'] = "EXIF data detected. For full extraction, use ExifTool."
                    else:
                        result['metadata']['exif_present'] = False
                elif data.startswith(b'\x89PNG'):
                    result['file_type'] = 'PNG'
                elif data.startswith(b'%PDF'):
                    result['file_type'] = 'PDF'
                else:
                    result['file_type'] = 'Unknown'
                    
        except Exception as e:
            result['message'] = f"Error during extraction: {str(e)}"

        return {'status': 'success', 'result': result}
