from core.base_tool import BaseTool, register_tool
from core.exceptions import ExecutionError

@register_tool
class HexTool(BaseTool):
    """Hex encode/decode tool."""
    name = 'hex'
    category = 'crypto'
    description = 'Hexadecimal encoder and decoder'
    tags = ['hex', 'encode', 'decode']
    
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
                result = data.hex()
            else:
                # Handle space-separated and 0x prefix
                clean_data = data.replace(' ', '').replace('0x', '').replace('\\x', '')
                result = bytes.fromhex(clean_data).decode('utf-8')
            return {'status': 'success', 'result': result}
        except Exception as e:
            raise ExecutionError(f"Hex operation failed: {str(e)}")
