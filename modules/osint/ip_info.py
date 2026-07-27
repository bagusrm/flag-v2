import socket
import ipaddress
from core.base_tool import BaseTool, register_tool
from core.exceptions import ExecutionError

@register_tool
class IPInfo(BaseTool):
    name = 'ip_info'
    category = 'osint'
    description = 'Get information about an IP address'
    tags = ['osint', 'ip', 'network']

    def _setup_options(self):
        self.add_option('IP', 'IP address to check', required=True)

    def run(self) -> dict:
        ip_str = self.get_option('IP')
        
        result = {
            'ip': ip_str,
            'valid': False,
            'version': None,
            'is_private': False,
            'is_global': False,
            'reverse_dns': None,
            'error': ''
        }

        try:
            # Validate and parse IP
            ip = ipaddress.ip_address(ip_str)
            result['valid'] = True
            result['version'] = ip.version
            result['is_private'] = ip.is_private
            result['is_global'] = ip.is_global
            result['is_multicast'] = ip.is_multicast
            result['is_loopback'] = ip.is_loopback

            # Reverse DNS
            try:
                result['reverse_dns'] = socket.gethostbyaddr(ip_str)[0]
            except socket.herror:
                result['reverse_dns'] = "No PTR record found"
                
        except ValueError as e:
            result['error'] = str(e)
            raise ExecutionError(f"Invalid IP address: {str(e)}")
        except Exception as e:
            result['error'] = str(e)

        return {'status': 'success', 'result': result}
