from core.base_tool import BaseTool, register_tool
from core.exceptions import ExecutionError

@register_tool
class VigenereTool(BaseTool):
    """Vigenere cipher tool."""
    name = 'vigenere'
    category = 'crypto'
    description = 'Vigenere cipher tool'
    tags = ['vigenere', 'encrypt', 'decrypt']
    
    def _setup_options(self):
        self.add_option('DATA', 'Input data', required=True)
        self.add_option('KEY', 'Vigenere key', required=True)
        self.add_option('MODE', 'encrypt/decrypt', required=False, default='decrypt', choices=['encrypt', 'decrypt'])
    
    def run(self) -> dict:
        data = self.get_option('DATA')
        key = self.get_option('KEY')
        mode = self.get_option('MODE')
        
        try:
            if not key:
                raise ValueError("Key is required")
                
            key = [char for char in key.lower() if 'a' <= char <= 'z']
            if not key:
                raise ValueError("Key must contain alphabetic characters")
                
            result = []
            key_index = 0
            
            for char in data:
                if 'a' <= char <= 'z':
                    shift = ord(key[key_index]) - ord('a')
                    if mode == 'decrypt':
                        shift = -shift
                    result.append(chr((ord(char) - ord('a') + shift) % 26 + ord('a')))
                    key_index = (key_index + 1) % len(key)
                elif 'A' <= char <= 'Z':
                    shift = ord(key[key_index]) - ord('a')
                    if mode == 'decrypt':
                        shift = -shift
                    result.append(chr((ord(char) - ord('A') + shift) % 26 + ord('A')))
                    key_index = (key_index + 1) % len(key)
                else:
                    result.append(char)
                    
            return {'status': 'success', 'result': ''.join(result)}
        except Exception as e:
            raise ExecutionError(f"Vigenere operation failed: {str(e)}")
