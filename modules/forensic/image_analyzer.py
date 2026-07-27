import os
import struct
import math
from core.base_tool import BaseTool, register_tool
from core.exceptions import ExecutionError

@register_tool
class ImageAnalyzerTool(BaseTool):
    name = 'image_analyzer'
    category = 'forensic'
    description = 'Analyze image files (dimensions, depth, entropy)'
    tags = ['forensic', 'image', 'picture']
    
    def _setup_options(self):
        self.add_option('FILE', 'Path to file', required=True)
        
    def calc_entropy(self, data: bytes) -> float:
        if not data: return 0.0
        entropy = 0
        for x in range(256):
            p_x = float(data.count(x)) / len(data)
            if p_x > 0:
                entropy += - p_x * math.log2(p_x)
        return entropy

    def run(self) -> dict:
        file_path = self.get_option('FILE')
        
        if not os.path.exists(file_path):
            raise ExecutionError(f"File not found: {file_path}")
            
        with open(file_path, 'rb') as f:
            content = f.read()
            
        result = {
            'file_size': len(content),
            'entropy': self.calc_entropy(content)
        }
        
        if content.startswith(b'\x89PNG\r\n\x1a\n'):
            result['type'] = 'PNG'
            if len(content) >= 24 and content[12:16] == b'IHDR':
                width, height, depth, color_type = struct.unpack('>IIBB', content[16:26])
                result['width'] = width
                result['height'] = height
                result['bit_depth'] = depth
                result['color_type'] = color_type
        elif content.startswith(b'\xff\xd8\xff'):
            result['type'] = 'JPEG'
            result['has_exif'] = b'Exif' in content[:1024]
            # Try to find dimensions
            idx = 2
            while idx < len(content) - 8:
                marker, length = struct.unpack('>HH', content[idx:idx+4])
                if 0xFFC0 <= marker <= 0xFFC3:
                    height, width = struct.unpack('>HH', content[idx+5:idx+9])
                    result['width'] = width
                    result['height'] = height
                    break
                idx += length + 2
        else:
            result['type'] = 'Unknown/Unsupported natively'
            
        return {'status': 'success', 'result': result}
