from core.base_tool import BaseTool, register_tool
from core.exceptions import ExecutionError
import urllib.parse
import html
import base64

@register_tool
class XssEncoder(BaseTool):
    name = 'xss_encoder'
    category = 'web'
    description = 'XSS payload encoder for CTF'
    tags = ['web', 'xss', 'encode']

    def _setup_options(self):
        self.add_option('DATA', 'XSS payload', required=True)
        self.add_option('MODE', 'Mode', required=False, default='html')

    def run(self) -> dict:
        data = self.get_option('DATA')
        mode = self.get_option('MODE')
        
        res = ""
        if mode == 'html':
            res = html.escape(data)
        elif mode == 'url':
            res = urllib.parse.quote(data)
        elif mode == 'base64':
            b64 = base64.b64encode(data.encode()).decode()
            res = f"data:text/html;base64,{b64}"
        elif mode == 'reference':
            res = "<script>alert(1)</script>"
            
        return {'status': 'success', 'result': {'output': res}}
