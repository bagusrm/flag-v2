from core.base_tool import BaseTool, register_tool

@register_tool
class MagicBytesTool(BaseTool):
    name = 'magic_bytes'
    category = 'forensic'
    description = 'Database of magic bytes for file identification'
    tags = ['forensic', 'magic', 'database']
    
    DB = [
        {'name': 'PNG', 'hex': '89504E470D0A1A0A', 'offset': 0},
        {'name': 'JPEG', 'hex': 'FFD8FF', 'offset': 0},
        {'name': 'GIF87a', 'hex': '474946383761', 'offset': 0},
        {'name': 'GIF89a', 'hex': '474946383961', 'offset': 0},
        {'name': 'PDF', 'hex': '255044462D', 'offset': 0},
        {'name': 'ZIP', 'hex': '504B0304', 'offset': 0},
        {'name': 'RAR v4', 'hex': '526172211A0700', 'offset': 0},
        {'name': 'RAR v5', 'hex': '526172211A070100', 'offset': 0},
        {'name': '7Z', 'hex': '377ABCAF271C', 'offset': 0},
        {'name': 'GZIP', 'hex': '1F8B', 'offset': 0},
        {'name': 'ELF', 'hex': '7F454C46', 'offset': 0},
        {'name': 'PE/MZ', 'hex': '4D5A', 'offset': 0}
    ]
    
    def _setup_options(self):
        self.add_option('QUERY', 'Search query (name or hex)', required=False)
        self.add_option('MODE', 'list or search', default='list')
        self.add_option('ADD_NAME', 'Custom name to add', required=False)
        self.add_option('ADD_HEX', 'Custom hex to add', required=False)
    
    def run(self) -> dict:
        mode = self.get_option('MODE').lower()
        
        # Add custom
        add_name = self.get_option('ADD_NAME')
        add_hex = self.get_option('ADD_HEX')
        if add_name and add_hex:
            self.DB.append({'name': add_name, 'hex': add_hex.upper(), 'offset': 0})
            
        if mode == 'list':
            return {'status': 'success', 'result': self.DB}
            
        elif mode == 'search':
            query = self.get_option('QUERY')
            if not query:
                return {'status': 'error', 'message': 'QUERY option required for search mode'}
                
            query = query.upper()
            results = []
            for entry in self.DB:
                if query in entry['name'].upper() or query in entry['hex']:
                    results.append(entry)
                    
            return {'status': 'success', 'result': results}
            
        return {'status': 'error', 'message': 'Unknown mode'}
