from core.base_tool import BaseTool, register_tool
from core.exceptions import ExecutionError

@register_tool
class BinaryTool(BaseTool):
    """Binary encode/decode tool."""
    name = 'binary'
    category = 'crypto'
    description = 'Binary string encoder and decoder'
    tags = ['binary', 'encode', 'decode']
    
    def _setup_options(self):
        self.add_option('DATA', 'Input data', required=True)
        self.add_option('MODE', 'encode/decode', required=False, default='decode', choices=['encode', 'decode'])
    
    def run(self) -> dict:
        data = self.get_option('DATA')
        mode = self.get_option('MODE')
        
        try:
            if mode == 'encode':
                if isinstance(data, str):
                    data = data.encode('utf-8')
                result = ' '.join(f'{b:08b}' for b in data)
            else:
                clean_data = data.replace(' ', '')
                if len(clean_data) % 8 != 0:
                    raise ValueError("Binary string length must be a multiple of 8")
                b_array = bytearray()
                for i in range(0, len(clean_data), 8):
                    byte_str = clean_data[i:i+8]
                    b_array.append(int(byte_str, 2))
                result = b_array.decode('utf-8')
            return {'status': 'success', 'result': result}
        except Exception as e:
            raise ExecutionError(f"Binary operation failed: {str(e)}")
