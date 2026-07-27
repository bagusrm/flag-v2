from core.base_tool import BaseTool, register_tool
from core.exceptions import ExecutionError

@register_tool
class Rot13Tool(BaseTool):
    """ROT cipher tool."""
    name = 'rot'
    category = 'crypto'
    description = 'ROT cipher encoder and decoder (default ROT13)'
    tags = ['rot', 'rot13', 'encode', 'decode']
    
    def _setup_options(self):
        self.add_option('DATA', 'Input data', required=True)
        self.add_option('MODE', 'encode/decode', required=False, default='decode', choices=['encode', 'decode'])
        self.add_option('SHIFT', 'Shift value', required=False, default=13)
    
    def run(self) -> dict:
        data = self.get_option('DATA')
        mode = self.get_option('MODE')
        shift = int(self.get_option('SHIFT'))
        
        try:
            if mode == 'decode':
                shift = -shift
                
            result = []
            for char in data:
                if 'a' <= char <= 'z':
                    result.append(chr((ord(char) - ord('a') + shift) % 26 + ord('a')))
                elif 'A' <= char <= 'Z':
                    result.append(chr((ord(char) - ord('A') + shift) % 26 + ord('A')))
                else:
                    result.append(char)
                    
            return {'status': 'success', 'result': ''.join(result)}
        except Exception as e:
            raise ExecutionError(f"ROT operation failed: {str(e)}")
