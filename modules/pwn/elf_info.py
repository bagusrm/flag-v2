from core.base_tool import BaseTool, register_tool
from core.exceptions import ExecutionError
import os
import struct

@register_tool
class ElfInfo(BaseTool):
    name = 'elf_info'
    category = 'pwn'
    description = 'Detailed ELF binary information'
    tags = ['pwn', 'elf', 'info']

    def _setup_options(self):
        self.add_option('FILE', 'ELF file to analyze', required=True)

    def run(self) -> dict:
        filepath = self.get_option('FILE')
        if not os.path.exists(filepath):
            raise ExecutionError(f"File not found: {filepath}")
            
        info = {}
        try:
            with open(filepath, 'rb') as f:
                header = f.read(64)
                if not header.startswith(b'\x7fELF'):
                    raise ExecutionError("Not an ELF file")
                
                ei_class = header[4]
                ei_data = header[5]
                
                info['architecture'] = '64-bit' if ei_class == 2 else '32-bit'
                info['endianness'] = 'Big-endian' if ei_data == 2 else 'Little-endian'
                
        except Exception as e:
            raise ExecutionError(f"Error parsing ELF: {str(e)}")
            
        return {'status': 'success', 'result': info}
