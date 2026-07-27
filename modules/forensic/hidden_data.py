import os
from core.base_tool import BaseTool, register_tool
from core.exceptions import ExecutionError

@register_tool
class HiddenDataDetector(BaseTool):
    name = 'hidden_data'
    category = 'forensic'
    description = 'Detect hidden data (appended files, EOF markers, padding) in files'
    tags = ['forensic', 'steganography', 'hidden']
    
    EOF_MARKERS = {
        'JPEG': b'\xff\xd9',
        'PNG': b'IEND\xae\x42\x60\x82',
        'GIF': b'\x3b',
        'PDF': b'%%EOF'
    }
    
    def _setup_options(self):
        self.add_option('FILE', 'Path to file', required=True)
    
    def run(self) -> dict:
        file_path = self.get_option('FILE')
        
        if not os.path.exists(file_path):
            raise ExecutionError(f"File not found: {file_path}")
            
        results = {
            'eof_analysis': {},
            'padding_analysis': {},
            'appended_archives': []
        }
        
        file_size = os.path.getsize(file_path)
        with open(file_path, 'rb') as f:
            content = f.read()
            
        # EOF Analysis
        for ftype, marker in self.EOF_MARKERS.items():
            idx = content.rfind(marker)
            if idx != -1:
                end_of_file_data = idx + len(marker)
                extra_bytes = file_size - end_of_file_data
                if extra_bytes > 0:
                    results['eof_analysis'][ftype] = {
                        'marker_found': True,
                        'extra_bytes': extra_bytes,
                        'hidden_data_preview': content[end_of_file_data:end_of_file_data+32].hex()
                    }
                    
        # Padding Analysis
        null_count = 0
        for i in range(len(content)-1, -1, -1):
            if content[i] == 0:
                null_count += 1
            else:
                break
        if null_count > 0:
            results['padding_analysis']['trailing_null_bytes'] = null_count
            
        # Appended Archives
        zip_idx = content.find(b'PK\x03\x04', 1)
        if zip_idx != -1:
            results['appended_archives'].append({'type': 'ZIP', 'offset': zip_idx})
            
        rar_idx = content.find(b'Rar!\x1a\x07\x00', 1)
        if rar_idx != -1:
            results['appended_archives'].append({'type': 'RAR', 'offset': rar_idx})
            
        return {'status': 'success', 'result': results}
