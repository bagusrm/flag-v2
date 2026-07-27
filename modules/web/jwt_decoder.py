from core.base_tool import BaseTool, register_tool
from core.exceptions import ExecutionError
import base64
import json

@register_tool
class JwtDecoder(BaseTool):
    name = 'jwt_decoder'
    category = 'web'
    description = 'JWT token decoder'
    tags = ['web', 'jwt', 'decode']

    def _setup_options(self):
        self.add_option('TOKEN', 'JWT string', required=True)

    def _decode_b64url(self, s):
        s = s + '=' * (4 - len(s) % 4)
        return base64.urlsafe_b64decode(s).decode('utf-8')

    def run(self) -> dict:
        token = self.get_option('TOKEN')
        parts = token.split('.')
        
        if len(parts) != 3:
            raise ExecutionError("Invalid JWT token format")
            
        try:
            header = json.loads(self._decode_b64url(parts[0]))
            payload = json.loads(self._decode_b64url(parts[1]))
            signature = parts[2]
            
            issues = []
            if header.get('alg', '').lower() == 'none':
                issues.append("VULNERABILITY: Algorithm set to 'none'")
                
            return {'status': 'success', 'result': {
                'header': header,
                'payload': payload,
                'signature': signature,
                'issues': issues
            }}
        except Exception as e:
            raise ExecutionError(f"Error decoding JWT: {str(e)}")
