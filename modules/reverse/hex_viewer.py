import os
from core.base_tool import BaseTool, register_tool
from core.exceptions import ExecutionError

@register_tool
class HexViewerTool(BaseTool):
    name = 'hex_viewer'
    category = 'reverse'
    description = 'Interactive hex viewer'
    tags = ['reverse', 'hex', 'viewer']
    
    def _setup_options(self):
        self.add_option('FILE', 'Path to file', required=True)
        self.add_option('OFFSET', 'Start offset', default='0')
        self.add_option('LENGTH', 'Bytes to display', default='512')
        self.add_option('WIDTH', 'Bytes per line', default='16')
        self.add_option('HIGHLIGHT', 'Hex pattern to highlight', default='')
    
    def run(self) -> dict:
        file_path = self.get_option('FILE')
        if not os.path.exists(file_path):
            raise ExecutionError(f"File not found: {file_path}")
            
        try:
            offset = int(self.get_option('OFFSET'), 0)
            length = int(self.get_option('LENGTH'), 0)
            width = int(self.get_option('WIDTH'), 0)
        except ValueError:
            raise ExecutionError("Invalid OFFSET, LENGTH, or WIDTH format")
            
        highlight = self.get_option('HIGHLIGHT').replace(' ', '').lower()
        
        with open(file_path, 'rb') as f:
            f.seek(offset)
            data = f.read(length)
            
        lines = []
        for i in range(0, len(data), width):
            chunk = data[i:i+width]
            hex_part = ' '.join(f'{b:02x}' for b in chunk)
            ascii_part = ''.join(chr(b) if 32 <= b <= 126 else '.' for b in chunk)
            lines.append(f'{offset + i:08x}  {hex_part:<{width*3}} |{ascii_part}|')
            
        result = {
            'offset': hex(offset),
            'length': len(data),
            'hexdump': '\n'.join(lines),
            'highlight_found': highlight in data.hex() if highlight else False
        }
        
        return {'status': 'success', 'result': result}
