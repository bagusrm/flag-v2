from core.base_tool import BaseTool, register_tool
from core.exceptions import ExecutionError

@register_tool
class LibcHelper(BaseTool):
    name = 'libc_helper'
    category = 'pwn'
    description = 'Libc database helper'
    tags = ['pwn', 'libc', 'database']

    def _setup_options(self):
        self.add_option('FUNCTION', 'Function name', required=False, default='')
        self.add_option('ADDRESS', 'Leaked address', required=False, default='')
        self.add_option('MODE', 'Mode: info/lookup', required=False, default='info')

    def run(self) -> dict:
        func = self.get_option('FUNCTION')
        addr = self.get_option('ADDRESS')
        mode = self.get_option('MODE')
        
        res = {}
        if func and addr:
            offset = addr[-3:]
            res['url1'] = f"https://libc.rip/?symbol={func}&address={offset}"
            res['url2'] = f"https://libc.blukat.me/?q={func}%3A{offset}"
            res['suggestion'] = f"Look up {func} ending in {offset}"
        else:
            res['info'] = "Provide FUNCTION and ADDRESS for lookups."
            
        return {'status': 'success', 'result': res}
