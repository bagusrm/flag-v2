from core.base_tool import BaseTool, register_tool
from core.exceptions import ExecutionError
import hashlib
import os

@register_tool
class MD5Tool(BaseTool):
    """MD5 hash operations."""
    name = 'md5_tool'
    category = 'crypto'
    description = 'MD5 hash string or file, and verify.'
    tags = ['md5', 'hash']

    def _setup_options(self):
        self.add_option('DATA', 'Input data or file path', required=True)
        self.add_option('MODE', 'hash/verify/file', required=False, default='hash', choices=['hash', 'verify', 'file'])
        self.add_option('EXPECTED', 'Expected hash for verify mode', required=False, default='')

    def run(self) -> dict:
        data = self.get_option('DATA')
        mode = self.get_option('MODE')
        expected = self.get_option('EXPECTED').lower()
        
        try:
            if mode == 'hash':
                h = hashlib.md5(data.encode('utf-8')).hexdigest()
                return {'status': 'success', 'result': h}
            
            elif mode == 'file':
                if not os.path.exists(data):
                    raise ExecutionError(f"File not found: {data}")
                md5_hash = hashlib.md5()
                with open(data, 'rb') as f:
                    for chunk in iter(lambda: f.read(4096), b""):
                        md5_hash.update(chunk)
                return {'status': 'success', 'result': md5_hash.hexdigest()}
            
            elif mode == 'verify':
                h = hashlib.md5(data.encode('utf-8')).hexdigest()
                is_match = h == expected
                res = f"Calculated: {h}\nExpected:   {expected}\nMatch:      {is_match}"
                return {'status': 'success', 'result': res}
                
        except Exception as e:
            raise ExecutionError(f"MD5 Tool error: {str(e)}")
