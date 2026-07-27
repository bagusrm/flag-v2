import os
import zipfile
from core.base_tool import BaseTool, register_tool
from core.exceptions import ExecutionError

@register_tool
class ZipAnalyzerTool(BaseTool):
    name = 'zip_analyzer'
    category = 'forensic'
    description = 'Analyze ZIP archive structure and look for anomalies'
    tags = ['forensic', 'zip', 'archive']
    
    def _setup_options(self):
        self.add_option('FILE', 'Path to file', required=True)
    
    def run(self) -> dict:
        file_path = self.get_option('FILE')
        
        if not os.path.exists(file_path):
            raise ExecutionError(f"File not found: {file_path}")
            
        if not zipfile.is_zipfile(file_path):
            return {'status': 'error', 'message': 'Not a valid ZIP file'}
            
        result = {
            'files': [],
            'comment': '',
            'warnings': []
        }
        
        try:
            with zipfile.ZipFile(file_path, 'r') as zf:
                result['comment'] = zf.comment.decode('latin1', errors='replace')
                
                total_uncompressed = 0
                total_compressed = 0
                
                for info in zf.infolist():
                    is_encrypted = bool(info.flag_bits & 0x1)
                    
                    file_info = {
                        'filename': info.filename,
                        'compressed_size': info.compress_size,
                        'uncompressed_size': info.file_size,
                        'encrypted': is_encrypted,
                        'datetime': info.date_time
                    }
                    result['files'].append(file_info)
                    
                    total_uncompressed += info.file_size
                    total_compressed += info.compress_size
                    
                    if info.filename.endswith('.zip'):
                        result['warnings'].append(f"Nested ZIP found: {info.filename}")
                        
                    if info.filename.startswith('.') or '/.' in info.filename:
                        result['warnings'].append(f"Hidden file found: {info.filename}")
                        
                # Zip bomb detection
                if total_compressed > 0 and total_uncompressed / total_compressed > 100:
                    result['warnings'].append("High compression ratio detected. Possible ZIP bomb.")
                    
        except Exception as e:
            raise ExecutionError(f"Error parsing ZIP: {str(e)}")
            
        return {'status': 'success', 'result': result}
