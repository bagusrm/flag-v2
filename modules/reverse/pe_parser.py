import os
import struct
from core.base_tool import BaseTool, register_tool
from core.exceptions import ExecutionError

@register_tool
class PeParserTool(BaseTool):
    name = 'pe_parser'
    category = 'reverse'
    description = 'Parse PE (Windows) binary files (pure Python with struct)'
    tags = ['reverse', 'pe', 'parser', 'windows']
    
    def _setup_options(self):
        self.add_option('FILE', 'Path to file', required=True)
    
    def run(self) -> dict:
        file_path = self.get_option('FILE')
        if not os.path.exists(file_path):
            raise ExecutionError(f"File not found: {file_path}")
            
        try:
            with open(file_path, 'rb') as f:
                dos_header = f.read(64)
                if len(dos_header) < 64 or dos_header[:2] != b'MZ':
                    raise ExecutionError("Not a valid PE file (Missing MZ signature)")
                
                pe_offset = struct.unpack('<I', dos_header[60:64])[0]
                f.seek(pe_offset)
                pe_sig = f.read(4)
                if pe_sig != b'PE\x00\x00':
                    raise ExecutionError("Invalid PE signature")
                
                file_hdr_fmt = '<HHIIIH'
                file_hdr_size = struct.calcsize(file_hdr_fmt)
                file_hdr_data = f.read(file_hdr_size)
                machine, num_sections, timedatestamp, ptr_symtab, num_syms, opt_hdr_size, characteristics = struct.unpack('<HHIIIHH', file_hdr_data)
                
                result = {
                    'dos_header_valid': True,
                    'pe_signature': 'PE\\x00\\x00',
                    'machine': hex(machine),
                    'num_sections': num_sections,
                    'characteristics': hex(characteristics),
                    'optional_header_size': opt_hdr_size
                }
                
                if opt_hdr_size > 0:
                    magic = struct.unpack('<H', f.read(2))[0]
                    f.seek(pe_offset + 4 + file_hdr_size)
                    if magic == 0x10b: # PE32
                        opt_hdr = f.read(96)
                        entry_point = struct.unpack('<I', opt_hdr[16:20])[0]
                        image_base = struct.unpack('<I', opt_hdr[28:32])[0]
                        subsystem = struct.unpack('<H', opt_hdr[68:70])[0]
                    elif magic == 0x20b: # PE32+
                        opt_hdr = f.read(112)
                        entry_point = struct.unpack('<I', opt_hdr[16:20])[0]
                        image_base = struct.unpack('<Q', opt_hdr[24:32])[0]
                        subsystem = struct.unpack('<H', opt_hdr[68:70])[0]
                    else:
                        entry_point = image_base = subsystem = 0
                        
                    result['optional_header'] = {
                        'magic': hex(magic),
                        'entry_point': hex(entry_point),
                        'image_base': hex(image_base),
                        'subsystem': subsystem
                    }
                    
                return {'status': 'success', 'result': result}
        except Exception as e:
            raise ExecutionError(f"Error parsing PE: {str(e)}")
