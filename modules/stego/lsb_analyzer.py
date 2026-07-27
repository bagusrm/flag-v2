import os
import zlib
import struct
from core.base_tool import BaseTool, register_tool
from core.exceptions import ExecutionError

@register_tool
class LSBAnalyzer(BaseTool):
    name = 'lsb_analyzer'
    category = 'stego'
    description = 'Analyze LSB distribution of an image'
    tags = ['stego', 'lsb', 'analysis']

    def _setup_options(self):
        self.add_option('FILE', 'Path to file', required=True)
        self.add_option('CHANNEL', 'Channel: red/green/blue/all', required=False, default='all')
        self.add_option('BITS', 'Number of LSB bits', required=False, default='1')

    def _extract_idat(self, file_path):
        data = b''
        with open(file_path, 'rb') as f:
            f.read(8) # sig
            while True:
                length_bytes = f.read(4)
                if not length_bytes: break
                length = struct.unpack('>I', length_bytes)[0]
                chunk_type = f.read(4)
                chunk_data = f.read(length)
                f.read(4) # crc
                if chunk_type == b'IDAT':
                    data += chunk_data
                elif chunk_type == b'IEND':
                    break
        return data

    def run(self) -> dict:
        file_path = self.get_option('FILE')
        channel = self.get_option('CHANNEL')
        bits = int(self.get_option('BITS'))
        
        if not os.path.exists(file_path):
            raise ExecutionError(f"File not found: {file_path}")

        result = {
            'analysis': {},
            'message': 'LSB analysis performed on raw IDAT (PNG) data.',
            'is_png': file_path.lower().endswith('.png')
        }

        if not result['is_png']:
            result['message'] = "Currently only PNG files are supported for pure Python LSB analysis."
            return {'status': 'success', 'result': result}

        try:
            compressed_data = self._extract_idat(file_path)
            if not compressed_data:
                raise ExecutionError("No IDAT chunks found in PNG")
                
            raw_pixels = zlib.decompress(compressed_data)
            
            # Simple zero-one count for first few thousand bytes of raw data
            # Real LSB extraction would parse scanlines and filters
            sample = raw_pixels[:10000]
            zeros = 0
            ones = 0
            
            mask = (1 << bits) - 1
            for byte in sample:
                lsb = byte & mask
                if lsb == 0: zeros += 1
                else: ones += 1
                
            total = zeros + ones
            if total > 0:
                result['analysis'] = {
                    'zeros_count': zeros,
                    'ones_count': ones,
                    'zero_ratio': zeros / total,
                    'one_ratio': ones / total,
                    'anomaly_detected': abs((zeros / total) - 0.5) > 0.1
                }
            
        except Exception as e:
            raise ExecutionError(f"Error analyzing LSB: {str(e)}")

        return {'status': 'success', 'result': result}
