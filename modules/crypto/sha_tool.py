from core.base_tool import BaseTool, register_tool
from core.exceptions import ExecutionError
import hashlib
import os

@register_tool
class SHATool(BaseTool):
    """SHA family hash operations."""
    name = 'sha_tool'
    category = 'crypto'
    description = 'SHA hash string or file, and verify.'
    tags = ['sha', 'hash']

    def _setup_options(self):
        self.add_option('DATA', 'Input data or file path', required=True)
        self.add_option('ALGORITHM', 'sha1/sha224/sha256/sha384/sha512', required=False, default='sha256', choices=['sha1', 'sha224', 'sha256', 'sha384', 'sha512'])
        self.add_option('MODE', 'hash/verify/file', required=False, default='hash', choices=['hash', 'verify', 'file'])
        self.add_option('EXPECTED', 'Expected hash for verify mode', required=False, default='')

    def _get_hasher(self, algo):
        return getattr(hashlib, algo)()

    def run(self) -> dict:
        data = self.get_option('DATA')
        algo = self.get_option('ALGORITHM')
        mode = self.get_option('MODE')
        expected = self.get_option('EXPECTED').lower()
        
        try:
            if mode == 'hash':
                hasher = self._get_hasher(algo)
                hasher.update(data.encode('utf-8'))
                return {'status': 'success', 'result': hasher.hexdigest()}
            
            elif mode == 'file':
                if not os.path.exists(data):
                    raise ExecutionError(f"File not found: {data}")
                hasher = self._get_hasher(algo)
                with open(data, 'rb') as f:
                    for chunk in iter(lambda: f.read(4096), b""):
                        hasher.update(chunk)
                return {'status': 'success', 'result': hasher.hexdigest()}
            
            elif mode == 'verify':
                hasher = self._get_hasher(algo)
                hasher.update(data.encode('utf-8'))
                h = hasher.hexdigest()
                is_match = h == expected
                res = f"Algorithm:  {algo}\nCalculated: {h}\nExpected:   {expected}\nMatch:      {is_match}"
                return {'status': 'success', 'result': res}
                
        except Exception as e:
            raise ExecutionError(f"SHA Tool error: {str(e)}")
