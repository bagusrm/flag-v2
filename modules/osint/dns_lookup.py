import socket
import subprocess
from core.base_tool import BaseTool, register_tool
from core.exceptions import ExecutionError

@register_tool
class DNSLookup(BaseTool):
    name = 'dns_lookup'
    category = 'osint'
    description = 'Perform DNS record lookup'
    tags = ['osint', 'dns', 'domain']

    def _setup_options(self):
        self.add_option('DOMAIN', 'Domain to lookup', required=True)
        self.add_option('RECORD_TYPE', 'A/AAAA/MX/NS/TXT/CNAME/ALL', required=False, default='ALL')

    def run(self) -> dict:
        domain = self.get_option('DOMAIN')
        record_type = self.get_option('RECORD_TYPE')
        
        result = {
            'domain': domain,
            'records': {},
            'raw_tool_output': ''
        }

        # Try basic socket resolution for A records
        try:
            result['records']['A'] = socket.gethostbyname_ex(domain)[2]
        except Exception:
            pass

        # Use nslookup as subprocess since pure Python lacks advanced DNS without external libraries
        try:
            cmd = ['nslookup']
            if record_type != 'ALL':
                cmd.append(f'-type={record_type}')
            cmd.append(domain)
            
            process = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=10)
            result['raw_tool_output'] = process.stdout
            
        except Exception as e:
            result['raw_tool_output'] = f"Error running nslookup: {str(e)}"

        return {'status': 'success', 'result': result}
