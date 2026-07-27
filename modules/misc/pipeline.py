from core.base_tool import BaseTool, register_tool
from core.exceptions import ExecutionError
from core.registry import ModuleRegistry

@register_tool
class Pipeline(BaseTool):
    name = 'pipeline'
    category = 'misc'
    description = 'Chain multiple tools together sequentially'
    tags = ['automation', 'pipeline', 'chain']

    def _setup_options(self):
        self.add_option('PIPELINE', 'Pipeline definition string (e.g., "crypto/base64 -> crypto/hex")', required=True)
        self.add_option('DATA', 'Initial input data', required=True)

    def run(self) -> dict:
        pipeline_str = self.get_option('PIPELINE')
        current_data = self.get_option('DATA')

        steps = [s.strip() for s in pipeline_str.split('->')]
        if not steps or not steps[0]:
            raise ExecutionError("Invalid pipeline string")

        registry = ModuleRegistry()
        results_log = []

        for step in steps:
            parts = step.split('/')
            if len(parts) != 2:
                raise ExecutionError(f"Invalid tool format in step: {step}. Expected category/name")
            
            cat, name = parts
            tool_class = registry.get_tool(cat, name)
            if not tool_class:
                raise ExecutionError(f"Tool not found: {step}")

            # Instantiate and run tool
            tool = tool_class()
            # Set DATA or INPUT option for the tool
            if 'DATA' in tool.options:
                tool.set_option('DATA', current_data)
            elif 'INPUT' in tool.options:
                tool.set_option('INPUT', current_data)
            elif 'FILE' in tool.options:
                tool.set_option('FILE', current_data)
            else:
                raise ExecutionError(f"Tool {step} does not have a recognizable input option (DATA, INPUT, or FILE)")

            try:
                res = tool.run()
                if res.get('status') != 'success':
                    raise ExecutionError(f"Tool {step} failed: {res}")
                
                # Try to extract the primary output to pass to next step
                # Typically it might be 'result', 'output', 'decoded', etc.
                next_data = res.get('result') or res.get('output') or res.get('decoded')
                if next_data is None:
                    # Fallback to string representation if standard output key is missing
                    next_data = str(res)
                
                results_log.append({
                    'step': step,
                    'input': current_data,
                    'output': next_data,
                    'full_result': res
                })
                current_data = str(next_data)
            except Exception as e:
                raise ExecutionError(f"Error executing {step}: {str(e)}")

        return {
            'status': 'success',
            'final_result': current_data,
            'steps_executed': len(steps),
            'log': results_log
        }
