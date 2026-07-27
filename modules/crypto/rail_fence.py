from core.base_tool import BaseTool, register_tool
from core.exceptions import ExecutionError

@register_tool
class RailFenceCipher(BaseTool):
    """Rail fence cipher encrypt, decrypt, and bruteforce."""
    name = 'rail_fence'
    category = 'crypto'
    description = 'Rail fence cipher operations.'
    tags = ['railfence', 'transposition']

    def _setup_options(self):
        self.add_option('DATA', 'Input data', required=True)
        self.add_option('RAILS', 'Number of rails', required=False, default='3')
        self.add_option('MODE', 'encrypt/decrypt/bruteforce', required=False, default='decrypt', choices=['encrypt', 'decrypt', 'bruteforce'])

    def encrypt(self, text, rails):
        if rails <= 1: return text
        fence = [[] for _ in range(rails)]
        rail = 0
        direction = 1
        for char in text:
            fence[rail].append(char)
            rail += direction
            if rail == rails - 1 or rail == 0:
                direction = -direction
        return ''.join(''.join(row) for row in fence)

    def decrypt(self, text, rails):
        if rails <= 1: return text
        fence = [['\n'] * len(text) for _ in range(rails)]
        rail = 0
        direction = 1
        for i in range(len(text)):
            fence[rail][i] = '*'
            rail += direction
            if rail == rails - 1 or rail == 0:
                direction = -direction
        
        index = 0
        for i in range(rails):
            for j in range(len(text)):
                if fence[i][j] == '*' and index < len(text):
                    fence[i][j] = text[index]
                    index += 1
                    
        result = []
        rail = 0
        direction = 1
        for i in range(len(text)):
            result.append(fence[rail][i])
            rail += direction
            if rail == rails - 1 or rail == 0:
                direction = -direction
        return ''.join(result)

    def run(self) -> dict:
        data = self.get_option('DATA')
        mode = self.get_option('MODE')
        
        try:
            rails = int(self.get_option('RAILS'))
            if mode == 'encrypt':
                return {'status': 'success', 'result': self.encrypt(data, rails)}
            elif mode == 'decrypt':
                return {'status': 'success', 'result': self.decrypt(data, rails)}
            elif mode == 'bruteforce':
                results = []
                max_rails = max(2, len(data) // 2 + 1)
                for r in range(2, max_rails + 1):
                    results.append(f"Rails {r}: {self.decrypt(data, r)}")
                return {'status': 'success', 'result': '\n'.join(results)}
        except Exception as e:
            raise ExecutionError(f"Rail Fence error: {str(e)}")
