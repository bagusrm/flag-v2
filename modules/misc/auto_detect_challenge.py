import os
import re
from core.base_tool import BaseTool, register_tool
from core.exceptions import ExecutionError
from core.utils import read_file_bytes, calculate_entropy, get_file_type

@register_tool
class AutoDetectChallenge(BaseTool):
    name = 'auto_detect_challenge'
    category = 'misc'
    description = 'Auto-detect CTF challenge type from a file and recommend tools'
    tags = ['automation', 'detect', 'challenge']

    def _setup_options(self):
        self.add_option('FILE', 'Path to the challenge file', required=True)

    def run(self) -> dict:
        file_path = self.get_option('FILE')
        if not os.path.isfile(file_path):
            raise ExecutionError(f"File not found: {file_path}")

        try:
            data = read_file_bytes(file_path)
            file_type = get_file_type(file_path)
        except Exception as e:
            raise ExecutionError(f"Failed to read file: {e}")

        entropy = calculate_entropy(data) if data else 0
        suggestions = []

        # Map file extensions / types to tools
        ext = os.path.splitext(file_path)[1].lower()
        if ext in ['.elf', '.bin'] or b'\x7fELF' in data[:4]:
            suggestions.append({'tools': ['reverse/elf_parser', 'pwn/checksec_wrapper'], 'reason': 'ELF executable detected', 'confidence': 95})
        elif ext in ['.exe', '.dll'] or b'MZ' in data[:2]:
            suggestions.append({'tools': ['reverse/pe_parser', 'reverse/strings_extractor'], 'reason': 'PE executable detected', 'confidence': 95})
        elif ext in ['.png', '.jpg', '.jpeg', '.bmp'] or b'\x89PNG' in data[:4] or b'\xff\xd8\xff' in data[:3]:
            suggestions.append({'tools': ['stego/zsteg_wrapper', 'stego/stegsolve_helper', 'forensic/image_analyzer'], 'reason': 'Image file detected', 'confidence': 90})
        elif ext in ['.zip', '.tar', '.gz'] or b'PK\x03\x04' in data[:4]:
            suggestions.append({'tools': ['forensic/zip_analyzer', 'forensic/binwalk_wrapper'], 'reason': 'Archive detected', 'confidence': 90})
        elif ext == '.pdf' or b'%PDF' in data[:4]:
            suggestions.append({'tools': ['forensic/pdf_analyzer'], 'reason': 'PDF document detected', 'confidence': 90})

        # Check entropy
        if entropy > 7.5:
            suggestions.append({'tools': ['forensic/entropy_analyzer', 'forensic/binwalk_wrapper'], 'reason': f'High entropy ({entropy:.2f}) indicates packed/encrypted/compressed data', 'confidence': 85})

        # Text analysis
        try:
            text = data.decode('utf-8')
            if '<html' in text.lower() or '<script' in text.lower():
                suggestions.append({'tools': ['web/html_parser', 'web/js_beautifier'], 'reason': 'HTML/JS content', 'confidence': 80})
            if re.search(r'^[A-Za-z0-9+/]+={0,2}$', text.strip()) and len(text.strip()) > 20:
                suggestions.append({'tools': ['crypto/base64', 'crypto/auto_detect'], 'reason': 'Possible Base64 content', 'confidence': 70})
        except UnicodeDecodeError:
            pass

        suggestions.sort(key=lambda x: x['confidence'], reverse=True)

        return {
            'status': 'success',
            'file_type': file_type,
            'entropy': entropy,
            'suggestions': suggestions
        }
