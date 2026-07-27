from core.base_tool import BaseTool, register_tool
from core.exceptions import ExecutionError

@register_tool
class PwntoolsTemplate(BaseTool):
    name = 'pwntools_template'
    category = 'pwn'
    description = 'Generate pwntools exploit template'
    tags = ['pwn', 'pwntools', 'template']

    def _setup_options(self):
        self.add_option('BINARY', 'Binary name', required=False, default='./vuln')
        self.add_option('HOST', 'Remote host', required=False, default='127.0.0.1')
        self.add_option('PORT', 'Remote port', required=False, default='1337')
        self.add_option('TYPE', 'Exploit type', required=False, default='bof')

    def run(self) -> dict:
        binary = self.get_option('BINARY')
        host = self.get_option('HOST')
        port = self.get_option('PORT')
        
        template = f'''#!/usr/bin/env python3
from pwn import *

context.binary = elf = ELF('{binary}')
# libc = ELF('./libc.so.6')

def start():
    if args.REMOTE:
        return remote('{host}', {port})
    else:
        return process(elf.path)

io = start()

# payload = b'A' * 64
# io.sendline(payload)

io.interactive()
'''
        return {'status': 'success', 'result': {'template': template}}
