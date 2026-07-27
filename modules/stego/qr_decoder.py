import os
import subprocess
from core.base_tool import BaseTool, register_tool
from core.exceptions import ExecutionError

@register_tool
class QRDecoder(BaseTool):
    name = 'qr_decoder'
    category = 'stego'
    description = 'Decode QR codes using zbarimg'
    tags = ['stego', 'qr', 'barcode']

    def _setup_options(self):
        self.add_option('FILE', 'Path to file', required=True)

    def run(self) -> dict:
        file_path = self.get_option('FILE')
        
        if not os.path.exists(file_path):
            raise ExecutionError(f"File not found: {file_path}")

        result = {
            'tool_used': 'zbarimg',
            'installed': False,
            'decoded_data': [],
            'message': ''
        }

        try:
            subprocess.run(['zbarimg', '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            result['installed'] = True
        except (subprocess.CalledProcessError, FileNotFoundError):
            result['message'] = "zbarimg is not installed. Please install 'zbar-tools' or use an online decoder like zxing.org."
            return {'status': 'success', 'result': result}

        try:
            process = subprocess.run(['zbarimg', '-q', file_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if process.stdout:
                for line in process.stdout.splitlines():
                    if line.startswith('QR-Code:'):
                        result['decoded_data'].append(line.replace('QR-Code:', '', 1).strip())
            
            if not result['decoded_data']:
                result['message'] = "No QR code detected or unable to decode."
                
        except Exception as e:
            raise ExecutionError(f"Error decoding QR code: {str(e)}")

        return {'status': 'success', 'result': result}
