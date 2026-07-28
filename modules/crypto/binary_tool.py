from core.base_tool import BaseTool, register_tool
from core.exceptions import ExecutionError
from pathlib import Path

@register_tool
class BinaryTool(BaseTool):
    name = 'binary_tool'
    category = 'crypto'
    description = 'Convert text/binary files to/from 8-bit binary representation'
    tags = ['crypto', 'binary', 'encode', 'decode', 'file']

    def _setup_options(self):
        self.add_option('DATA', 'Binary string or text input', required=False)
        self.add_option('FILE', 'Path to binary/text file', required=False)
        self.add_option('MODE', 'encode/decode or read_raw', default='decode', choices=['encode', 'decode', 'read_raw'])

    def run(self) -> dict:
        data = self.get_option('DATA')
        file_path = self.get_option('FILE')
        mode = self.get_option('MODE')

        # If FILE option is provided, read from file
        if file_path:
            p = Path(file_path)
            if not p.exists():
                raise ExecutionError(f"File not found: {file_path}")
            
            if mode == 'read_raw':
                # Read raw bytes and convert to binary string representation
                raw_bytes = p.read_bytes()
                binary_str = ' '.join(f'{b:08b}' for b in raw_bytes)
                ascii_preview = ''.join(chr(b) if 32 <= b <= 126 else '.' for b in raw_bytes)
                return {
                    'status': 'success',
                    'result': {
                        'binary_stream': binary_str[:1000] + ('...' if len(binary_str) > 1000 else ''),
                        'ascii_decoded': ascii_preview[:500],
                        'total_bytes': len(raw_bytes)
                    }
                }
            else:
                try:
                    data = p.read_text(encoding='utf-8', errors='ignore').strip()
                except Exception as e:
                    raise ExecutionError(f"Failed to read file text: {e}")

        if not data:
            raise ExecutionError("Either DATA or FILE must be provided.")

        try:
            if mode == 'encode':
                # Text to binary string
                binary_res = ' '.join(format(ord(c), '08b') for c in data)
                return {'status': 'success', 'result': binary_res}
            
            elif mode == 'decode':
                # Binary string to text
                clean_data = data.replace(' ', '').replace('\n', '').replace('\r', '')
                if not all(c in '01' for c in clean_data):
                    raise ExecutionError("Input contains non-binary characters (only 0 and 1 allowed).")
                
                if len(clean_data) % 8 != 0:
                    raise ExecutionError(f"Binary string length ({len(clean_data)}) must be a multiple of 8.")
                
                chars = []
                for i in range(0, len(clean_data), 8):
                    byte_str = clean_data[i:i+8]
                    chars.append(chr(int(byte_str, 2)))
                
                decoded_text = ''.join(chars)
                return {'status': 'success', 'result': decoded_text}
                
        except Exception as e:
            if isinstance(e, ExecutionError):
                raise e
            raise ExecutionError(f"Binary operation failed: {str(e)}")
