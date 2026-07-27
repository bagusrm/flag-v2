from core.base_tool import BaseTool, register_tool
from core.exceptions import ExecutionError

@register_tool
class CaesarTool(BaseTool):
    """Caesar cipher tool."""
    name = 'caesar'
    category = 'crypto'
    description = 'Caesar cipher tool'
    tags = ['caesar', 'encrypt', 'decrypt', 'bruteforce']
    
    def _setup_options(self):
        self.add_option('DATA', 'Input data', required=True)
        self.add_option('MODE', 'encrypt/decrypt/bruteforce', required=False, default='bruteforce', choices=['encrypt', 'decrypt', 'bruteforce'])
        self.add_option('SHIFT', 'Shift value (0-25)', required=False, default=0)
    
    def run(self) -> dict:
        data = self.get_option('DATA')
        mode = self.get_option('MODE')
        
        try:
            if mode == 'bruteforce':
                results = []
                for shift in range(26):
                    res = self._shift_data(data, -shift) # bruteforce typically tries decrypting
                    results.append(f"Shift {shift:02d}: {res}")
                return {'status': 'success', 'result': '\n'.join(results)}
            else:
                shift = int(self.get_option('SHIFT'))
                if mode == 'decrypt':
                    shift = -shift
                result = self._shift_data(data, shift)
                return {'status': 'success', 'result': result}
        except Exception as e:
            raise ExecutionError(f"Caesar operation failed: {str(e)}")

    def _shift_data(self, data: str, shift: int) -> str:
        result = []
        for char in data:
            if 'a' <= char <= 'z':
                result.append(chr((ord(char) - ord('a') + shift) % 26 + ord('a')))
            elif 'A' <= char <= 'Z':
                result.append(chr((ord(char) - ord('A') + shift) % 26 + ord('A')))
            else:
                result.append(char)
        return ''.join(result)
