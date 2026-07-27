import os
import zipfile
from core.base_tool import BaseTool, register_tool
from core.exceptions import ExecutionError

@register_tool
class MetadataExtractor(BaseTool):
    name = 'metadata'
    category = 'forensic'
    description = 'Extract metadata from common file types natively'
    tags = ['forensic', 'metadata']
    
    def _setup_options(self):
        self.add_option('FILE', 'Path to file', required=True)
    
    def parse_png(self, content: bytes) -> dict:
        meta = {}
        idx = 8
        while idx < len(content):
            if idx + 8 > len(content): break
            length = int.from_bytes(content[idx:idx+4], 'big')
            chunk_type = content[idx+4:idx+8].decode('ascii', errors='ignore')
            data_start = idx + 8
            data_end = data_start + length
            if data_end > len(content): break
            
            if chunk_type in ('tEXt', 'zTXt', 'iTXt'):
                data = content[data_start:data_end]
                try:
                    if b'\x00' in data:
                        key, val = data.split(b'\x00', 1)
                        meta[key.decode('latin1', errors='ignore')] = val.decode('latin1', errors='ignore')
                except Exception:
                    pass
            idx = data_end + 4
        return meta

    def parse_pdf(self, content: bytes) -> dict:
        meta = {}
        info_idx = content.find(b'/Info')
        if info_idx != -1:
            obj_idx = content.rfind(b'obj', 0, info_idx)
            endobj_idx = content.find(b'endobj', info_idx)
            if obj_idx != -1 and endobj_idx != -1:
                info_data = content[obj_idx:endobj_idx].decode('latin1', errors='ignore')
                import re
                matches = re.findall(r'/([A-Za-z]+)\s*\((.*?)\)', info_data)
                for k, v in matches:
                    meta[k] = v
        return meta

    def run(self) -> dict:
        file_path = self.get_option('FILE')
        
        if not os.path.exists(file_path):
            raise ExecutionError(f"File not found: {file_path}")
            
        with open(file_path, 'rb') as f:
            content = f.read()
            
        results = {}
        
        if content.startswith(b'\x89PNG\r\n\x1a\n'):
            results['type'] = 'PNG'
            results['metadata'] = self.parse_png(content)
        elif content.startswith(b'%PDF-'):
            results['type'] = 'PDF'
            results['metadata'] = self.parse_pdf(content)
        elif content.startswith(b'PK\x03\x04'):
            results['type'] = 'ZIP'
            meta = {}
            try:
                with zipfile.ZipFile(file_path, 'r') as zf:
                    meta['comment'] = zf.comment.decode('latin1', errors='ignore')
                    meta['files'] = [info.filename for info in zf.infolist()]
            except Exception as e:
                meta['error'] = str(e)
            results['metadata'] = meta
        elif content.startswith(b'\xff\xd8\xff'):
            results['type'] = 'JPEG'
            results['metadata'] = {'info': 'Basic JPEG found. EXIF parsing not fully implemented natively yet. Use exiftool wrapper.'}
        else:
            results['type'] = 'Unknown'
            results['metadata'] = {}
            
        return {'status': 'success', 'result': results}
