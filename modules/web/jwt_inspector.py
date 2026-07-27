from core.base_tool import BaseTool, register_tool
from core.exceptions import ExecutionError
import base64
import json
import time

@register_tool
class JwtInspector(BaseTool):
    name = 'jwt_inspector'
    category = 'web'
    description = 'JWT deep inspector'
    tags = ['web', 'jwt', 'inspect']

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
            payload = json.loads(self._decode_b64url(parts[1]))
            res = {'claims': payload, 'expired': False}
            
            if 'exp' in payload:
                exp = payload['exp']
                res['expires_at'] = exp
                if time.time() > exp:
                    res['expired'] = True
                    
            if 'iat' in payload:
                res['issued_at'] = payload['iat']
                res['age_seconds'] = time.time() - payload['iat']
                
            return {'status': 'success', 'result': res}
        except Exception as e:
            raise ExecutionError(f"Error inspecting JWT: {str(e)}")
