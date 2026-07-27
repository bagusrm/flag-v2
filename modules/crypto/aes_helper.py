from core.base_tool import BaseTool, register_tool
from core.exceptions import ExecutionError

@register_tool
class AESHelper(BaseTool):
    """AES helper tool to parse parameters and generate scripts."""
    name = 'aes_helper'
    category = 'crypto'
    description = 'Parse AES parameters and generate Python pycryptodome solve scripts.'
    tags = ['aes', 'script', 'generate']

    def _setup_options(self):
        self.add_option('KEY', 'AES Key in hex', required=False, default='')
        self.add_option('IV', 'Initialization Vector in hex', required=False, default='')
        self.add_option('CIPHERTEXT', 'Ciphertext in hex', required=False, default='')
        self.add_option('PLAINTEXT', 'Plaintext for encryption (hex/string)', required=False, default='')
        self.add_option('MODE', 'AES mode (info/ecb/cbc/ctr/gcm)', required=False, default='info', choices=['info', 'ecb', 'cbc', 'ctr', 'gcm'])

    def run(self) -> dict:
        key = self.get_option('KEY')
        iv = self.get_option('IV')
        ctx = self.get_option('CIPHERTEXT')
        ptx = self.get_option('PLAINTEXT')
        mode = self.get_option('MODE').lower()

        try:
            result = []
            if mode == 'info':
                result.append("=== AES Modes Info ===")
                result.append("ECB: Electronic Codebook. No IV. Patterns are preserved.")
                result.append("CBC: Cipher Block Chaining. Needs IV. Each block XORed with previous ciphertext.")
                result.append("CTR: Counter. Needs IV/Nonce. Turns block cipher into stream cipher.")
                result.append("GCM: Galois/Counter Mode. Authenticated encryption.")
            else:
                key_size = len(key) * 4 if key else 0
                if key and key_size not in (128, 192, 256):
                    result.append(f"Warning: Key size is {key_size} bits, which is not standard for AES (128/192/256).")
                elif key:
                    result.append(f"AES Key Size: {key_size} bits")
                
                result.append("\n=== Generated PyCryptodome Script ===")
                result.append("from Crypto.Cipher import AES")
                if key:
                    result.append(f"key = bytes.fromhex('{key}')")
                if iv:
                    result.append(f"iv = bytes.fromhex('{iv}')")
                if ctx:
                    result.append(f"ciphertext = bytes.fromhex('{ctx}')")
                
                mode_str = f"AES.MODE_{mode.upper()}"
                
                if mode == 'ecb':
                    result.append(f"cipher = AES.new(key, {mode_str})")
                else:
                    result.append(f"cipher = AES.new(key, {mode_str}, iv=iv)")
                
                if ctx:
                    result.append("plaintext = cipher.decrypt(ciphertext)")
                    result.append("print(plaintext)")
                
            return {'status': 'success', 'result': "\n".join(result)}
        except Exception as e:
            raise ExecutionError(f"Error in AES helper: {str(e)}")
