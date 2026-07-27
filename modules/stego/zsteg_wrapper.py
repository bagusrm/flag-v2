import os
import subprocess
from core.base_tool import BaseTool, register_tool
from core.exceptions import ExecutionError

@register_tool
class ZstegWrapper(BaseTool):
    name = 'zsteg_wrapper'
    category = 'stego'
    description = 'Wrapper for zsteg Ruby tool for PNG/BMP steganography'
    tags = ['stego', 'zsteg', 'lsb', 'png', 'bmp']

    def _setup_options(self):
        self.add_option('FILE', 'Path to file', required=True)
        self.add_option('MODE', 'Mode: all/lsb/text', required=False, default='all')

    def run(self) -> dict:
        file_path = self.get_option('FILE')
        mode = self.get_option('MODE')
        
        if not os.path.exists(file_path):
            raise ExecutionError(f"File not found: {file_path}")

        result = {
            'installed': False,
            'output': '',
            'message': ''
        }

        try:
            # Check if zsteg is installed
            subprocess.run(['zsteg', '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            result['installed'] = True
        except (subprocess.CalledProcessError, FileNotFoundError):
            result['message'] = "zsteg is not installed. Please install it using 'gem install zsteg' or check your PATH."
            return {'status': 'success', 'result': result}

        cmd = ['zsteg']
        if mode == 'all':
            cmd.append('--all')
        
        cmd.append(file_path)
        
        try:
            process = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=60)
            result['output'] = process.stdout
            if process.stderr:
                result['errors'] = process.stderr
        except subprocess.TimeoutExpired:
            result['message'] = "zsteg execution timed out after 60 seconds."
        except Exception as e:
            raise ExecutionError(f"Error running zsteg: {str(e)}")

        return {'status': 'success', 'result': result}
