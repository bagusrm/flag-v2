from core.base_tool import BaseTool, register_tool
from core.exceptions import ExecutionError
import json

@register_tool
class ResponseBeautifier(BaseTool):
    name = 'response_beautifier'
    category = 'web'
    description = 'HTTP response beautifier'
    tags = ['web', 'http', 'response']

    def _setup_options(self):
        self.add_option('DATA', 'Raw HTTP response', required=True)

    def run(self) -> dict:
        data = self.get_option('DATA')
        parts = data.split('\n\n', 1)
        headers = parts[0]
        body = parts[1] if len(parts) > 1 else ""
        
        # Try JSON format
        try:
            body = json.dumps(json.loads(body), indent=2)
        except:
            pass
            
        return {'status': 'success', 'result': {'headers': headers, 'body': body}}
