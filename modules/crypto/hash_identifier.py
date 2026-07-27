from core.base_tool import BaseTool, register_tool
from core.exceptions import ExecutionError
import re

@register_tool
class HashIdentifier(BaseTool):
    """Hash type identifier tool."""
    name = 'hash_identifier'
    category = 'crypto'
    description = 'Identify hash types based on length and character set.'
    tags = ['hash', 'identify']

    def _setup_options(self):
        self.add_option('HASH', 'The hash string', required=True)

    def run(self) -> dict:
        h = self.get_option('HASH').strip()
        length = len(h)
        is_hex = all(c in '0123456789abcdefABCDEF' for c in h)
        
        results = []
        try:
            if length == 8 and is_hex:
                results.append("CRC32")
            elif length == 32 and is_hex:
                results.append("MD5")
                results.append("MD4")
                results.append("NTLM")
            elif length == 40 and is_hex:
                results.append("SHA-1")
                results.append("MySQL 4.1+")
            elif length == 56 and is_hex:
                results.append("SHA-224")
            elif length == 64 and is_hex:
                results.append("SHA-256")
                results.append("GOST")
            elif length == 96 and is_hex:
                results.append("SHA-384")
            elif length == 128 and is_hex:
                results.append("SHA-512")
                results.append("Whirlpool")
            elif h.startswith('$2') and len(h) >= 59:
                results.append("bcrypt")
            elif h.startswith('$1$') and len(h) == 34:
                results.append("MD5 Crypt")
            elif h.startswith('$6$') and len(h) >= 86:
                results.append("SHA-512 Crypt")
            elif h.startswith('$5$') and len(h) >= 43:
                results.append("SHA-256 Crypt")
            
            if not results:
                results.append("Unknown hash type.")
                
            output = "Possible hash types:\n" + "\n".join(f"- {r}" for r in results)
            return {'status': 'success', 'result': output}
        except Exception as e:
            raise ExecutionError(f"Hash Identifier error: {str(e)}")
