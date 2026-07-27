import os
from core.base_tool import BaseTool, register_tool
from core.exceptions import ExecutionError

@register_tool
class RecursiveExtractorTool(BaseTool):
    name = 'recursive_extractor'
    category = 'forensic'
    description = 'Recursively extract embedded files based on signatures'
    tags = ['forensic', 'extract', 'recursive']
    
    SIGNATURES = {
        b'\xff\xd8\xff\xe0': ('JPEG', '.jpg'),
        b'\x89PNG\r\n\x1a\n': ('PNG', '.png'),
        b'PK\x03\x04': ('ZIP', '.zip'),
        b'%PDF-': ('PDF', '.pdf')
    }
    
    def _setup_options(self):
        self.add_option('FILE', 'Path to file', required=True)
        self.add_option('OUTPUT_DIR', 'Output directory', default='extracted')
        self.add_option('MAX_DEPTH', 'Maximum recursion depth', default='3')
    
    def extract_from_data(self, data: bytes, base_name: str, out_dir: str, depth: int, max_depth: int, report: list):
        if depth > max_depth:
            return
            
        for sig, (ftype, ext) in self.SIGNATURES.items():
            idx = data.find(sig, 1) # Skip offset 0
            while idx != -1:
                # Basic extraction: dump from signature to end of file
                # Real implementation would parse structure or use binwalk
                extr_data = data[idx:]
                file_name = f"{base_name}_{ftype}_{idx}{ext}"
                out_path = os.path.join(out_dir, file_name)
                
                with open(out_path, 'wb') as f:
                    f.write(extr_data)
                    
                report.append({
                    'depth': depth,
                    'type': ftype,
                    'offset': idx,
                    'saved_to': out_path
                })
                
                # Recurse
                self.extract_from_data(extr_data, file_name, out_dir, depth + 1, max_depth, report)
                
                idx = data.find(sig, idx + 1)

    def run(self) -> dict:
        file_path = self.get_option('FILE')
        out_dir = self.get_option('OUTPUT_DIR')
        max_depth = int(self.get_option('MAX_DEPTH'))
        
        if not os.path.exists(file_path):
            raise ExecutionError(f"File not found: {file_path}")
            
        if not os.path.isabs(out_dir):
            out_dir = os.path.join(os.getcwd(), out_dir)
            
        os.makedirs(out_dir, exist_ok=True)
        
        with open(file_path, 'rb') as f:
            content = f.read()
            
        report = []
        base = os.path.basename(file_path)
        self.extract_from_data(content, base, out_dir, 1, max_depth, report)
        
        return {
            'status': 'success', 
            'result': {
                'output_dir': out_dir,
                'extracted_count': len(report),
                'report': report
            }
        }
