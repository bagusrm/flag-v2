from core.base_tool import BaseTool, register_tool
from core.exceptions import ExecutionError
import os
import struct

@register_tool
class ChecksecWrapper(BaseTool):
    name = 'checksec_wrapper'
    category = 'pwn'
    description = 'Binary security checks (pure Python for ELF)'
    tags = ['pwn', 'checksec', 'elf']

    def _setup_options(self):
        self.add_option('FILE', 'ELF file to check', required=True)

    def run(self) -> dict:
        filepath = self.get_option('FILE')
        if not os.path.exists(filepath):
            raise ExecutionError(f"File not found: {filepath}")
        
        result = {'NX': 'Unknown', 'PIE': 'Unknown', 'Canary': 'Unknown', 'RELRO': 'Unknown', 'Stripped': 'Unknown'}
        try:
            with open(filepath, 'rb') as f:
                header = f.read(64)
                if not header.startswith(b'\x7fELF'):
                    raise ExecutionError("Not an ELF file")
                
                # Simplified check for educational purposes
                result['Info'] = "Basic ELF header detected. Full checks require complete section header parsing."
        except Exception as e:
            raise ExecutionError(f"Error checking binary: {str(e)}")
            
        return {'status': 'success', 'result': result}
