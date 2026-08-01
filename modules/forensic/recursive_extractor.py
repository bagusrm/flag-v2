from core.base_tool import BaseTool, register_tool
from core.exceptions import ExecutionError
from pathlib import Path
import re

@register_tool
class RecursiveExtractor(BaseTool):
    name = 'recursive_extractor'
    category = 'forensic'
    description = 'Recursively extract embedded files (JPEG, PNG, GIF, ZIP, PDF, ELF) by signature scanning'
    tags = ['forensic', 'extract', 'carve', 'embedded', 'recursive']

    def _setup_options(self):
        self.add_option('FILE', 'Path to host file', required=True)
        self.add_option('OUTPUT_DIR', 'Directory to save extracted files', default='extracted_output')
        self.add_option('MAX_DEPTH', 'Maximum recursion depth', default='3')

    def run(self) -> dict:
        file_path = self.get_option('FILE')
        output_dir = self.get_option('OUTPUT_DIR')
        max_depth = int(self.get_option('MAX_DEPTH'))

        p = Path(file_path).expanduser().resolve()
        if not p.exists():
            raise ExecutionError(f"File not found: {file_path}")

        out_p = Path(output_dir).expanduser().resolve()
        out_p.mkdir(parents=True, exist_ok=True)

        # File magic headers to scan for
        SIGNATURES = [
            (b'\xff\xd8\xff', '.jpg', b'\xff\xd9'),
            (b'\x89PNG\r\n\x1a\n', '.png', b'IEND\xaeB`\x82'),
            (b'GIF87a', '.gif', b'\x00\x3b'),
            (b'GIF89a', '.gif', b'\x00\x3b'),
            (b'PK\x03\x04', '.zip', None),
            (b'%PDF-', '.pdf', b'%%EOF'),
            (b'\x7fELF', '.elf', None)
        ]

        extracted_files = []

        def carve_file(data: bytes, depth: int, prefix: str) -> None:
            if depth > max_depth or not data:
                return

            for head_sig, ext, tail_sig in SIGNATURES:
                start_idx = 0
                while True:
                    idx = data.find(head_sig, start_idx)
                    if idx == -1:
                        break
                    
                    # Ignore signature if it is at the very beginning (0th byte) of original host file
                    if depth == 1 and idx == 0 and head_sig in data[:10]:
                        start_idx = idx + len(head_sig)
                        continue

                    # Determine end index
                    end_idx = -1
                    if tail_sig:
                        tail_pos = data.find(tail_sig, idx + len(head_sig))
                        if tail_pos != -1:
                            end_idx = tail_pos + len(tail_sig)
                    
                    if end_idx == -1:
                        # Fallback default length 1MB if no footer marker
                        end_idx = min(len(data), idx + 1024 * 1024)

                    extracted_data = data[idx:end_idx]
                    out_filename = out_p / f"{prefix}_offset_{idx}{ext}"
                    out_filename.write_bytes(extracted_data)

                    extracted_files.append({
                        'filename': out_filename.name,
                        'path': str(out_filename),
                        'offset': idx,
                        'size_bytes': len(extracted_data),
                        'type': ext.upper().replace('.', '')
                    })

                    # Recurse into extracted payload
                    carve_file(extracted_data, depth + 1, f"{prefix}_sub_{idx}")
                    start_idx = idx + len(head_sig)

        try:
            raw_content = p.read_bytes()
            carve_file(raw_content, depth=1, prefix=p.stem)
        except Exception as e:
            raise ExecutionError(f"Extraction failed: {str(e)}")

        return {
            'status': 'success',
            'result': {
                'output_dir': str(out_p),
                'extracted_count': len(extracted_files),
                'extracted_files': extracted_files
            }
        }
