from core.base_tool import BaseTool, register_tool
from core.exceptions import ExecutionError
import string
import collections

@register_tool
class FrequencyAnalysis(BaseTool):
    """Frequency analysis and IC calculator."""
    name = 'freq_analysis'
    category = 'crypto'
    description = 'Analyze letter frequencies and Index of Coincidence.'
    tags = ['frequency', 'ic', 'analysis']

    def _setup_options(self):
        self.add_option('DATA', 'Input data', required=True)

    def run(self) -> dict:
        data = self.get_option('DATA')
        
        try:
            letters = [c.upper() for c in data if c.isalpha()]
            N = len(letters)
            
            if N == 0:
                raise ExecutionError("No alphabetic characters found in data.")
                
            counts = collections.Counter(letters)
            
            # IC calculation
            ic = 0.0
            if N > 1:
                ic = sum(c * (c - 1) for c in counts.values()) / (N * (N - 1))
                
            english_freq = {
                'E': 12.7, 'T': 9.1, 'A': 8.1, 'O': 7.5, 'I': 7.0, 'N': 6.7,
                'S': 6.3, 'H': 6.1, 'R': 6.0, 'D': 4.3, 'L': 4.0, 'C': 2.8,
                'U': 2.8, 'M': 2.4, 'W': 2.4, 'F': 2.2, 'Y': 2.0, 'G': 2.0,
                'P': 1.9, 'B': 1.5, 'V': 1.0, 'K': 0.8, 'X': 0.15, 'J': 0.15,
                'Q': 0.10, 'Z': 0.07
            }
            
            result = []
            result.append(f"Total alphabetic characters: {N}")
            result.append(f"Index of Coincidence (IC): {ic:.5f}")
            
            if ic > 0.06:
                result.append("-> IC suggests English/Monoalphabetic substitution.")
            elif ic > 0.05:
                result.append("-> IC suggests weak polyalphabetic (Vigenere with small key).")
            else:
                result.append("-> IC suggests Polyalphabetic substitution or random data.")
                
            result.append("\nCharacter Frequencies:")
            for char in string.ascii_uppercase:
                count = counts.get(char, 0)
                pct = (count / N) * 100
                eng_pct = english_freq[char]
                result.append(f"{char}: {count:4d} ({pct:5.2f}%)  | English: {eng_pct:5.2f}%")
                
            return {'status': 'success', 'result': '\n'.join(result)}
        except Exception as e:
            raise ExecutionError(f"Frequency Analysis error: {str(e)}")
