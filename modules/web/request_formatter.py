from core.base_tool import BaseTool, register_tool
from core.exceptions import ExecutionError

@register_tool
class RequestFormatter(BaseTool):
    name = 'request_formatter'
    category = 'web'
    description = 'HTTP request formatter'
    tags = ['web', 'http', 'request']

    def _setup_options(self):
        self.add_option('DATA', 'Raw HTTP request', required=True)
        self.add_option('FORMAT', 'Format (curl/python/javascript)', required=False, default='curl')

    def run(self) -> dict:
        data = self.get_option('DATA')
        fmt = self.get_option('FORMAT')
        
        lines = data.strip().split('\n')
        if not lines:
            raise ExecutionError("Empty request")
            
        req_line = lines[0].strip().split()
        method = req_line[0] if len(req_line) > 0 else "GET"
        path = req_line[1] if len(req_line) > 1 else "/"
        
        res = "Basic formatter"
        if fmt == 'curl':
            res = f"curl -X {method} http://TARGET{path}"
        elif fmt == 'python':
            res = f"requests.{method.lower()}('http://TARGET{path}')"
            
        return {'status': 'success', 'result': {'formatted': res}}
