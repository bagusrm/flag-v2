import os
from core.base_tool import BaseTool, register_tool
from core.exceptions import ExecutionError

@register_tool
class ImageCompare(BaseTool):
    name = 'image_compare'
    category = 'stego'
    description = 'Compare two images (basic binary comparison)'
    tags = ['stego', 'compare', 'xor']

    def _setup_options(self):
        self.add_option('FILE', 'Path to first file', required=True)
        self.add_option('FILE2', 'Path to second file', required=True)

    def run(self) -> dict:
        file1 = self.get_option('FILE')
        file2 = self.get_option('FILE2')
        
        if not os.path.exists(file1):
            raise ExecutionError(f"First file not found: {file1}")
        if not os.path.exists(file2):
            raise ExecutionError(f"Second file not found: {file2}")

        result = {
            'same_size': False,
            'differences': 0,
            'percentage_diff': 0.0,
            'message': ''
        }

        size1 = os.path.getsize(file1)
        size2 = os.path.getsize(file2)

        result['same_size'] = (size1 == size2)

        try:
            with open(file1, 'rb') as f1, open(file2, 'rb') as f2:
                # Basic binary comparison to avoid heavy memory usage
                chunk_size = 8192
                diff_count = 0
                total_bytes = 0
                
                while True:
                    b1 = f1.read(chunk_size)
                    b2 = f2.read(chunk_size)
                    
                    if not b1 and not b2:
                        break
                        
                    total_bytes += max(len(b1), len(b2))
                    
                    for i in range(min(len(b1), len(b2))):
                        if b1[i] != b2[i]:
                            diff_count += 1
                            
                    if len(b1) != len(b2):
                        diff_count += abs(len(b1) - len(b2))

                result['differences'] = diff_count
                if total_bytes > 0:
                    result['percentage_diff'] = (diff_count / total_bytes) * 100
                    
                if diff_count == 0:
                    result['message'] = "Files are identical."
                else:
                    result['message'] = f"Found {diff_count} differing bytes."
                    
        except Exception as e:
            raise ExecutionError(f"Error comparing images: {str(e)}")

        return {'status': 'success', 'result': result}
