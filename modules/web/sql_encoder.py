from core.base_tool import BaseTool, register_tool
from core.exceptions import ExecutionError
import urllib.parse
import binascii

@register_tool
class SqlEncoder(BaseTool):
    name = 'sql_encoder'
    category = 'web'
    description = 'SQL payload encoder for CTF'
    tags = ['web', 'sql', 'encode']

    def _setup_options(self):
        self.add_option('DATA', 'SQL payload', required=True)
        self.add_option('MODE', 'Mode', required=False, default='url')

    def run(self) -> dict:
        data = self.get_option('DATA')
        mode = self.get_option('MODE')
        
        res = ""
        if mode == 'url':
            res = urllib.parse.quote(data)
        elif mode == 'double_url':
            res = urllib.parse.quote(urllib.parse.quote(data))
        elif mode == 'hex':
            res = "0x" + binascii.hexlify(data.encode()).decode()
        elif mode == 'reference':
            res = "Common: ' OR 1=1 --, UNION SELECT"
            
        return {'status': 'success', 'result': {'output': res}}
