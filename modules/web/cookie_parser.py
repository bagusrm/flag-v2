from core.base_tool import BaseTool, register_tool
from core.exceptions import ExecutionError
import urllib.parse

@register_tool
class CookieParser(BaseTool):
    name = 'cookie_parser'
    category = 'web'
    description = 'HTTP Cookie parser'
    tags = ['web', 'cookie', 'parse']

    def _setup_options(self):
        self.add_option('DATA', 'Cookie string', required=True)

    def run(self) -> dict:
        data = self.get_option('DATA')
        cookies = {}
        
        parts = data.split(';')
        for part in parts:
            part = part.strip()
            if not part: continue
            if '=' in part:
                k, v = part.split('=', 1)
                cookies[k] = urllib.parse.unquote(v)
            else:
                cookies[part] = True
                
        return {'status': 'success', 'result': {'parsed_cookies': cookies}}
