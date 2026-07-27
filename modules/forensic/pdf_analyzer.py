import os
import re
from core.base_tool import BaseTool, register_tool
from core.exceptions import ExecutionError

@register_tool
class PDFAnalyzerTool(BaseTool):
    name = 'pdf_analyzer'
    category = 'forensic'
    description = 'Analyze PDF structure and metadata without external dependencies'
    tags = ['forensic', 'pdf', 'document']
    
    def _setup_options(self):
        self.add_option('FILE', 'Path to file', required=True)
    
    def run(self) -> dict:
        file_path = self.get_option('FILE')
        
        if not os.path.exists(file_path):
            raise ExecutionError(f"File not found: {file_path}")
            
        with open(file_path, 'rb') as f:
            content = f.read()
            
        if not content.startswith(b'%PDF-'):
            return {'status': 'error', 'message': 'Not a PDF file'}
            
        version = content[5:8].decode('ascii', errors='ignore')
        
        # Count objects and streams
        obj_count = len(re.findall(b'\\bobj\\b', content))
        stream_count = len(re.findall(b'\\bstream\\b', content))
        
        # Detect malicious/interesting elements
        suspicious = []
        if b'/JavaScript' in content or b'/JS' in content:
            suspicious.append("JavaScript detected")
        if b'/OpenAction' in content or b'/AA' in content:
            suspicious.append("Auto-action on open detected")
        if b'/EmbeddedFiles' in content:
            suspicious.append("Embedded files detected")
            
        # Basic Info dict extraction
        meta = {}
        info_idx = content.find(b'/Info')
        if info_idx != -1:
            obj_idx = content.rfind(b'obj', 0, info_idx)
            endobj_idx = content.find(b'endobj', info_idx)
            if obj_idx != -1 and endobj_idx != -1:
                info_data = content[obj_idx:endobj_idx].decode('latin1', errors='ignore')
                matches = re.findall(r'/([A-Za-z]+)\s*\((.*?)\)', info_data)
                for k, v in matches:
                    meta[k] = v
                    
        return {
            'status': 'success', 
            'result': {
                'pdf_version': version,
                'objects_count': obj_count,
                'streams_count': stream_count,
                'metadata': meta,
                'suspicious_elements': suspicious
            }
        }
