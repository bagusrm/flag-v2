import os
from core.base_tool import BaseTool, register_tool
from core.exceptions import ExecutionError

@register_tool
class OpcodeViewerTool(BaseTool):
    name = 'opcode_viewer'
    category = 'reverse'
    description = 'Opcode viewer for identifying common byte patterns'
    tags = ['reverse', 'opcode', 'viewer', 'hex']
    
    def _setup_options(self):
        self.add_option('FILE', 'Path to file (optional)', default='')
        self.add_option('DATA', 'Hex string (optional)', default='')
        self.add_option('OFFSET', 'Start offset', default='0')
        self.add_option('LENGTH', 'Bytes to show', default='256')
    
    def run(self) -> dict:
        file_path = self.get_option('FILE')
        hex_data = self.get_option('DATA')
        
        try:
            offset = int(self.get_option('OFFSET'), 0)
            length = int(self.get_option('LENGTH'), 0)
        except ValueError:
            raise ExecutionError("Invalid OFFSET or LENGTH format")
            
        data_bytes = b''
        
        if file_path and os.path.exists(file_path):
            with open(file_path, 'rb') as f:
                f.seek(offset)
                data_bytes = f.read(length)
        elif hex_data:
            try:
                data_bytes = bytes.fromhex(hex_data.replace(' ', ''))[offset:offset+length]
            except ValueError:
                raise ExecutionError("Invalid hex DATA")
        else:
            raise ExecutionError("Must provide FILE or DATA")
            
        patterns = {
            b'\x90\x90\x90\x90': 'NOP sled',
            b'\xcc\xcc\xcc': 'INT3 padding',
            b'\x31\xc0\x50\x68\x2f\x2f\x73\x68': 'Shellcode (execve /bin/sh)'
        }
        
        found_patterns = []
        for pat, desc in patterns.items():
            idx = data_bytes.find(pat)
            if idx != -1:
                found_patterns.append({'offset': hex(offset + idx), 'description': desc})
                
        result = {
            'offset_start': hex(offset),
            'length': len(data_bytes),
            'hex': data_bytes.hex(' '),
            'patterns': found_patterns
        }
        
        return {'status': 'success', 'result': result}
