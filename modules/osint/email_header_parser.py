import email
from email.parser import Parser
import re
from core.base_tool import BaseTool, register_tool
from core.exceptions import ExecutionError

@register_tool
class EmailHeaderParser(BaseTool):
    name = 'email_header_parser'
    category = 'osint'
    description = 'Parse email headers and extract trace information'
    tags = ['osint', 'email', 'headers']

    def _setup_options(self):
        self.add_option('DATA', 'Raw email headers or content', required=True)

    def run(self) -> dict:
        data = self.get_option('DATA')
        
        result = {
            'sender': None,
            'recipient': None,
            'subject': None,
            'date': None,
            'received': [],
            'auth_results': {},
            'ips_found': []
        }

        try:
            msg = Parser().parsestr(data)
            
            result['sender'] = msg.get('From')
            result['recipient'] = msg.get('To')
            result['subject'] = msg.get('Subject')
            result['date'] = msg.get('Date')
            
            # Parse Received headers
            received_headers = msg.get_all('Received', [])
            result['received'] = received_headers
            
            # Auth Results
            auth = msg.get('Authentication-Results')
            if auth:
                result['auth_results']['raw'] = auth
                if 'spf=pass' in auth.lower():
                    result['auth_results']['spf'] = 'pass'
                if 'dkim=pass' in auth.lower():
                    result['auth_results']['dkim'] = 'pass'
                if 'dmarc=pass' in auth.lower():
                    result['auth_results']['dmarc'] = 'pass'
            
            # Extract IP addresses
            ip_pattern = re.compile(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b')
            ips = set()
            for header, value in msg.items():
                found_ips = ip_pattern.findall(value)
                for ip in found_ips:
                    ips.add(ip)
            
            result['ips_found'] = list(ips)
            
        except Exception as e:
            raise ExecutionError(f"Error parsing email headers: {str(e)}")

        return {'status': 'success', 'result': result}
