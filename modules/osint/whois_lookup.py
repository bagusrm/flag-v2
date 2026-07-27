import socket
from core.base_tool import BaseTool, register_tool
from core.exceptions import ExecutionError

@register_tool
class WhoisLookup(BaseTool):
    name = 'whois_lookup'
    category = 'osint'
    description = 'Perform WHOIS domain lookup'
    tags = ['osint', 'whois', 'domain']

    def _setup_options(self):
        self.add_option('DOMAIN', 'Domain to lookup', required=True)

    def run(self) -> dict:
        domain = self.get_option('DOMAIN')
        
        # Determine whois server based on TLD, default to whois.iana.org to find the real one
        whois_server = "whois.iana.org"
        result = {
            'domain': domain,
            'raw_output': '',
            'error': ''
        }

        def query_whois(server, target_domain):
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(10)
            try:
                s.connect((server, 43))
                s.send((target_domain + "\r\n").encode())
                response = b""
                while True:
                    data = s.recv(4096)
                    if not data:
                        break
                    response += data
                return response.decode(errors='ignore')
            finally:
                s.close()

        try:
            # Query IANA first to find the authoritative server
            iana_resp = query_whois(whois_server, domain)
            auth_server = None
            for line in iana_resp.splitlines():
                if line.startswith("refer:"):
                    auth_server = line.split()[1].strip()
                    break
            
            if auth_server:
                final_resp = query_whois(auth_server, domain)
                result['raw_output'] = final_resp
            else:
                # Fallback to whois.verisign-grs.com for common ones
                result['raw_output'] = query_whois("whois.verisign-grs.com", domain)

        except Exception as e:
            result['error'] = str(e)
            raise ExecutionError(f"WHOIS lookup failed: {str(e)}")

        return {'status': 'success', 'result': result}
