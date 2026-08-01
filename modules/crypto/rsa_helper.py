from core.base_tool import BaseTool, register_tool
from core.exceptions import ExecutionError
from math import gcd

@register_tool
class RsaHelper(BaseTool):
    name = 'rsa_helper'
    category = 'crypto'
    description = 'RSA analysis, parameter parser, Coppersmith partial-key solver script generator'
    tags = ['crypto', 'rsa', 'coppersmith', 'factor', 'solver']

    def _setup_options(self):
        self.add_option('N', 'Modulus N', required=False)
        self.add_option('E', 'Public exponent e', default='65537')
        self.add_option('B', 'Base parameter b', required=False)
        self.add_option('C', 'Ciphertext or tuple C', required=False)
        self.add_option('DP', 'Partial prime leak dp', required=False)
        self.add_option('P', 'Prime p', required=False)
        self.add_option('Q', 'Prime q', required=False)
        self.add_option('MODE', 'analyze/factor/generate/coppersmith', default='analyze', choices=['analyze', 'factor', 'generate', 'coppersmith'])

    def _parse_int(self, val) -> int | None:
        if not val:
            return None
        val_str = str(val).strip()
        if val_str.startswith(('0x', '0X')):
            return int(val_str, 16)
        return int(val_str)

    def run(self) -> dict:
        N = self._parse_int(self.get_option('N'))
        e = self._parse_int(self.get_option('E'))
        b = self._parse_int(self.get_option('B'))
        C_raw = self.get_option('C')
        dp = self._parse_int(self.get_option('DP'))
        p = self._parse_int(self.get_option('P'))
        q = self._parse_int(self.get_option('Q'))
        mode = self.get_option('MODE')

        if mode == 'coppersmith' or (dp and N):
            sage_script = f"""# SageMath Solver for Partial Leakage Coppersmith RSA
N = {N}
e = {e}
b = {b}
C = {C_raw}
dp = {dp}

# Step 1: Coppersmith Attack to recover q
PR.<x> = PolynomialRing(Zmod(N))
f = dp + x
roots = f.small_roots(X=2^307, beta=0.4)

if roots:
    q = int(dp + roots[0])
    p = N // q
    print(f"[+] Recovered q = {{q}}")
    print(f"[+] Recovered p = {{p}}")
    
    c = pow(b, 3, N)
    psi = (p - 1)^2 * (q - 1)^2
    d0 = (psi - pow(e, -1, psi)) % psi
    
    def mul(a, b, c, N):
        u1, v1, w1 = a
        u2, v2, w2 = b
        return ((u1*u2 + c*(v1*w2 + v2*w1)) % N,
                (u1*v2 + u2*v1 + c*w1*w2) % N,
                (u1*w2 + u2*w1 + v1*v2) % N)

    def power(a, k, c, N):
        r = (1, 0, 0)
        while k:
            if k & 1:
                r = mul(r, a, c, N)
            a = mul(a, a, c, N)
            k >>= 1
        return r

    M = power(C, psi - d0, c, N)
    u, v = M[1], M[2]
    m = (u * pow(v, -1, N)) % N
    
    from Crypto.Util.number import long_to_bytes
    print("[+] FLAG:", long_to_bytes(int(m)).decode(errors='ignore'))
else:
    print("[-] Coppersmith attack failed.")
"""
            return {
                'status': 'success',
                'result': {
                    'analysis': 'Coppersmith Partial Prime Leakage Attack Detected',
                    'sage_solver_script': sage_script
                }
            }

        # General RSA analysis mode
        res_info = {
            'N_bits': N.bit_length() if N else None,
            'e': e,
            'has_dp_leak': dp is not None
        }

        return {'status': 'success', 'result': res_info}
