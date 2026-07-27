from core.base_tool import BaseTool, register_tool

@register_tool
class GhidraHelperTool(BaseTool):
    name = 'ghidra_helper'
    category = 'reverse'
    description = 'Ghidra project helper'
    tags = ['reverse', 'ghidra', 'decompiler']
    
    def _setup_options(self):
        self.add_option('FILE', 'Path to binary', default='')
        self.add_option('MODE', 'script/tips/headless', default='tips')
    
    def run(self) -> dict:
        mode = self.get_option('MODE').lower()
        filepath = self.get_option('FILE') or 'binary.bin'
        
        result = {}
        
        if mode == 'tips':
            result['tips'] = [
                'Press "G" to go to an address or symbol.',
                'Press "L" to rename a variable or function.',
                'Press ";" to add a comment.',
                'Use "Search > For Strings" to find strings.'
            ]
        elif mode == 'headless':
            result['headless_command'] = f'analyzeHeadless <project_dir> <project_name> -import {filepath}'
        elif mode == 'script':
            result['script'] = '''# Example Ghidra Python (Jython) script
from ghidra.program.model.symbol import SourceType
print("Analyzing...")
currProgram = getCurrentProgram()
print(currProgram.getName())'''

        return {'status': 'success', 'result': result}
