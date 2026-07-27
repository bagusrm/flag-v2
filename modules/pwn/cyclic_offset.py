from core.base_tool import BaseTool, register_tool
from core.exceptions import ExecutionError
import string

@register_tool
class CyclicOffset(BaseTool):
    name = 'cyclic_offset'
    category = 'pwn'
    description = 'Find offset in cyclic pattern'
    tags = ['pwn', 'cyclic', 'offset']

    def _setup_options(self):
        self.add_option('VALUE', 'Value to find (hex or ASCII)', required=True)
        self.add_option('LENGTH', 'Pattern length', required=False, default='5000')
        self.add_option('ENDIAN', 'Endianness (little/big)', required=False, default='little')

    def _de_bruijn(self, k, n):
        a = [0] * k * n
        sequence = []
        def db(t, p):
            if t > n:
                if n % p == 0:
                    sequence.extend(a[1:p + 1])
            else:
                a[t] = a[t - p]
                db(t + 1, p)
                for j in range(a[t - p] + 1, k):
                    a[t] = j
                    db(t + 1, t)
        db(1, 1)
        return sequence

    def run(self) -> dict:
        val_str = self.get_option('VALUE')
        length = int(self.get_option('LENGTH'))
        endian = self.get_option('ENDIAN')
        
        # Parse value
        if val_str.startswith('0x'):
            val_bytes = bytes.fromhex(val_str[2:])
            if endian == 'little':
                val_bytes = val_bytes[::-1]
            search_str = val_bytes.decode('ascii', errors='ignore')
        else:
            search_str = val_str
            
        alphabet = string.ascii_lowercase + string.ascii_uppercase + string.digits
        indices = self._de_bruijn(len(alphabet), 4)
        pattern = ''.join([alphabet[i] for i in indices])[:length]
        
        offset = pattern.find(search_str)
        if offset == -1:
            raise ExecutionError("Value not found in pattern")
            
        return {'status': 'success', 'result': {'offset': offset}}
