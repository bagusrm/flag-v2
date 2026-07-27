import os
import re
from core.base_tool import BaseTool, register_tool
from core.exceptions import ExecutionError

@register_tool
class AutoRecommend(BaseTool):
    name = 'auto_recommend'
    category = 'misc'
    description = 'Auto-recommend tools based on challenge description or file'
    tags = ['automation', 'recommend']

    def _setup_options(self):
        self.add_option('DESCRIPTION', 'Challenge description text', required=False, default='')
        self.add_option('FILE', 'Path to the challenge file', required=False, default='')

    def run(self) -> dict:
        desc = self.get_option('DESCRIPTION').lower()
        file_path = self.get_option('FILE')

        if not desc and not file_path:
            raise ExecutionError("Must provide DESCRIPTION or FILE")

        recommendations = []

        # Analyze description keywords
        if desc:
            keywords_map = {
                'rsa': ('crypto/rsa_helper', 95),
                'aes': ('crypto/aes_helper', 95),
                'xor': ('crypto/xor', 90),
                'base64': ('crypto/base64', 90),
                'pcap': ('forensic/network_analyzer', 90), # Assuming this exists or generic
                'wireshark': ('forensic/network_analyzer', 90),
                'sql': ('web/sql_encoder', 85),
                'xss': ('web/xss_encoder', 85),
                'buffer overflow': ('pwn/exploit_template', 90),
                'rop': ('pwn/rop_gadget', 95),
                'lsb': ('stego/lsb_analyzer', 90),
                'exif': ('forensic/exiftool_wrapper', 90),
                'jwt': ('web/jwt_inspector', 90),
                'ghidra': ('reverse/ghidra_helper', 90)
            }
            for kw, (tool, conf) in keywords_map.items():
                if kw in desc:
                    recommendations.append({'tool': tool, 'reason': f'Matched keyword "{kw}"', 'confidence': conf})

        # Analyze file extension if provided
        if file_path and os.path.isfile(file_path):
            ext = os.path.splitext(file_path)[1].lower()
            ext_map = {
                '.pcap': ('forensic/network_analyzer', 90),
                '.pcapng': ('forensic/network_analyzer', 90),
                '.png': ('stego/zsteg_wrapper', 85),
                '.jpg': ('stego/stegsolve_helper', 80),
                '.elf': ('reverse/elf_parser', 90),
                '.exe': ('reverse/pe_parser', 90),
                '.apk': ('reverse/apk_analyzer', 90)
            }
            if ext in ext_map:
                tool, conf = ext_map[ext]
                recommendations.append({'tool': tool, 'reason': f'Matched extension "{ext}"', 'confidence': conf})

        # Sort recommendations
        recommendations.sort(key=lambda x: x['confidence'], reverse=True)

        return {
            'status': 'success',
            'recommendations': recommendations
        }
