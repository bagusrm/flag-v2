from core.base_tool import BaseTool, register_tool
from core.exceptions import ExecutionError
from html.parser import HTMLParser

class CTFHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.forms = []
    
    def handle_starttag(self, tag, attrs):
        attr_dict = dict(attrs)
        if tag == 'a' and 'href' in attr_dict:
            self.links.append(attr_dict['href'])
        elif tag == 'form':
            self.forms.append(attr_dict)

@register_tool
class HtmlParserTool(BaseTool):
    name = 'html_parser'
    category = 'web'
    description = 'HTML analysis tool'
    tags = ['web', 'html', 'parse']

    def _setup_options(self):
        self.add_option('DATA', 'HTML content', required=True)
        self.add_option('MODE', 'Mode', required=False, default='all')

    def run(self) -> dict:
        data = self.get_option('DATA')
        parser = CTFHTMLParser()
        parser.feed(data)
        
        return {'status': 'success', 'result': {
            'links': parser.links,
            'forms': parser.forms
        }}
