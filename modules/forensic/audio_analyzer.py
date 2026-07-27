import os
import struct
from core.base_tool import BaseTool, register_tool
from core.exceptions import ExecutionError

@register_tool
class AudioAnalyzerTool(BaseTool):
    name = 'audio_analyzer'
    category = 'forensic'
    description = 'Analyze audio files and suggest analysis tools'
    tags = ['forensic', 'audio', 'sound']
    
    def _setup_options(self):
        self.add_option('FILE', 'Path to file', required=True)
    
    def run(self) -> dict:
        file_path = self.get_option('FILE')
        
        if not os.path.exists(file_path):
            raise ExecutionError(f"File not found: {file_path}")
            
        with open(file_path, 'rb') as f:
            content = f.read(1024)
            
        result = {
            'suggestions': ['Sonic Visualiser (for spectrogram)', 'Audacity']
        }
        
        if content.startswith(b'RIFF') and content[8:12] == b'WAVE':
            result['format'] = 'WAV'
            fmt_idx = content.find(b'fmt ')
            if fmt_idx != -1:
                fmt_chunk = content[fmt_idx:fmt_idx+24]
                if len(fmt_chunk) == 24:
                    audio_format, num_channels, sample_rate, byte_rate, block_align, bits_per_sample = struct.unpack('<HHIIHH', fmt_chunk[8:24])
                    result['channels'] = num_channels
                    result['sample_rate'] = sample_rate
                    result['bits_per_sample'] = bits_per_sample
                    result['is_pcm'] = (audio_format == 1)
        elif content.startswith(b'ID3') or b'\xff\xfb' in content[:4]:
            result['format'] = 'MP3'
        elif content.startswith(b'OggS'):
            result['format'] = 'OGG'
        elif content.startswith(b'fLaC'):
            result['format'] = 'FLAC'
        else:
            result['format'] = 'Unknown'
            
        return {'status': 'success', 'result': result}
