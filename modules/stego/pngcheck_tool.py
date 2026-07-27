import os
import struct
import zlib
from core.base_tool import BaseTool, register_tool
from core.exceptions import ExecutionError

@register_tool
class PNGCheckTool(BaseTool):
    name = 'pngcheck'
    category = 'stego'
    description = 'Verify PNG signature, chunk CRCs, and IHDR values'
    tags = ['stego', 'png', 'verify']

    def _setup_options(self):
        self.add_option('FILE', 'Path to file', required=True)

    def run(self) -> dict:
        file_path = self.get_option('FILE')
        if not os.path.exists(file_path):
            raise ExecutionError(f"File not found: {file_path}")

        result = {
            'is_png': False,
            'chunks': [],
            'errors': [],
            'ihdr': {}
        }

        with open(file_path, 'rb') as f:
            signature = f.read(8)
            if signature != b'\x89PNG\r\n\x1a\n':
                result['errors'].append("Invalid PNG signature")
                return {'status': 'success', 'result': result}
            
            result['is_png'] = True
            
            while True:
                chunk_length_bytes = f.read(4)
                if len(chunk_length_bytes) == 0:
                    break
                if len(chunk_length_bytes) < 4:
                    result['errors'].append("Truncated chunk length")
                    break
                    
                length = struct.unpack('>I', chunk_length_bytes)[0]
                chunk_type = f.read(4)
                if len(chunk_type) < 4:
                    result['errors'].append("Truncated chunk type")
                    break
                
                chunk_data = f.read(length)
                if len(chunk_data) < length:
                    result['errors'].append(f"Truncated chunk data for {chunk_type.decode(errors='ignore')}")
                    break
                
                crc_bytes = f.read(4)
                if len(crc_bytes) < 4:
                    result['errors'].append(f"Truncated CRC for {chunk_type.decode(errors='ignore')}")
                    break
                    
                crc = struct.unpack('>I', crc_bytes)[0]
                computed_crc = zlib.crc32(chunk_type + chunk_data) & 0xffffffff
                
                is_crc_valid = crc == computed_crc
                
                c_type_str = chunk_type.decode(errors='replace')
                result['chunks'].append({
                    'type': c_type_str,
                    'length': length,
                    'crc_valid': is_crc_valid
                })
                
                if not is_crc_valid:
                    result['errors'].append(f"CRC mismatch in {c_type_str} chunk")

                if chunk_type == b'IHDR':
                    if length == 13:
                        w, h, bd, ct, cm, fm, im = struct.unpack('>IIBBBBB', chunk_data)
                        result['ihdr'] = {
                            'width': w,
                            'height': h,
                            'bit_depth': bd,
                            'color_type': ct,
                            'compression_method': cm,
                            'filter_method': fm,
                            'interlace_method': im
                        }
                    else:
                        result['errors'].append("Invalid IHDR length")
                
                if chunk_type == b'IEND':
                    break

        return {'status': 'success', 'result': result}
