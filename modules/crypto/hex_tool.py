from core.base_tool import BaseTool, register_tool
from core.exceptions import ExecutionError
import re

@register_tool
class HexTool(BaseTool):
    name = 'hex_tool'
    category = 'crypto'
    description = 'Hex encode/decode with support for Registry hex(3): dumps, comma/space separated bytes'
    tags = ['crypto', 'hex', 'decode', 'encode', 'registry']

    def _setup_options(self):
        self.add_option('DATA', 'Hex string or plain text to process', required=True)
        self.add_option('MODE', 'encode/decode', default='decode', choices=['encode', 'decode'])

    def run(self) -> dict:
        data = str(self.get_option('DATA'))
        mode = self.get_option('MODE')

        try:
            if mode == 'encode':
                hex_str = ''.join(f'{ord(c):02x}' for c in data)
                return {'status': 'success', 'result': hex_str}

            elif mode == 'decode':
                # Clean Registry prefixes like "CopyHistory"=hex(3): or hex:
                cleaned = re.sub(r'^.*?hex(\(\d+\))?:', '', data, flags=re.IGNORECASE)
                
                # Remove non-hex characters except hex digits (keep only 0-9, a-f, A-F)
                hex_only = re.sub(r'[^0-9a-fA-F]', '', cleaned)
                
                if not hex_only:
                    raise ExecutionError("No valid hexadecimal digits found in input.")
                
                if len(hex_only) % 2 != 0:
                    # Pad single odd hex byte if needed
                    hex_only = '0' + hex_only

                raw_bytes = bytes.fromhex(hex_only)
                
                # Try UTF-8 first, fallback to latin-1
                try:
                    text_decoded = raw_bytes.decode('utf-8', errors='ignore')
                except Exception:
                    text_decoded = raw_bytes.decode('latin-1', errors='ignore')

                # Clean null bytes (\x00) commonly found in UTF-16LE Windows Registry dumps
                printable_clean = text_decoded.replace('\x00', '')
                
                # Also extract clean strings list if multiple null-separated strings exist
                parts = [p for p in text_decoded.split('\x00') if p.strip()]

                return {
                    'status': 'success',
                    'result': {
                        'decoded_text': printable_clean,
                        'extracted_paths': parts if len(parts) > 1 else printable_clean,
                        'raw_hex_bytes': len(raw_bytes)
                    }
                }

        except Exception as e:
            if isinstance(e, ExecutionError):
                raise e
            raise ExecutionError(f"Hex processing error: {str(e)}")
