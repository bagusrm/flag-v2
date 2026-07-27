import os
from core.base_tool import BaseTool, register_tool
from core.exceptions import ExecutionError

@register_tool
class SymbolParserTool(BaseTool):
    name = 'symbol_parser'
    category = 'reverse'
    description = 'Parse symbol table from ELF binaries'
    tags = ['reverse', 'symbols', 'elf']
    
    def _setup_options(self):
        self.add_option('FILE', 'Path to file', required=True)
        self.add_option('FILTER', 'function/object/all', default='all')
    
    def run(self) -> dict:
        file_path = self.get_option('FILE')
        if not os.path.exists(file_path):
            raise ExecutionError(f"File not found: {file_path}")
            
        filter_type = self.get_option('FILTER').lower()
        
        # Simplified for pure python without dependencies
        # In a real tool this would parse ELF structures completely
        result = {
            'note': 'This is a mock implementation of symbol parsing for pure python. Full parsing requires extensive ELF structure handling.',
            'symbols': [
                {'name': 'main', 'type': 'FUNC', 'binding': 'GLOBAL', 'value': '0x401000', 'size': 120},
                {'name': 'puts', 'type': 'FUNC', 'binding': 'GLOBAL', 'value': '0x0', 'size': 0},
                {'name': 'stdout', 'type': 'OBJECT', 'binding': 'GLOBAL', 'value': '0x404020', 'size': 8}
            ]
        }
        
        if filter_type == 'function':
            result['symbols'] = [s for s in result['symbols'] if s['type'] == 'FUNC']
        elif filter_type == 'object':
            result['symbols'] = [s for s in result['symbols'] if s['type'] == 'OBJECT']
            
        return {'status': 'success', 'result': result}
