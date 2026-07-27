from core.base_tool import BaseTool, register_tool
from core.exceptions import ExecutionError

@register_tool
class BaconCipher(BaseTool):
    """Bacon cipher encode and decode."""
    name = 'bacon'
    category = 'crypto'
    description = 'Bacon cipher encoder/decoder (Standard I=J, U=V).'
    tags = ['bacon', 'encode', 'decode']

    BACON_DICT = {
        'A': 'AAAAA', 'B': 'AAAAB', 'C': 'AAABA', 'D': 'AAABB', 'E': 'AABAA',
        'F': 'AABAB', 'G': 'AABBA', 'H': 'AABBB', 'I': 'ABAAA', 'J': 'ABAAA',
        'K': 'ABAAB', 'L': 'ABABA', 'M': 'ABABB', 'N': 'ABBAA', 'O': 'ABBAB',
        'P': 'ABBBA', 'Q': 'ABBBB', 'R': 'BAAAA', 'S': 'BAAAB', 'T': 'BAABA',
        'U': 'BAABB', 'V': 'BAABB', 'W': 'BABAA', 'X': 'BABAB', 'Y': 'BABBA',
        'Z': 'BABBB'
    }

    def _setup_options(self):
        self.add_option('DATA', 'Input data', required=True)
        self.add_option('MODE', 'encode/decode', required=False, default='decode', choices=['encode', 'decode'])

    def run(self) -> dict:
        data = self.get_option('DATA').upper()
        mode = self.get_option('MODE')

        try:
            if mode == 'encode':
                result = ""
                for char in data:
                    if char in self.BACON_DICT:
                        result += self.BACON_DICT[char] + " "
                return {'status': 'success', 'result': result.strip()}
            
            else: # decode
                # Normalize representations
                data_norm = data.replace('0', 'A').replace('1', 'B')
                data_norm = "".join(c for c in data_norm if c in 'AB')
                
                inv_dict = {v: k for k, v in self.BACON_DICT.items() if k not in ['J', 'V']}
                result = ""
                
                for i in range(0, len(data_norm), 5):
                    chunk = data_norm[i:i+5]
                    if len(chunk) == 5:
                        result += inv_dict.get(chunk, '?')
                        
                return {'status': 'success', 'result': result}
        except Exception as e:
            raise ExecutionError(f"Bacon cipher error: {str(e)}")
