import json
import datetime
from core.base_tool import BaseTool, register_tool
from core.exceptions import ExecutionError

@register_tool
class ReportGenerator(BaseTool):
    name = 'report_generator'
    category = 'misc'
    description = 'Generate analysis reports from session'
    tags = ['automation', 'report']

    def _setup_options(self):
        self.add_option('FORMAT', 'html or markdown', required=False, default='markdown')
        self.add_option('OUTPUT', 'Output file path', required=False, default='report')
        self.add_option('SESSION_FILE', 'Session JSON file', required=False, default='')

    def _generate_markdown(self, data: dict, output_path: str):
        md = f"# CTF Analysis Report\n"
        md += f"**Generated:** {datetime.datetime.now().isoformat()}\n\n"
        md += f"## Summary Statistics\n"
        md += f"- Total Tools Run: {len(data.get('history', []))}\n\n"
        
        md += f"## Execution History\n"
        for item in data.get('history', []):
            md += f"### Tool: {item.get('tool', 'Unknown')}\n"
            md += f"- **Time**: {item.get('time', 'N/A')}\n"
            md += f"- **Input**: `{item.get('input', 'N/A')}`\n"
            md += f"```json\n{json.dumps(item.get('output', {}), indent=2)}\n```\n\n"
            
        with open(output_path, 'w') as f:
            f.write(md)
        return output_path

    def _generate_html(self, data: dict, output_path: str):
        html = f"""<!DOCTYPE html>
<html>
<head>
<style>
    body {{ background-color: #1e1e1e; color: #d4d4d4; font-family: monospace; padding: 20px; }}
    h1, h2, h3 {{ color: #569cd6; }}
    .entry {{ border: 1px solid #333; padding: 10px; margin-bottom: 15px; border-radius: 5px; }}
    pre {{ background-color: #2d2d2d; padding: 10px; overflow-x: auto; border-radius: 3px; }}
</style>
<title>CTF Analysis Report</title>
</head>
<body>
<h1>CTF Analysis Report</h1>
<p>Generated: {datetime.datetime.now().isoformat()}</p>
<h2>Summary Statistics</h2>
<p>Total Tools Run: {len(data.get('history', []))}</p>
<h2>Execution History</h2>
"""
        for item in data.get('history', []):
            html += f"""<div class="entry">
<h3>Tool: {item.get('tool', 'Unknown')}</h3>
<p><strong>Time:</strong> {item.get('time', 'N/A')}</p>
<p><strong>Input:</strong> <code>{item.get('input', 'N/A')}</code></p>
<pre>{json.dumps(item.get('output', {}), indent=2)}</pre>
</div>
"""
        html += "</body></html>"
        with open(output_path, 'w') as f:
            f.write(html)
        return output_path

    def run(self) -> dict:
        fmt = self.get_option('FORMAT').lower()
        output = self.get_option('OUTPUT')
        sess_file = self.get_option('SESSION_FILE')

        if fmt not in ['html', 'markdown']:
            raise ExecutionError("FORMAT must be 'html' or 'markdown'")

        session_data = {'history': []}
        if sess_file:
            try:
                with open(sess_file, 'r') as f:
                    session_data = json.load(f)
            except Exception as e:
                raise ExecutionError(f"Failed to load session file: {e}")

        try:
            if fmt == 'html':
                if not output.endswith('.html'): output += '.html'
                final_path = self._generate_html(session_data, output)
            else:
                if not output.endswith('.md'): output += '.md'
                final_path = self._generate_markdown(session_data, output)
        except Exception as e:
            raise ExecutionError(f"Failed to write report: {e}")

        return {
            'status': 'success',
            'report_file': final_path,
            'format': fmt
        }
