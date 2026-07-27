import os
from core.base_tool import BaseTool, register_tool
from core.exceptions import ExecutionError

@register_tool
class StegsolveHelper(BaseTool):
    name = 'stegsolve_helper'
    category = 'stego'
    description = 'Stegsolve-like operations reference and basic analysis'
    tags = ['stego', 'stegsolve', 'planes', 'xor']

    def _setup_options(self):
        self.add_option('FILE', 'Path to file', required=True)
        self.add_option('MODE', 'Mode: planes/xor/stats/info', required=False, default='info')

    def run(self) -> dict:
        file_path = self.get_option('FILE')
        mode = self.get_option('MODE')
        
        if not os.path.exists(file_path):
            raise ExecutionError(f"File not found: {file_path}")

        result = {
            'file': file_path,
            'mode': mode,
            'message': '',
            'data': {}
        }

        if mode == 'info':
            result['message'] = (
                "For advanced pixel manipulation, it is recommended to use the Stegsolve Java tool "
                "(https://github.com/zardus/ctf-tools/blob/master/stegsolve/install). "
                "Alternatively, you can write a script using the Pillow library in Python."
            )
            result['data']['file_size'] = os.path.getsize(file_path)
            
        elif mode == 'stats':
            result['message'] = "Basic file statistics retrieved. Full image statistics require Pillow."
            result['data']['size_bytes'] = os.path.getsize(file_path)
            
        elif mode == 'planes' or mode == 'xor':
            result['message'] = (
                f"Mode '{mode}' requested. Since this is a pure Python implementation without external "
                "imaging libraries, full image processing is limited. Please use the 'color_splitter' "
                "tool or Stegsolve."
            )

        return {'status': 'success', 'result': result}
