from core.base_tool import BaseTool, register_tool
from core.exceptions import ExecutionError
import urllib.parse

@register_tool
class UrlDecoder(BaseTool):
    name = 'url_decoder'
    category = 'web'
    description = 'URL encode/decode tool'
    tags = ['web', 'url', 'encode', 'decode']

    def _setup_options(self):
        self.add_option('DATA', 'Data string', required=True)
        self.add_option('MODE', 'Mode', required=False, default='decode')

    def run(self) -> dict:
        data = self.get_option('DATA')
        mode = self.get_option('MODE')
        
        res = ""
        if mode == 'decode':
            res = urllib.parse.unquote(data)
        elif mode == 'encode':
            res = urllib.parse.quote(data)
        elif mode == 'double_decode':
            res = urllib.parse.unquote(urllib.parse.unquote(data))
        elif mode == 'parse':
            p = urllib.parse.urlparse(data)
            return {'status': 'success', 'result': {
                'scheme': p.scheme, 'host': p.netloc, 'path': p.path,
                'query': p.query, 'fragment': p.fragment
            }}
            
        return {'status': 'success', 'result': {'output': res}}
