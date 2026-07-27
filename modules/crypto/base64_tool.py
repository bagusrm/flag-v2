import base64
from core.base_tool import BaseTool, register_tool
from core.exceptions import ExecutionError

@register_tool
class Base64Tool(BaseTool):
    """Base64 encode/decode tool."""
    name = 'base64'
    category = 'crypto'
    description = 'Base64 encoder and decoder'
    tags = ['base64', 'encode', 'decode']
    
    def _setup_options(self):
        self.add_option('DATA', 'Input data', required=True)
        self.add_option('MODE', 'encode/decode', required=False, default='decode', choices=['encode', 'decode'])
        self.add_option('VARIANT', 'standard/urlsafe', required=False, default='standard', choices=['standard', 'urlsafe'])
    
    def run(self) -> dict:
        data = self.get_option('DATA')
        mode = self.get_option('MODE')
        variant = self.get_option('VARIANT')
        
        try:
            if mode == 'encode':
                if isinstance(data, str):
                    data = data.encode('utf-8')
                if variant == 'urlsafe':
                    result = base64.urlsafe_b64encode(data).decode('utf-8')
                else:
                    result = base64.b64encode(data).decode('utf-8')
            else:
                if isinstance(data, str):
                    data += "=" * ((4 - len(data) % 4) % 4)
                if variant == 'urlsafe':
                    result = base64.urlsafe_b64decode(data).decode('utf-8')
                else:
                    result = base64.b64decode(data).decode('utf-8')
            return {'status': 'success', 'result': result}
        except Exception as e:
            raise ExecutionError(f"Base64 operation failed: {str(e)}")
