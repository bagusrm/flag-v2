import os
import subprocess
from core.base_tool import BaseTool, register_tool
from core.exceptions import ExecutionError

@register_tool
class BarcodeReader(BaseTool):
    name = 'barcode_reader'
    category = 'stego'
    description = 'Read standard barcodes using zbarimg'
    tags = ['stego', 'barcode']

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
            result['message'] = "zbarimg is not installed. Please install 'zbar-tools'."
            return {'status': 'success', 'result': result}

        try:
            process = subprocess.run(['zbarimg', '-q', file_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if process.stdout:
                for line in process.stdout.splitlines():
                    if not line.startswith('QR-Code:'):
                        result['decoded_data'].append(line.strip())
            
            if not result['decoded_data']:
                result['message'] = "No barcode detected or unable to decode."
                
        except Exception as e:
            raise ExecutionError(f"Error decoding barcode: {str(e)}")

        return {'status': 'success', 'result': result}
