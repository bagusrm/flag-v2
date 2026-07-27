import os
import math
from core.base_tool import BaseTool, register_tool
from core.exceptions import ExecutionError

@register_tool
class EntropyAnalyzer(BaseTool):
    name = 'entropy'
    category = 'forensic'
    description = 'Analyze file entropy to detect encryption or compression'
    tags = ['forensic', 'entropy', 'crypto', 'compression']
    
    def _setup_options(self):
        self.add_option('FILE', 'Path to file', required=True)
        self.add_option('BLOCK_SIZE', 'Block size for block-by-block analysis', default='256')
    
    def calculate_entropy(self, data: bytes) -> float:
        if not data:
            return 0.0
        entropy = 0
        for x in range(256):
            p_x = float(data.count(x)) / len(data)
            if p_x > 0:
                entropy += - p_x * math.log2(p_x)
        return entropy

    def run(self) -> dict:
        file_path = self.get_option('FILE')
        block_size = int(self.get_option('BLOCK_SIZE'))
        
        if not os.path.exists(file_path):
            raise ExecutionError(f"File not found: {file_path}")
            
        with open(file_path, 'rb') as f:
            content = f.read()
            
        overall_entropy = self.calculate_entropy(content)
        
        blocks = []
        high_entropy_regions = []
        for i in range(0, len(content), block_size):
            block = content[i:i+block_size]
            ent = self.calculate_entropy(block)
            blocks.append(ent)
            if ent > 7.5:
                high_entropy_regions.append({'offset': i, 'entropy': ent})
                
        # Visual representation
        blocks_visual = ""
        symbols = [' ', '▂', '▃', '▄', '▅', '▆', '▇', '█']
        
        sampled_blocks = blocks
        if len(blocks) > 100:
            step = len(blocks) // 100
            sampled_blocks = [sum(blocks[i:i+step])/len(blocks[i:i+step]) for i in range(0, len(blocks), step)]
            
        for ent in sampled_blocks:
            idx = int((ent / 8.0) * (len(symbols) - 1))
            blocks_visual += symbols[min(idx, len(symbols)-1)]
            
        return {
            'status': 'success', 
            'result': {
                'overall_entropy': overall_entropy,
                'possible_encrypted_or_compressed': overall_entropy > 7.5,
                'high_entropy_regions_count': len(high_entropy_regions),
                'high_entropy_regions': high_entropy_regions[:10], # limit output
                'visual_graph': blocks_visual
            }
        }
