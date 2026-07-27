from core.base_tool import BaseTool, register_tool
from core.exceptions import ExecutionError

@register_tool
class AsmHelperTool(BaseTool):
    name = 'asm_helper'
    category = 'reverse'
    description = 'Assembly language reference helper'
    tags = ['reverse', 'asm', 'reference', 'assembly']
    
    def _setup_options(self):
        self.add_option('QUERY', 'Instruction or topic', required=True)
        self.add_option('ARCH', 'x86/x64/arm', default='x64')
    
    def run(self) -> dict:
        query = self.get_option('QUERY').lower()
        arch = self.get_option('ARCH').lower()
        
        info = {
            'cdecl': 'Caller cleans the stack. Arguments pushed right-to-left.',
            'stdcall': 'Callee cleans the stack. Arguments pushed right-to-left.',
            'system v amd64 abi': 'First 6 args in RDI, RSI, RDX, RCX, R8, R9. Rest on stack.',
            'mov': 'Copies data from source to destination',
            'lea': 'Load Effective Address - computes address but doesn\'t dereference',
            'push': 'Pushes onto stack, decrements RSP',
            'pop': 'Pops from stack, increments RSP'
        }
        
        result = {
            'arch': arch,
            'query': query,
            'result': info.get(query, f"No detailed info for '{query}' in {arch}.")
        }
        
        return {'status': 'success', 'result': result}
