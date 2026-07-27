import base64
import string
import urllib.parse
from core.base_tool import BaseTool, register_tool
from core.exceptions import ExecutionError

@register_tool
class AutoIdentifyEncoding(BaseTool):
    name = 'auto_identify_encoding'
    category = 'misc'
    description = 'Automatically identify encoding of a string and recursively decode'
    tags = ['automation', 'encoding', 'identify']

    def _setup_options(self):
        self.add_option('DATA', 'Input data string', required=True)
        self.add_option('MAX_DEPTH', 'Maximum recursion depth', required=False, default=3)

    def is_printable(self, s: str) -> bool:
        printable = set(string.printable)
        return all(c in printable for c in s) and len(s) > 0

    def try_decode(self, data: str) -> list:
        results = []
        
        # Base64
        try:
            dec = base64.b64decode(data).decode('utf-8')
            if self.is_printable(dec) and dec != data:
                results.append(('Base64', dec))
        except: pass
        
        # Base32
        try:
            dec = base64.b32decode(data).decode('utf-8')
            if self.is_printable(dec) and dec != data:
                results.append(('Base32', dec))
        except: pass
        
        # Base16 / Hex
        try:
            dec = bytes.fromhex(data).decode('utf-8')
            if self.is_printable(dec) and dec != data:
                results.append(('Hex', dec))
        except: pass
        
        # URL
        try:
            dec = urllib.parse.unquote(data)
            if dec != data:
                results.append(('URL', dec))
        except: pass
        
        # Binary
        try:
            clean = data.replace(' ', '')
            if all(c in '01' for c in clean) and len(clean) % 8 == 0:
                dec = ''.join(chr(int(clean[i:i+8], 2)) for i in range(0, len(clean), 8))
                if self.is_printable(dec):
                    results.append(('Binary', dec))
        except: pass

        # ROT13
        try:
            dec = data.translate(str.maketrans(
                string.ascii_lowercase + string.ascii_uppercase,
                string.ascii_lowercase[13:] + string.ascii_lowercase[:13] + string.ascii_uppercase[13:] + string.ascii_uppercase[:13]
            ))
            if dec != data and self.is_printable(dec):
                results.append(('ROT13', dec))
        except: pass
        
        return results

    def recursive_decode(self, data: str, depth: int, max_depth: int) -> list:
        if depth >= max_depth:
            return []
        
        found = self.try_decode(data)
        paths = []
        for enc, dec in found:
            paths.append({
                'encoding': enc, 
                'decoded': dec, 
                'depth': depth + 1, 
                'children': self.recursive_decode(dec, depth + 1, max_depth)
            })
        return paths

    def run(self) -> dict:
        data = self.get_option('DATA')
        max_depth = int(self.get_option('MAX_DEPTH'))
        
        results = self.recursive_decode(data, 0, max_depth)
        
        return {
            'status': 'success',
            'original_data': data,
            'max_depth': max_depth,
            'results': results
        }
