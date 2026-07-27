from core.base_tool import BaseTool, register_tool
from core.exceptions import ExecutionError

@register_tool
class RobotsParser(BaseTool):
    name = 'robots_parser'
    category = 'web'
    description = 'Robots.txt parser'
    tags = ['web', 'robots', 'parse']

    def _setup_options(self):
        self.add_option('DATA', 'robots.txt content', required=True)

    def run(self) -> dict:
        data = self.get_option('DATA')
        disallowed = []
        allowed = []
        
        for line in data.split('\n'):
            line = line.strip()
            if line.lower().startswith('disallow:'):
                disallowed.append(line.split(':', 1)[1].strip())
            elif line.lower().startswith('allow:'):
                allowed.append(line.split(':', 1)[1].strip())
                
        return {'status': 'success', 'result': {
            'disallowed': disallowed,
            'allowed': allowed
        }}
