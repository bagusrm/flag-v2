from core.base_tool import BaseTool, register_tool
from core.exceptions import ExecutionError

def gcd(a, b):
    while b:
        a, b = b, a % b
    return a

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
        raise Exception('Modular inverse does not exist')
    else:
        return x % m

@register_tool
class RSAHelper(BaseTool):
    """RSA analysis and calculation helper."""
    name = 'rsa_helper'
    category = 'crypto'
    description = 'Analyze RSA parameters, factor small N, and decrypt.'
    tags = ['rsa', 'factor', 'decrypt']

    def _setup_options(self):
        self.add_option('N', 'Modulus', required=False, default='')
        self.add_option('E', 'Public Exponent', required=False, default='65537')
        self.add_option('D', 'Private Exponent', required=False, default='')
        self.add_option('P', 'Prime 1', required=False, default='')
        self.add_option('Q', 'Prime 2', required=False, default='')
        self.add_option('C', 'Ciphertext', required=False, default='')
        self.add_option('MODE', 'analyze/factor/decrypt/generate', required=False, default='analyze', choices=['analyze', 'factor', 'decrypt', 'generate'])

    def _parse_int(self, val):
        if not val:
            return None
        if val.startswith('0x') or val.startswith('0X'):
            return int(val, 16)
        return int(val)

    def run(self) -> dict:
        mode = self.get_option('MODE')
        try:
            n = self._parse_int(self.get_option('N'))
            e = self._parse_int(self.get_option('E'))
            d = self._parse_int(self.get_option('D'))
            p = self._parse_int(self.get_option('P'))
            q = self._parse_int(self.get_option('Q'))
            c = self._parse_int(self.get_option('C'))

            result = []

            if mode == 'analyze':
                result.append("=== RSA Analysis ===")
                result.append("Common attacks:")
                result.append("- Small N (factorization)")
                result.append("- Small e (cube root attack)")
                result.append("- Wiener's attack (small d)")
                result.append("- Hastad's Broadcast (same M, small e, multiple N)")
                result.append("- Common Modulus (same N, different e)")
            
            elif mode == 'factor':
                if not n:
                    raise ExecutionError("N is required for factoring.")
                if n > 10**12:
                    result.append("N is too large for trial division, try using factordb.")
                else:
                    found = False
                    for i in range(2, min(10**6, int(n**0.5) + 1)):
                        if n % i == 0:
                            p_found, q_found = i, n // i
                            result.append(f"Factored N: p = {p_found}, q = {q_found}")
                            found = True
                            break
                    if not found:
                        result.append("Could not factor N with trial division.")
            
            elif mode == 'generate':
                if p and q and e:
                    phi = (p - 1) * (q - 1)
                    d_gen = modinv(e, phi)
                    n_gen = p * q
                    result.append(f"N = {n_gen}\nD = {d_gen}")
                else:
                    raise ExecutionError("P, Q, and E required to generate D and N.")
            
            elif mode == 'decrypt':
                if d and n and c:
                    m = pow(c, d, n)
                    result.append(f"Decrypted M: {m}")
                    try:
                        m_bytes = m.to_bytes((m.bit_length() + 7) // 8, 'big')
                        result.append(f"Decrypted M (ascii): {m_bytes.decode(errors='ignore')}")
                    except:
                        pass
                elif p and q and e and c:
                    n_calc = p * q
                    phi = (p - 1) * (q - 1)
                    d_calc = modinv(e, phi)
                    m = pow(c, d_calc, n_calc)
                    result.append(f"Calculated D: {d_calc}")
                    result.append(f"Decrypted M: {m}")
                else:
                    raise ExecutionError("Need D, N, C or P, Q, E, C for decryption.")
                    
            return {'status': 'success', 'result': "\n".join(result)}
        except Exception as err:
            raise ExecutionError(f"RSA Helper Error: {str(err)}")
