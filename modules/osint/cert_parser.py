import socket
import ssl
from datetime import datetime
from core.base_tool import BaseTool, register_tool
from core.exceptions import ExecutionError

@register_tool
class CertParser(BaseTool):
    name = 'cert_parser'
    category = 'osint'
    description = 'Parse SSL/TLS certificate details'
    tags = ['osint', 'ssl', 'tls', 'certificate']

    def _setup_options(self):
        self.add_option('HOST', 'Hostname to connect to', required=True)
        self.add_option('PORT', 'Port number', required=False, default='443')

    def run(self) -> dict:
        host = self.get_option('HOST')
        port = int(self.get_option('PORT'))
        
        result = {
            'host': host,
            'port': port,
            'subject': {},
            'issuer': {},
            'version': None,
            'sans': [],
            'not_before': None,
            'not_after': None,
            'expired': False
        }

        context = ssl.create_default_context()
        try:
            with socket.create_connection((host, port), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=host) as ssock:
                    cert = ssock.getpeercert()
                    
                    if 'subject' in cert:
                        for entry in cert['subject']:
                            for k, v in entry:
                                result['subject'][k] = v
                                
                    if 'issuer' in cert:
                        for entry in cert['issuer']:
                            for k, v in entry:
                                result['issuer'][k] = v
                                
                    result['version'] = cert.get('version')
                    
                    if 'subjectAltName' in cert:
                        result['sans'] = [v for k, v in cert['subjectAltName']]
                        
                    if 'notBefore' in cert:
                        result['not_before'] = cert['notBefore']
                    if 'notAfter' in cert:
                        result['not_after'] = cert['notAfter']
                        
                        # Check expiration
                        not_after_date = ssl.cert_time_to_seconds(cert['notAfter'])
                        if datetime.utcnow().timestamp() > not_after_date:
                            result['expired'] = True
                            
        except Exception as e:
            raise ExecutionError(f"Error fetching certificate: {str(e)}")

        return {'status': 'success', 'result': result}
