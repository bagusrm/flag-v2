from core.base_tool import BaseTool, register_tool
from core.exceptions import ExecutionError
import base64
import binascii
import urllib.parse
import string

@register_tool
class AutoDetect(BaseTool):
    """Auto-detect encoding tool for CTF."""
    name = 'auto_detect'
    category = 'crypto'
    description = 'Recursively decode common encodings.'
    tags = ['decode', 'auto', 'base64', 'hex']

    def _setup_options(self):
        self.add_option('DATA', 'Input data', required=True)
        self.add_option('MAX_DEPTH', 'Max recursion depth', required=False, default='3')

    def is_printable(self, text):
        if not isinstance(text, str):
            return False
        return all(c in string.printable for c in text)

    def attempt_decodes(self, text):
        results = {}
        
        # Base64
        try:
            res = base64.b64decode(text).decode('utf-8')
            if res and res != text and self.is_printable(res):
                results['Base64'] = res
        except: pass
        
        # Base32
        try:
            res = base64.b32decode(text).decode('utf-8')
            if res and res != text and self.is_printable(res):
                results['Base32'] = res
        except: pass

        # Base16 / Hex
        try:
            if all(c in string.hexdigits for c in text):
                res = bytes.fromhex(text).decode('utf-8')
                if res and res != text and self.is_printable(res):
                    results['Hex'] = res
        except: pass
        
        # URL
        try:
            res = urllib.parse.unquote(text)
            if res and res != text:
                results['URL'] = res
        except: pass
        
        # Binary
        try:
            text_clean = text.replace(' ', '')
            if all(c in '01' for c in text_clean) and len(text_clean) % 8 == 0:
                res = ''.join(chr(int(text_clean[i:i+8], 2)) for i in range(0, len(text_clean), 8))
                if res and res != text and self.is_printable(res):
                    results['Binary'] = res
        except: pass

        # ROT13
        try:
            res = text.translate(str.maketrans(
                string.ascii_uppercase + string.ascii_lowercase,
                string.ascii_uppercase[13:] + string.ascii_uppercase[:13] +
                string.ascii_lowercase[13:] + string.ascii_lowercase[:13]
            ))
            if res and res != text:
                results['ROT13'] = res
        except: pass
        
        # Base85 / Ascii85
        try:
            res = base64.a85decode(text.encode('utf-8')).decode('utf-8')
            if res and res != text and self.is_printable(res):
                results['Base85'] = res
        except: pass

        # Base58
        try:
            b58_alphabet = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
            if all(c in b58_alphabet for c in text):
                num = 0
                for char in text:
                    num = num * 58 + b58_alphabet.index(char)
                res = num.to_bytes((num.bit_length() + 7) // 8, 'big').decode('utf-8')
                if res and res != text and self.is_printable(res):
                    results['Base58'] = res
        except: pass

        # Morse
        try:
            morse_dict = {
                '.-': 'A', '-...': 'B', '-.-.': 'C', '-..': 'D', '.': 'E', '..-.': 'F',
                '--.': 'G', '....': 'H', '..': 'I', '.---': 'J', '-.-': 'K', '.-..': 'L',
                '--': 'M', '-.': 'N', '---': 'O', '.--.': 'P', '--.-': 'Q', '.-.': 'R',
                '...': 'S', '-': 'T', '..-': 'U', '...-': 'V', '.--': 'W', '-..-': 'X',
                '-.--': 'Y', '--..': 'Z', '.----': '1', '..---': '2', '...--': '3',
                '....-': '4', '.....': '5', '-....': '6', '--...': '7', '---..': '8',
                '----.': '9', '-----': '0'
            }
            parts = text.split()
            if all(p in morse_dict or p == '/' for p in parts):
                res = ''.join(morse_dict.get(p, ' ' if p == '/' else '') for p in parts)
                if res and res != text:
                    results['Morse'] = res
        except: pass

        return results

    def run(self) -> dict:
        initial_data = self.get_option('DATA')
        try:
            max_depth = int(self.get_option('MAX_DEPTH'))
        except ValueError:
            max_depth = 3

        queue = [(initial_data, [])]
        found = []
        
        try:
            while queue:
                current_text, path = queue.pop(0)
                if len(path) >= max_depth:
                    continue
                    
                decodes = self.attempt_decodes(current_text)
                for enc, dec_text in decodes.items():
                    new_path = path + [enc]
                    found.append((new_path, dec_text))
                    queue.append((dec_text, new_path))
                    
            if not found:
                return {'status': 'success', 'result': 'No valid decodings found.'}
                
            # Sort by path length (shorter first) and printable ratio
            found.sort(key=lambda x: (len(x[0]), -sum(1 for c in x[1] if c in string.printable)/max(1, len(x[1]))))
            
            output = []
            for path, text in found:
                path_str = " -> ".join(path)
                output.append(f"[{path_str}]\n{text}\n")
                
            return {'status': 'success', 'result': '\n'.join(output)}
        except Exception as e:
            raise ExecutionError(f"Auto Detect error: {str(e)}")
