from core.base_tool import BaseTool, register_tool
from core.exceptions import ExecutionError
from pathlib import Path

@register_tool
class BinaryChunker(BaseTool):
    name = 'binary_chunker'
    category = 'crypto'
    description = 'Custom binary stream chunking, auto-chunk size finder, and raw data conversion'
    tags = ['crypto', 'binary', 'chunk', 'convert', 'auto', 'stego']

    def _setup_options(self):
        self.add_option('DATA', 'Binary string input (0s and 1s)', required=False)
        self.add_option('FILE', 'Path to binary text file', required=False)
        self.add_option('CHUNK_SIZE', 'Bits per chunk (default 8, or auto/custom)', default='8')
        self.add_option('ENDIAN', 'Byte order (little/big)', default='big', choices=['big', 'little'])
        self.add_option('OUTPUT_FILE', 'Save converted raw bytes to file', required=False)
        self.add_option('MODE', 'convert or auto_bruteforce', default='convert', choices=['convert', 'auto_bruteforce'])

    def _clean_binary(self, raw_str: str) -> str:
        return raw_str.replace(' ', '').replace('\n', '').replace('\r', '').replace('\t', '').strip()

    def _score_text(self, text: str) -> float:
        """Score text printability for auto-detection."""
        if not text:
            return 0.0
        printable = sum(1 for c in text if 32 <= ord(c) <= 126 or c in '\n\r\t')
        score = printable / len(text)
        if 'flag' in text.lower() or 'ctf' in text.lower() or '{' in text:
            score += 2.0
        return score

    def run(self) -> dict:
        data = self.get_option('DATA')
        file_path = self.get_option('FILE')
        chunk_size_raw = str(self.get_option('CHUNK_SIZE')).strip().lower()
        endian = self.get_option('ENDIAN')
        output_file = self.get_option('OUTPUT_FILE')
        mode = self.get_option('MODE')

        if file_path:
            p = Path(file_path)
            if not p.exists():
                raise ExecutionError(f"File not found: {file_path}")
            data = p.read_text(encoding='utf-8', errors='ignore')

        if not data:
            raise ExecutionError("Either DATA or FILE must be provided.")

        clean_bin = self._clean_binary(data)
        if not all(c in '01' for c in clean_bin):
            raise ExecutionError("Input contains non-binary characters (only 0 and 1 allowed).")

        # Auto-bruteforce mode: try chunk sizes 4 to 32
        if mode == 'auto_bruteforce' or chunk_size_raw == 'auto':
            results = []
            for cs in range(4, 33):
                chunks = [clean_bin[i:i+cs] for i in range(0, len(clean_bin) - len(clean_bin) % cs, cs)]
                if not chunks:
                    continue
                
                raw_bytes = bytearray()
                ascii_chars = []
                for chk in chunks:
                    val = int(chk, 2)
                    byte_len = (cs + 7) // 8
                    val_bytes = val.to_bytes(byte_len, byteorder=endian)
                    raw_bytes.extend(val_bytes)
                    
                    if 32 <= val <= 126:
                        ascii_chars.append(chr(val))
                    else:
                        ascii_chars.append('.')
                        
                text_preview = ''.join(ascii_chars)
                score = self._score_text(text_preview)
                
                results.append({
                    'chunk_size': cs,
                    'total_chunks': len(chunks),
                    'score': round(score, 3),
                    'ascii_preview': text_preview[:100],
                    'hex_head': raw_bytes[:16].hex()
                })
            
            results.sort(key=lambda x: x['score'], reverse=True)
            return {
                'status': 'success',
                'result': {
                    'recommended_chunk_size': results[0]['chunk_size'] if results else 8,
                    'all_attempts': results[:10]
                }
            }

        # Convert mode with specific CHUNK_SIZE
        try:
            chunk_size = int(chunk_size_raw)
        except ValueError:
            raise ExecutionError("CHUNK_SIZE must be an integer (e.g. 7, 8, 16) or 'auto'.")

        chunks = [clean_bin[i:i+chunk_size] for i in range(0, len(clean_bin) - len(clean_bin) % chunk_size, chunk_size)]
        if not chunks:
            raise ExecutionError(f"Binary string length ({len(clean_bin)}) is shorter than chunk size ({chunk_size}).")

        raw_bytes = bytearray()
        ascii_chars = []
        parsed_numbers = []

        for chk in chunks:
            val = int(chk, 2)
            parsed_numbers.append(val)
            byte_len = max(1, (chunk_size + 7) // 8)
            val_bytes = val.to_bytes(byte_len, byteorder=endian)
            raw_bytes.extend(val_bytes)
            
            if 32 <= val <= 126:
                ascii_chars.append(chr(val))
            else:
                ascii_chars.append('.')

        ascii_str = ''.join(ascii_chars)
        hex_dump = raw_bytes.hex()

        # Save raw bytes to output file if requested
        if output_file:
            out_p = Path(output_file).expanduser().resolve()
            out_p.parent.mkdir(parents=True, exist_ok=True)
            out_p.write_bytes(raw_bytes)

        return {
            'status': 'success',
            'result': {
                'chunk_size': chunk_size,
                'total_chunks': len(chunks),
                'ascii_text': ascii_str,
                'hex_stream': hex_dump[:200] + ('...' if len(hex_dump) > 200 else ''),
                'numbers_preview': parsed_numbers[:20],
                'saved_to': str(output_file) if output_file else None
            }
        }
