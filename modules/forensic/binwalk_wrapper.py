import subprocess
import shutil
import os
from core.base_tool import BaseTool, register_tool
from core.exceptions import ExecutionError

@register_tool
class BinwalkWrapper(BaseTool):
    name = 'binwalk'
    category = 'forensic'
    description = 'Wrapper for binwalk CLI to analyze and extract firmwares'
    tags = ['forensic', 'binwalk', 'firmware', 'extract']
    
    def _setup_options(self):
        self.add_option('FILE', 'Path to file', required=True)
        self.add_option('MODE', 'scan, extract, or entropy', default='scan')
    
    def run(self) -> dict:
        file_path = self.get_option('FILE')
        mode = self.get_option('MODE').lower()
        
        if not os.path.exists(file_path):
            raise ExecutionError(f"File not found: {file_path}")
            
        binwalk_path = shutil.which('binwalk')
        if not binwalk_path:
            return {
                'status': 'error', 
                'message': 'binwalk is not installed or not in PATH.',
                'instructions': 'Please install binwalk (e.g. apt-get install binwalk or pip install binwalk)'
            }
            
        cmd = [binwalk_path]
        if mode == 'extract':
            cmd.append('-e')
        elif mode == 'entropy':
            cmd.append('-E')
        cmd.append(file_path)
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            output = result.stdout
            
            parsed = []
            for line in output.splitlines():
                if line and not line.startswith('DECIMAL') and not line.startswith('-'):
                    parts = line.split(maxsplit=2)
                    if len(parts) >= 3:
                        parsed.append({
                            'decimal': parts[0],
                            'hex': parts[1],
                            'description': parts[2]
                        })
                        
            return {'status': 'success', 'result': {'mode': mode, 'entries': parsed}, 'raw': output}
        except subprocess.CalledProcessError as e:
            raise ExecutionError(f"binwalk execution failed: {e.stderr}")
