import os
from core.base_tool import BaseTool, register_tool
from core.exceptions import ExecutionError
from core.registry import ModuleRegistry

@register_tool
class BatchProcessor(BaseTool):
    name = 'batch_processor'
    category = 'misc'
    description = 'Apply a tool to multiple inputs (files or data list)'
    tags = ['automation', 'batch']

    def _setup_options(self):
        self.add_option('TOOL', 'Tool full name like "crypto/base64"', required=True)
        self.add_option('INPUT_DIR', 'Directory path with input files', required=False, default='')
        self.add_option('DATA_LIST', 'Newline-separated data strings', required=False, default='')
        self.add_option('MODE', 'Tool specific mode parameter', required=False, default='')

    def run(self) -> dict:
        tool_name = self.get_option('TOOL')
        input_dir = self.get_option('INPUT_DIR')
        data_list_str = self.get_option('DATA_LIST')
        mode = self.get_option('MODE')

        if not input_dir and not data_list_str:
            raise ExecutionError("Must provide INPUT_DIR or DATA_LIST")

        parts = tool_name.split('/')
        if len(parts) != 2:
            raise ExecutionError("Tool name must be 'category/name'")
            
        registry = ModuleRegistry()
        tool_class = registry.get_tool(parts[0], parts[1])
        if not tool_class:
            raise ExecutionError(f"Tool not found: {tool_name}")

        results = []
        success_count = 0
        fail_count = 0

        # Process directory
        if input_dir and os.path.isdir(input_dir):
            for fname in os.listdir(input_dir):
                fpath = os.path.join(input_dir, fname)
                if os.path.isfile(fpath):
                    tool = tool_class()
                    if 'FILE' in tool.options:
                        tool.set_option('FILE', fpath)
                    elif 'DATA' in tool.options:
                        with open(fpath, 'rb') as f:
                            tool.set_option('DATA', f.read().decode(errors='ignore'))
                    if mode and 'MODE' in tool.options:
                        tool.set_option('MODE', mode)
                    
                    try:
                        res = tool.run()
                        res['batch_input'] = fpath
                        results.append(res)
                        success_count += 1
                    except Exception as e:
                        results.append({'batch_input': fpath, 'status': 'error', 'error': str(e)})
                        fail_count += 1

        # Process data list
        if data_list_str:
            items = data_list_str.strip().split('\n')
            for item in items:
                if not item.strip(): continue
                tool = tool_class()
                if 'DATA' in tool.options:
                    tool.set_option('DATA', item)
                elif 'INPUT' in tool.options:
                    tool.set_option('INPUT', item)
                if mode and 'MODE' in tool.options:
                    tool.set_option('MODE', mode)
                
                try:
                    res = tool.run()
                    res['batch_input'] = item
                    results.append(res)
                    success_count += 1
                except Exception as e:
                    results.append({'batch_input': item, 'status': 'error', 'error': str(e)})
                    fail_count += 1

        return {
            'status': 'success',
            'total_processed': success_count + fail_count,
            'success_count': success_count,
            'fail_count': fail_count,
            'results': results
        }
