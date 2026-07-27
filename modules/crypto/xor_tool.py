from core.base_tool import BaseTool, register_tool
from core.exceptions import ExecutionError

@register_tool
class XorTool(BaseTool):
    """XOR cipher tool."""
    name = 'xor'
    category = 'crypto'
    description = 'XOR cipher tool (single byte, multi-byte, bruteforce)'
    tags = ['xor', 'encrypt', 'decrypt', 'bruteforce']
    
    def _setup_options(self):
        self.add_option('DATA', 'Input data', required=True)
        self.add_option('MODE', 'encrypt/decrypt/bruteforce', required=False, default='decrypt', choices=['encrypt', 'decrypt', 'bruteforce'])
        self.add_option('KEY', 'Hex key string (optional for bruteforce)', required=False, default='')
    
    def run(self) -> dict:
        data = self.get_option('DATA')
        mode = self.get_option('MODE')
        key_hex = self.get_option('KEY')
        
        try:
            if isinstance(data, str):
                try:
                    data = bytes.fromhex(data)
                except ValueError:
                    data = data.encode('utf-8')
                    
            if mode == 'bruteforce':
                results = []
                for k in range(256):
                    res = bytes(b ^ k for b in data)
                    # Simple printable filter
                    if all(32 <= b <= 126 or b in (9, 10, 13) for b in res):
                        try:
                            results.append(f"Key 0x{k:02x}: {res.decode('utf-8')}")
                        except UnicodeDecodeError:
                            results.append(f"Key 0x{k:02x}: {res}")
                return {'status': 'success', 'result': '\n'.join(results) if results else "No completely printable results found."}
            else:
                if not key_hex:
                    raise ValueError("Key is required for encrypt/decrypt")
                
                key = bytes.fromhex(key_hex.replace('0x', '').replace(' ', ''))
                if not key:
                    raise ValueError("Invalid hex key")
                    
                result = bytearray(len(data))
                for i in range(len(data)):
                    result[i] = data[i] ^ key[i % len(key)]
                    
                try:
                    return {'status': 'success', 'result': result.decode('utf-8')}
                except UnicodeDecodeError:
                    return {'status': 'success', 'result': result.hex()}
        except Exception as e:
            raise ExecutionError(f"XOR operation failed: {str(e)}")
