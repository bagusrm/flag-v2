from core.base_tool import BaseTool, register_tool
from core.exceptions import ExecutionError

@register_tool
class MorseTool(BaseTool):
    """Morse code encode and decode."""
    name = 'morse'
    category = 'crypto'
    description = 'Standard ITU Morse code encoder/decoder.'
    tags = ['morse', 'encode', 'decode']

    MORSE_CODE_DICT = {
        'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.', 'F': '..-.',
        'G': '--.', 'H': '....', 'I': '..', 'J': '.---', 'K': '-.-', 'L': '.-..',
        'M': '--', 'N': '-.', 'O': '---', 'P': '.--.', 'Q': '--.-', 'R': '.-.',
        'S': '...', 'T': '-', 'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-',
        'Y': '-.--', 'Z': '--..', '1': '.----', '2': '..---', '3': '...--',
        '4': '....-', '5': '.....', '6': '-....', '7': '--...', '8': '---..',
        '9': '----.', '0': '-----', ',': '--..--', '.': '.-.-.-', '?': '..--..',
        '/': '-..-.', '-': '-....-', '(': '-.--.', ')': '-.--.-'
    }

    def _setup_options(self):
        self.add_option('DATA', 'Input data', required=True)
        self.add_option('MODE', 'encode/decode', required=False, default='decode', choices=['encode', 'decode'])
        self.add_option('DELIMITER', 'Word delimiter for decode', required=False, default=' / ')

    def run(self) -> dict:
        data = self.get_option('DATA')
        mode = self.get_option('MODE')
        delim = self.get_option('DELIMITER')

        try:
            if mode == 'encode':
                result = []
                for char in data.upper():
                    if char in self.MORSE_CODE_DICT:
                        result.append(self.MORSE_CODE_DICT[char])
                    elif char == ' ':
                        result.append('/')
                return {'status': 'success', 'result': ' '.join(result)}
            else:
                inv_dict = {v: k for k, v in self.MORSE_CODE_DICT.items()}
                # Auto detect delimiter if data doesn't have the default one
                if delim not in data and '/' in data:
                    delim = '/'
                elif delim not in data and '|' in data:
                    delim = '|'
                
                if delim in data:
                    words = data.split(delim)
                else:
                    words = data.split('   ') # Default standard morse word gap
                    if len(words) == 1:
                        words = [data]

                decoded_message = []
                for word in words:
                    decoded_word = ""
                    for char in word.split():
                        if char in inv_dict:
                            decoded_word += inv_dict[char]
                        else:
                            decoded_word += '?'
                    decoded_message.append(decoded_word)
                
                return {'status': 'success', 'result': ' '.join(decoded_message)}
        except Exception as e:
            raise ExecutionError(f"Morse cipher error: {str(e)}")
