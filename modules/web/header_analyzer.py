from core.base_tool import BaseTool, register_tool
from core.exceptions import ExecutionError

@register_tool
class HeaderAnalyzer(BaseTool):
    name = 'header_analyzer'
    category = 'web'
    description = 'HTTP header analyzer'
    tags = ['web', 'headers', 'security']

    def _setup_options(self):
        self.add_option('DATA', 'Raw headers text', required=True)

    def run(self) -> dict:
        data = self.get_option('DATA')
        headers = {}
        for line in data.strip().split('\n'):
            line = line.strip()
            if not line: continue
            if ':' in line:
                k, v = line.split(':', 1)
                headers[k.strip().lower()] = v.strip()
                
        security_headers = ['content-security-policy', 'strict-transport-security', 'x-frame-options', 'x-content-type-options']
        missing = [h for h in security_headers if h not in headers]
        
        return {'status': 'success', 'result': {
            'parsed_headers': headers,
            'missing_security_headers': missing
        }}
