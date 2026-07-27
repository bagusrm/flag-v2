from core.base_tool import BaseTool, register_tool
from core.exceptions import ExecutionError

def ext_gcd(a, b):
    if a == 0:
        return b, 0, 1
    g, x1, y1 = ext_gcd(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return g, x, y

def modinv(a, m):
    g, x, y = ext_gcd(a, m)
    if g != 1:
        return None
    return x % m

@register_tool
class AffineCipher(BaseTool):
    """Affine cipher encrypt, decrypt, and bruteforce."""
    name = 'affine'
    category = 'crypto'
    description = 'Affine cipher substitution.'
    tags = ['affine', 'substitution']

    def _setup_options(self):
        self.add_option('DATA', 'Input data', required=True)
        self.add_option('A', 'Multiplier A', required=False, default='1')
        self.add_option('B', 'Shift B', required=False, default='0')
        self.add_option('MODE', 'encrypt/decrypt/bruteforce', required=False, default='bruteforce', choices=['encrypt', 'decrypt', 'bruteforce'])

    def run(self) -> dict:
        data = self.get_option('DATA')
        mode = self.get_option('MODE')
        
        try:
            a_val = int(self.get_option('A'))
            b_val = int(self.get_option('B'))

            if mode == 'encrypt':
                res = ""
                for c in data:
                    if c.isalpha():
                        base = ord('A') if c.isupper() else ord('a')
                        res += chr((a_val * (ord(c) - base) + b_val) % 26 + base)
                    else:
                        res += c
                return {'status': 'success', 'result': res}
            
            elif mode == 'decrypt':
                inv_a = modinv(a_val, 26)
                if not inv_a:
                    raise ExecutionError(f"A={a_val} has no inverse modulo 26.")
                res = ""
                for c in data:
                    if c.isalpha():
                        base = ord('A') if c.isupper() else ord('a')
                        res += chr((inv_a * (ord(c) - base - b_val)) % 26 + base)
                    else:
                        res += c
                return {'status': 'success', 'result': res}
            
            elif mode == 'bruteforce':
                results = []
                for a in range(1, 26):
                    inv_a = modinv(a, 26)
                    if not inv_a:
                        continue
                    for b in range(26):
                        res = ""
                        for c in data:
                            if c.isalpha():
                                base = ord('A') if c.isupper() else ord('a')
                                res += chr((inv_a * (ord(c) - base - b)) % 26 + base)
                            else:
                                res += c
                        results.append(f"A={a}, B={b}: {res}")
                return {'status': 'success', 'result': '\n'.join(results)}
                
        except Exception as e:
            raise ExecutionError(f"Affine Cipher error: {str(e)}")
