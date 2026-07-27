import os
import struct
from core.base_tool import BaseTool, register_tool
from core.exceptions import ExecutionError

@register_tool
class SectionViewerTool(BaseTool):
    name = 'section_viewer'
    category = 'reverse'
    description = 'Binary section viewer (ELF/PE)'
    tags = ['reverse', 'sections', 'elf', 'pe']
    
    def _setup_options(self):
        self.add_option('FILE', 'Path to file', required=True)
    
    def run(self) -> dict:
        file_path = self.get_option('FILE')
        if not os.path.exists(file_path):
            raise ExecutionError(f"File not found: {file_path}")
            
        sections = []
        fmt = 'unknown'
        
        try:
            with open(file_path, 'rb') as f:
                magic = f.read(4)
                
                if magic == b'\x7fELF':
                    fmt = 'ELF'
                    f.seek(4)
                    ei_class = f.read(1)[0]
                    f.seek(0)
                    
                    if ei_class == 1:
                        f.seek(32)
                        e_shoff = struct.unpack('<I', f.read(4))[0]
                        f.seek(46)
                        e_shentsize = struct.unpack('<H', f.read(2))[0]
                        e_shnum = struct.unpack('<H', f.read(2))[0]
                    else:
                        f.seek(40)
                        e_shoff = struct.unpack('<Q', f.read(8))[0]
                        f.seek(58)
                        e_shentsize = struct.unpack('<H', f.read(2))[0]
                        e_shnum = struct.unpack('<H', f.read(2))[0]
                        
                    for i in range(e_shnum):
                        f.seek(e_shoff + i * e_shentsize)
                        if ei_class == 1:
                            sh_name, sh_type, sh_flags, sh_addr, sh_offset, sh_size = struct.unpack('<IIIIII', f.read(24))
                        else:
                            sh_name, sh_type, sh_flags, sh_addr, sh_offset, sh_size = struct.unpack('<IIQQQQ', f.read(40))
                            
                        perms = []
                        if sh_flags & 0x1: perms.append('W')
                        if sh_flags & 0x2: perms.append('A')
                        if sh_flags & 0x4: perms.append('X')
                        
                        sections.append({
                            'index': i,
                            'name_offset': sh_name,
                            'virtual_address': hex(sh_addr),
                            'size': hex(sh_size),
                            'flags': hex(sh_flags),
                            'permissions': ''.join(perms),
                            'is_executable': 'X' in perms
                        })
                        
                elif magic[:2] == b'MZ':
                    fmt = 'PE'
                    f.seek(60)
                    pe_offset = struct.unpack('<I', f.read(4))[0]
                    f.seek(pe_offset)
                    if f.read(4) == b'PE\x00\x00':
                        f.seek(pe_offset + 6)
                        num_sections = struct.unpack('<H', f.read(2))[0]
                        f.seek(pe_offset + 20)
                        opt_hdr_size = struct.unpack('<H', f.read(2))[0]
                        sections_offset = pe_offset + 24 + opt_hdr_size
                        
                        for i in range(num_sections):
                            f.seek(sections_offset + i * 40)
                            sec_hdr = f.read(40)
                            name = sec_hdr[:8].rstrip(b'\x00').decode('ascii', errors='ignore')
                            vsize = struct.unpack('<I', sec_hdr[8:12])[0]
                            vaddr = struct.unpack('<I', sec_hdr[12:16])[0]
                            size = struct.unpack('<I', sec_hdr[16:20])[0]
                            chars = struct.unpack('<I', sec_hdr[36:40])[0]
                            
                            perms = []
                            if chars & 0x20000000: perms.append('X')
                            if chars & 0x40000000: perms.append('R')
                            if chars & 0x80000000: perms.append('W')
                            
                            sections.append({
                                'name': name,
                                'virtual_address': hex(vaddr),
                                'virtual_size': hex(vsize),
                                'raw_size': hex(size),
                                'characteristics': hex(chars),
                                'permissions': ''.join(perms),
                                'is_executable': 'X' in perms
                            })
                            
                else:
                    raise ExecutionError("Unsupported format")
                    
        except Exception as e:
            raise ExecutionError(f"Error parsing sections: {str(e)}")
            
        return {'status': 'success', 'result': {'format': fmt, 'sections': sections}}
