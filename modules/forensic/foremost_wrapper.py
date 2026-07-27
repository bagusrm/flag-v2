import subprocess
import shutil
import os
from core.base_tool import BaseTool, register_tool
from core.exceptions import ExecutionError

@register_tool
class ForemostWrapper(BaseTool):
    name = 'foremost'
    category = 'forensic'
    description = 'Wrapper for foremost file carver'
    tags = ['forensic', 'foremost', 'carving', 'extract']
    
    def _setup_options(self):
        self.add_option('FILE', 'Path to file', required=True)
        self.add_option('OUTPUT_DIR', 'Output directory', default='foremost_output')
        self.add_option('TYPES', 'File types to carve (comma separated, e.g. jpg,pdf)', required=False)
    
    def run(self) -> dict:
        file_path = self.get_option('FILE')
        output_dir = self.get_option('OUTPUT_DIR')
        types = self.get_option('TYPES')
        
        if not os.path.exists(file_path):
            raise ExecutionError(f"File not found: {file_path}")
            
        foremost_path = shutil.which('foremost')
        if not foremost_path:
            return {
                'status': 'error', 
                'message': 'foremost is not installed or not in PATH.',
                'instructions': 'Please install foremost (e.g. apt-get install foremost)'
            }
            
        if not os.path.isabs(output_dir):
            output_dir = os.path.join(os.getcwd(), output_dir)
            
        if os.path.exists(output_dir):
            shutil.rmtree(output_dir)
            
        cmd = [foremost_path, '-i', file_path, '-o', output_dir]
        if types:
            cmd.extend(['-t', types])
            
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            extracted_files = []
            if os.path.exists(output_dir):
                for root, dirs, files in os.walk(output_dir):
                    for file in files:
                        extracted_files.append(os.path.join(root, file))
                        
            return {
                'status': 'success', 
                'result': {
                    'output_directory': output_dir,
                    'files_extracted': len(extracted_files),
                    'files': extracted_files
                },
                'raw': result.stdout
            }
        except subprocess.CalledProcessError as e:
            raise ExecutionError(f"foremost execution failed: {e.stderr}")
