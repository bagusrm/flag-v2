from core.base_tool import BaseTool, register_tool
from core.exceptions import ExecutionError
from pathlib import Path
import zlib
import struct

@register_tool
class LsbAnalyzer(BaseTool):
    name = 'lsb_analyzer'
    category = 'stego'
    description = 'LSB Steganography analysis and automatic text/data extraction (Pure Python)'
    tags = ['stego', 'lsb', 'extract', 'png', 'decode']

    def _setup_options(self):
        self.add_option('FILE', 'Path to PNG/BMP image', required=True)
        self.add_option('BITS', 'Number of LSB bits to extract (1-8)', default='1')
        self.add_option('MODE', 'analyze or extract', default='extract', choices=['analyze', 'extract'])
        self.add_option('OUTPUT_FILE', 'Save extracted LSB raw data to file', required=False)

    def _parse_png_idat(self, raw_bytes: bytes) -> bytes:
        """Extract and decompress PNG IDAT chunks."""
        idx = 8  # Skip PNG signature
        idat_data = bytearray()
        
        while idx < len(raw_bytes):
            if idx + 8 > len(raw_bytes):
                break
            length, chunk_type = struct.unpack('>I4s', raw_bytes[idx:idx+8])
            idx += 8
            if chunk_type == b'IDAT':
                idat_data.extend(raw_bytes[idx:idx+length])
            idx += length + 4  # Skip data and CRC
            
        if not idat_data:
            raise ExecutionError("No IDAT chunks found in PNG file.")
            
        try:
            return zlib.decompress(idat_data)
        except Exception as e:
            return bytes(idat_data)

    def run(self) -> dict:
        file_path = self.get_option('FILE')
        num_bits = int(self.get_option('BITS'))
        mode = self.get_option('MODE')
        output_file = self.get_option('OUTPUT_FILE')

        p = Path(file_path).expanduser().resolve()
        if not p.exists():
            raise ExecutionError(f"File not found: {file_path}")

        raw_content = p.read_bytes()
        decompressed_data = self._parse_png_idat(raw_content)

        # Extract LSB bits
        extracted_bits = []
        for b in decompressed_data:
            for i in range(num_bits - 1, -1, -1):
                bit = (b >> i) & 1
                extracted_bits.append(str(bit))

        bit_string = ''.join(extracted_bits)
        
        # Convert bit string to bytes
        extracted_bytes = bytearray()
        for i in range(0, len(bit_string) - 7, 8):
            byte_val = int(bit_string[i:i+8], 2)
            extracted_bytes.append(byte_val)

        # Extract printable ASCII strings from extracted bytes
        ascii_chars = []
        current_str = []
        printable_strings = []

        for b in extracted_bytes:
            if 32 <= b <= 126 or b in (10, 13, 9):
                current_str.append(chr(b))
            else:
                if len(current_str) >= 4:
                    printable_strings.append(''.join(current_str))
                current_str = []

        if len(current_str) >= 4:
            printable_strings.append(''.join(current_str))

        # Save to file if output file specified
        if output_file:
            out_p = Path(output_file).expanduser().resolve()
            out_p.parent.mkdir(parents=True, exist_ok=True)
            out_p.write_bytes(extracted_bytes)

        return {
            'status': 'success',
            'result': {
                'mode': mode,
                'total_lsb_bytes_extracted': len(extracted_bytes),
                'found_strings': printable_strings[:20],
                'raw_preview': bytes(extracted_bytes[:100]).hex(),
                'saved_to': str(output_file) if output_file else None
            }
        }
