from core.base_tool import BaseTool, register_tool
from core.exceptions import ExecutionError

@register_tool
class DisasmHelperTool(BaseTool):
    name = 'disasm_helper'
    category = 'reverse'
    description = 'Disassembly helper (x86/x64 reference, syscalls, commands)'
    tags = ['reverse', 'disassembly', 'asm', 'helper']
    
    def _setup_options(self):
        self.add_option('DATA', 'Hex opcodes or instruction name', default='')
        self.add_option('MODE', 'decode/reference/syscall', default='decode')
    
    def run(self) -> dict:
        data = self.get_option('DATA').lower().strip()
        mode = self.get_option('MODE').lower()
        
        result = {}
        
        if mode == 'decode':
            opcodes = {
                '90': 'nop',
                'c3': 'ret',
                'cc': 'int3',
                '50': 'push eax/rax',
                '58': 'pop eax/rax',
                'e8': 'call',
                'eb': 'jmp short',
                'e9': 'jmp'
            }
            if data in opcodes:
                result['decoded'] = opcodes[data]
            else:
                result['decoded'] = 'Unknown or requires full disassembler (try objdump or radare2)'
                
        elif mode == 'reference':
            refs = {
                'mov': 'Moves data from source to destination',
                'push': 'Pushes value onto the stack',
                'pop': 'Pops value from the stack',
                'ret': 'Returns from procedure',
                'call': 'Calls a procedure'
            }
            result['reference'] = refs.get(data, 'Instruction not found in basic reference.')
            
        elif mode == 'syscall':
            syscalls = {
                '60': 'Linux x64 sys_exit',
                '0': 'Linux x64 sys_read',
                '1': 'Linux x64 sys_write',
                '11': 'Linux x86 sys_execve (0xb)'
            }
            result['syscall'] = syscalls.get(data, 'Syscall not found in basic reference.')
            
        else:
            raise ExecutionError("Invalid mode. Choose decode, reference, or syscall.")
            
        result['commands'] = {
            'objdump': 'objdump -M intel -d <binary>',
            'radare2': 'r2 -c "aaa; pdf @ main" <binary>'
        }
            
        return {'status': 'success', 'result': result}
