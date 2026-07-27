from core.base_tool import BaseTool, register_tool
from core.exceptions import ExecutionError

@register_tool
class Base58Tool(BaseTool):
    """Base58 encode/decode tool."""
    name = 'base58'
    category = 'crypto'
    description = 'Base58 encoder and decoder using Bitcoin alphabet'
    tags = ['base58', 'encode', 'decode']
    
    ALPHABET = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
    
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
                
                num = int.from_bytes(data, 'big')
                if num == 0:
                    return {'status': 'success', 'result': self.ALPHABET[0] * len(data)}
                
                res = []
                while num > 0:
                    num, mod = divmod(num, 58)
                    res.append(self.ALPHABET[mod])
                
                for b in data:
                    if b == 0:
                        res.append(self.ALPHABET[0])
                    else:
                        break
                        
                result = ''.join(reversed(res))
            else:
                num = 0
                for char in data:
                    num = num * 58 + self.ALPHABET.index(char)
                
                bytes_len = (num.bit_length() + 7) // 8
                res_bytes = num.to_bytes(bytes_len, 'big')
                
                pad = 0
                for char in data:
                    if char == self.ALPHABET[0]:
                        pad += 1
                    else:
                        break
                        
                result = (b'\x00' * pad + res_bytes).decode('utf-8')
            return {'status': 'success', 'result': result}
        except Exception as e:
            raise ExecutionError(f"Base58 operation failed: {str(e)}")
