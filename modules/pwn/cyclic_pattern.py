from core.base_tool import BaseTool, register_tool
from core.exceptions import ExecutionError
import string

@register_tool
class CyclicPattern(BaseTool):
    name = 'cyclic_pattern'
    category = 'pwn'
    description = 'Generate De Bruijn / cyclic pattern'
    tags = ['pwn', 'cyclic', 'pattern']

    def _setup_options(self):
        self.add_option('LENGTH', 'Pattern length', required=True)
        self.add_option('ALPHABET', 'Custom alphabet', required=False, default=string.ascii_lowercase + string.ascii_uppercase + string.digits)

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
        try:
            length = int(self.get_option('LENGTH'))
        except ValueError:
            raise ExecutionError("LENGTH must be an integer")
            
        alphabet = self.get_option('ALPHABET')
        k = len(alphabet)
        n = 4 # Default 4 byte chunks
        
        indices = self._de_bruijn(k, n)
        pattern = ''.join([alphabet[i] for i in indices])
        
        result_pattern = pattern[:length]
        
        return {'status': 'success', 'result': {'pattern': result_pattern, 'length': len(result_pattern)}}
