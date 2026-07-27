import subprocess
import shutil
import os
from core.base_tool import BaseTool, register_tool
from core.exceptions import ExecutionError

@register_tool
class ExifToolWrapper(BaseTool):
    name = 'exiftool'
    category = 'forensic'
    description = 'Wrapper for exiftool CLI to extract metadata'
    tags = ['forensic', 'metadata', 'exif']
    
    def _setup_options(self):
        self.add_option('FILE', 'Path to file', required=True)
        self.add_option('TAGS', 'Specific tags to extract (comma separated)', required=False)
    
    def run(self) -> dict:
        file_path = self.get_option('FILE')
        tags_opt = self.get_option('TAGS')
        
        if not os.path.exists(file_path):
            raise ExecutionError(f"File not found: {file_path}")
            
        exiftool_path = shutil.which('exiftool')
        if not exiftool_path:
            return {
                'status': 'error', 
                'message': 'exiftool is not installed or not in PATH.',
                'instructions': 'Please install exiftool (e.g. apt-get install libimage-exiftool-perl or download Windows executable)'
            }
            
        cmd = [exiftool_path]
        if tags_opt:
            tags = [t.strip() for t in tags_opt.split(',')]
            for tag in tags:
                cmd.append(f'-{tag}')
        cmd.append(file_path)
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            output = result.stdout
            
            parsed = {}
            for line in output.splitlines():
                if ':' in line:
                    parts = line.split(':', 1)
                    parsed[parts[0].strip()] = parts[1].strip()
                    
            return {'status': 'success', 'result': parsed, 'raw': output}
        except subprocess.CalledProcessError as e:
            raise ExecutionError(f"exiftool execution failed: {e.stderr}")
