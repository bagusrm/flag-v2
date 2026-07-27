from core.base_tool import BaseTool, register_tool
from core.exceptions import ExecutionError
import xml.etree.ElementTree as ET

@register_tool
class SitemapParser(BaseTool):
    name = 'sitemap_parser'
    category = 'web'
    description = 'Sitemap.xml parser'
    tags = ['web', 'sitemap', 'xml']

    def _setup_options(self):
        self.add_option('DATA', 'sitemap XML content', required=True)

    def run(self) -> dict:
        data = self.get_option('DATA')
        try:
            root = ET.fromstring(data)
            urls = []
            # Extract URLs namespace agnostic
            for loc in root.iter():
                if 'loc' in loc.tag:
                    urls.append(loc.text)
                    
            return {'status': 'success', 'result': {'urls': urls}}
        except Exception as e:
            raise ExecutionError(f"Error parsing sitemap: {str(e)}")
