import base64
from core.base_tool import BaseTool, register_tool
from core.exceptions import ExecutionError

@register_tool
class Base85Tool(BaseTool):
    """Base85 encode/decode tool."""
    name = 'base85'
    category = 'crypto'
    description = 'Base85 (Ascii85) encoder and decoder'
    tags = ['base85', 'ascii85', 'encode', 'decode']
    
    def _setup_options(self):
        self.add_option('DATA', 'Input data', required=True)
        self.add_option('MODE', 'encode/decode', required=False, default='decode', choices=['encode', 'decode'])
    
    def run(self) -> dict:
        data = self.get_option('DATA')
        mode = self.get_option('MODE')
        
        try:
            if mode == 'encode':
                if isinstance(data, str):
                    data = data.encode('utf-8')
                result = base64.b85encode(data).decode('utf-8')
            else:
                result = base64.b85decode(data).decode('utf-8')
            return {'status': 'success', 'result': result}
        except Exception as e:
            raise ExecutionError(f"Base85 operation failed: {str(e)}")
