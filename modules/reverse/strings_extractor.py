import os
import re
from core.base_tool import BaseTool, register_tool
from core.exceptions import ExecutionError

@register_tool
class StringsExtractorTool(BaseTool):
    name = 'strings_extractor'
    category = 'reverse'
    description = 'Extract strings from binary files'
    tags = ['reverse', 'strings', 'extractor']
    
    def _setup_options(self):
        self.add_option('FILE', 'Path to file', required=True)
        self.add_option('MIN_LENGTH', 'Minimum string length', default='4')
        self.add_option('PATTERN', 'Regex filter (optional)', default='')
        self.add_option('ENCODING', 'ascii/unicode/both', default='both')
    
    def run(self) -> dict:
        file_path = self.get_option('FILE')
        try:
            min_len = int(self.get_option('MIN_LENGTH'))
        except ValueError:
            min_len = 4
        pattern_str = self.get_option('PATTERN')
        encoding = self.get_option('ENCODING').lower()
        
        if not os.path.exists(file_path):
            raise ExecutionError(f"File not found: {file_path}")
            
        regex_filter = re.compile(pattern_str) if pattern_str else None
        strings_found = []
        
        with open(file_path, 'rb') as f:
            data = f.read()
            
        if encoding in ['ascii', 'both']:
            ascii_re = re.compile(b'[\x20-\x7E]{' + str(min_len).encode() + b',}')
            for match in ascii_re.finditer(data):
                s = match.group().decode('ascii', errors='ignore')
                if not regex_filter or regex_filter.search(s):
                    strings_found.append({'offset': hex(match.start()), 'type': 'ascii', 'string': s})
                    
        if encoding in ['unicode', 'both']:
            unicode_re = re.compile(b'(?:[\x20-\x7E]\x00){' + str(min_len).encode() + b',}')
            for match in unicode_re.finditer(data):
                s = match.group().decode('utf-16le', errors='ignore')
                if not regex_filter or regex_filter.search(s):
                    strings_found.append({'offset': hex(match.start()), 'type': 'utf-16le', 'string': s})
                    
        strings_found.sort(key=lambda x: int(x['offset'], 16))
        
        return {'status': 'success', 'result': {'count': len(strings_found), 'strings': strings_found}}
