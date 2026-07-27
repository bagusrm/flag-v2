import os
import zlib
from core.base_tool import BaseTool, register_tool
from core.exceptions import ExecutionError

@register_tool
class PNGChunkParser(BaseTool):
    name = 'png_chunks'
    category = 'forensic'
    description = 'Parse and validate PNG file chunks'
    tags = ['forensic', 'png', 'chunks']
    
    def _setup_options(self):
        self.add_option('FILE', 'Path to file', required=True)
    
    def run(self) -> dict:
        file_path = self.get_option('FILE')
        
        if not os.path.exists(file_path):
            raise ExecutionError(f"File not found: {file_path}")
            
        with open(file_path, 'rb') as f:
            content = f.read()
            
        if not content.startswith(b'\x89PNG\r\n\x1a\n'):
            return {'status': 'error', 'message': 'Not a valid PNG file'}
            
        chunks = []
        idx = 8
        suspicious = []
        
        known_chunks = {'IHDR', 'PLTE', 'IDAT', 'IEND', 'tRNS', 'cHRM', 'gAMA', 'iCCP', 'sBIT', 'sRGB', 'tEXt', 'zTXt', 'iTXt', 'bKGD', 'hIST', 'pHYs', 'sPLT', 'tIME'}
        
        while idx < len(content):
            if idx + 8 > len(content):
                suspicious.append("Truncated chunk header at end of file")
                break
                
            length = int.from_bytes(content[idx:idx+4], 'big')
            chunk_type = content[idx+4:idx+8].decode('ascii', errors='replace')
            data_start = idx + 8
            data_end = data_start + length
            
            if data_end + 4 > len(content):
                suspicious.append(f"Truncated chunk data for {chunk_type}")
                break
                
            chunk_data = content[data_start:data_end]
            file_crc = int.from_bytes(content[data_end:data_end+4], 'big')
            
            # Calculate CRC over chunk type + chunk data
            calc_crc = zlib.crc32(content[idx+4:data_end]) & 0xffffffff
            
            crc_ok = (file_crc == calc_crc)
            if not crc_ok:
                suspicious.append(f"CRC mismatch in chunk {chunk_type}")
                
            if chunk_type not in known_chunks:
                suspicious.append(f"Unknown/Non-standard chunk type: {chunk_type}")
                
            chunks.append({
                'type': chunk_type,
                'length': length,
                'crc_ok': crc_ok,
                'offset': idx
            })
            
            idx = data_end + 4
            
        return {
            'status': 'success', 
            'result': {
                'total_chunks': len(chunks),
                'chunks': chunks,
                'suspicious_findings': suspicious
            }
        }
