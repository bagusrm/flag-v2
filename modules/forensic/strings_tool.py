import string
import os
from core.base_tool import BaseTool, register_tool
from core.exceptions import ExecutionError

@register_tool
class StringsTool(BaseTool):
    name = 'strings'
    category = 'forensic'
    description = 'Extract printable strings from a binary file'
    tags = ['forensic', 'strings', 'binary']
    
    def _setup_options(self):
        self.add_option('FILE', 'Path to file', required=True)
        self.add_option('MIN_LENGTH', 'Minimum string length', default='4')
        self.add_option('ENCODING', 'ascii, unicode, or both', default='both')
    
    def run(self) -> dict:
        file_path = self.get_option('FILE')
        min_length = int(self.get_option('MIN_LENGTH'))
        encoding = self.get_option('ENCODING').lower()
        
        if not os.path.exists(file_path):
            raise ExecutionError(f"File not found: {file_path}")
            
        result_strings = []
        
        with open(file_path, 'rb') as f:
            content = f.read()
            
        if encoding in ['ascii', 'both']:
            current_str = []
            for byte in content:
                char = chr(byte)
                if char in string.printable and char not in ('\n', '\r', '\t', '\x0b', '\x0c'):
                    current_str.append(char)
                else:
                    if len(current_str) >= min_length:
                        result_strings.append("".join(current_str))
                    current_str = []
            if len(current_str) >= min_length:
                result_strings.append("".join(current_str))
                
        if encoding in ['unicode', 'both']:
            current_str = []
            for i in range(0, len(content) - 1, 2):
                if content[i+1] == 0:
                    char = chr(content[i])
                    if char in string.printable and char not in ('\n', '\r', '\t', '\x0b', '\x0c'):
                        current_str.append(char)
                    else:
                        if len(current_str) >= min_length:
                            result_strings.append("".join(current_str))
                        current_str = []
                else:
                    if len(current_str) >= min_length:
                        result_strings.append("".join(current_str))
                    current_str = []
            if len(current_str) >= min_length:
                result_strings.append("".join(current_str))
                
        return {'status': 'success', 'result': {'count': len(result_strings), 'strings': result_strings}}
