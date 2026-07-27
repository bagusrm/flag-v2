from core.base_tool import BaseTool, register_tool
from core.exceptions import ExecutionError
import re

@register_tool
class JsBeautifier(BaseTool):
    name = 'js_beautifier'
    category = 'web'
    description = 'JavaScript beautifier/formatter'
    tags = ['web', 'js', 'beautify']

    def _setup_options(self):
        self.add_option('DATA', 'JavaScript code', required=True)

    def run(self) -> dict:
        data = self.get_option('DATA')
        # Very basic formatting for stdlib
        formatted = data.replace(';', ';\n').replace('{', '{\n').replace('}', '}\n')
        strings = re.findall(r'"([^"]*)"|\'([^\']*)\'', data)
        strings = [s[0] or s[1] for s in strings]
        
        return {'status': 'success', 'result': {
            'formatted': formatted,
            'strings': strings
        }}
