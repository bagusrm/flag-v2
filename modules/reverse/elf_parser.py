import os
import struct
from core.base_tool import BaseTool, register_tool
from core.exceptions import ExecutionError

@register_tool
class ElfParserTool(BaseTool):
    name = 'elf_parser'
    category = 'reverse'
    description = 'Parse ELF binary files (pure Python with struct)'
    tags = ['reverse', 'elf', 'parser']
    
    def _setup_options(self):
        self.add_option('FILE', 'Path to file', required=True)
    
    def run(self) -> dict:
        file_path = self.get_option('FILE')
        if not os.path.exists(file_path):
            raise ExecutionError(f"File not found: {file_path}")
            
        try:
            with open(file_path, 'rb') as f:
                e_ident = f.read(16)
                if len(e_ident) < 16 or e_ident[:4] != b'\x7fELF':
                    raise ExecutionError("Not a valid ELF file")
                
                ei_class = e_ident[4]
                ei_data = e_ident[5]
                
                elf_class = '32-bit' if ei_class == 1 else '64-bit' if ei_class == 2 else 'Unknown'
                endian = '<' if ei_data == 1 else '>'
                endian_desc = 'Little Endian' if ei_data == 1 else 'Big Endian'
                
                if ei_class == 1:
                    hdr_fmt = endian + 'HHIIIIIHHHHHH'
                    hdr_size = struct.calcsize(hdr_fmt)
                    hdr_data = f.read(hdr_size)
                    e_type, e_machine, e_version, e_entry, e_phoff, e_shoff, e_flags, e_ehsize, e_phentsize, e_phnum, e_shentsize, e_shnum, e_shstrndx = struct.unpack(hdr_fmt, hdr_data)
                else:
                    hdr_fmt = endian + 'HHIQQQIHHHHHH'
                    hdr_size = struct.calcsize(hdr_fmt)
                    hdr_data = f.read(hdr_size)
                    e_type, e_machine, e_version, e_entry, e_phoff, e_shoff, e_flags, e_ehsize, e_phentsize, e_phnum, e_shentsize, e_shnum, e_shstrndx = struct.unpack(hdr_fmt, hdr_data)

                header = {
                    'magic': e_ident[:4].hex(),
                    'class': elf_class,
                    'endianness': endian_desc,
                    'type': e_type,
                    'machine': e_machine,
                    'entry_point': hex(e_entry),
                    'program_headers_offset': hex(e_phoff),
                    'section_headers_offset': hex(e_shoff),
                    'flags': hex(e_flags)
                }
                
                # Just a basic representation
                result = {
                    'header': header,
                    'program_headers_count': e_phnum,
                    'section_headers_count': e_shnum
                }
                
                return {'status': 'success', 'result': result}
        except Exception as e:
            raise ExecutionError(f"Error parsing ELF: {str(e)}")
