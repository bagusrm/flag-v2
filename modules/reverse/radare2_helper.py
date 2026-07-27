from core.base_tool import BaseTool, register_tool

@register_tool
class Radare2HelperTool(BaseTool):
    name = 'radare2_helper'
    category = 'reverse'
    description = 'Radare2 command helper'
    tags = ['reverse', 'r2', 'radare2']
    
    def _setup_options(self):
        self.add_option('FILE', 'Path to binary', default='')
        self.add_option('MODE', 'commands/cheatsheet/script', default='commands')
    
    def run(self) -> dict:
        mode = self.get_option('MODE').lower()
        filepath = self.get_option('FILE') or 'binary.bin'
        
        result = {}
        
        if mode == 'commands':
            result['commands'] = [
                f'r2 {filepath}',
                'aaa (analyze all)',
                'afl (analyze functions list)',
                'pdf @ main (print disassembly function main)',
                'iz (print strings in data section)'
            ]
        elif mode == 'cheatsheet':
            result['cheatsheet'] = {
                'Information': 'iI (info), iz (strings), iS (sections)',
                'Analysis': 'aa (analyze all), aac (analyze function calls)',
                'Print': 'px (hex), pd (disassemble), pdf (disassemble function)'
            }
        elif mode == 'script':
            result['script'] = '''import r2pipe
r2 = r2pipe.open("''' + filepath + '''")
r2.cmd('aaa')
print(r2.cmd('afl'))
r2.quit()'''
        
        return {'status': 'success', 'result': result}
