from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter, NestedCompleter, PathCompleter, merge_completers
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.styles import Style

from core.command_handler import CommandHandler
from core.ui import UI
from core.config import Config
from core.logger import get_logger
from core.constants import HISTORY_FILE

class InteractiveCLI:
    """Interactive CLI using prompt_toolkit."""
    def __init__(self, command_handler: CommandHandler, ui: UI, config: Config):
        self.handler = command_handler
        self.ui = ui
        self.config = config
        self.logger = get_logger('cli')
        self._path_completer = PathCompleter(expanduser=True)
        self._setup_prompt()
    
    def _setup_prompt(self):
        style = Style.from_dict({
            'prompt': '#00aa00 bold',
            'tool': '#ff0000 bold',
            'symbol': '#ffffff bold',
        })
        
        self.session = PromptSession(
            history=FileHistory(HISTORY_FILE),
            auto_suggest=AutoSuggestFromHistory(),
            style=style,
            completer=self._create_completer()
        )
    
    def _create_completer(self):
        commands = self.handler.get_command_names()
        
        # Tools completion list
        tools_list = []
        for cat in self.handler.registry.get_all_categories():
            cat_name = cat['name']
            tools_list.append(cat_name)
            for tool in self.handler.registry.get_category_tools(cat_name):
                tools_list.append(f"{cat_name}/{tool['name']}")
                
        completer_dict = {
            'use': WordCompleter(tools_list, ignore_case=True),
            'show': WordCompleter(['options', 'modules', 'tools'], ignore_case=True),
            'help': WordCompleter(commands, ignore_case=True),
            'load': self._path_completer,
            'search': None,
            'set': None,
        }
        
        for cmd in commands:
            if cmd not in completer_dict:
                completer_dict[cmd] = None
                
        return NestedCompleter.from_nested_dict(completer_dict)
    
    def _get_prompt_text(self):
        tool = self.handler.current_tool
        if tool:
            return HTML(f'<prompt>CTF</prompt> <tool>{tool.category}({tool.name})</tool><symbol> > </symbol>')
        return HTML('<prompt>CTF</prompt><symbol> > </symbol>')
    
    def start(self):
        """Start the interactive CLI loop."""
        self.ui.show_banner()
        running = True
        
        while running:
            try:
                # Universal path completion: enable PathCompleter for ALL options in 'set'
                if self.handler.current_tool:
                    opts = list(self.handler.current_tool.options.keys())
                    set_dict = {}
                    for opt_name in opts:
                        # Allow PathCompleter on ALL option values when TAB is pressed
                        set_dict[opt_name] = self._path_completer
                            
                    self.session.completer = merge_completers([
                        self._create_completer(),
                        NestedCompleter.from_nested_dict({'set': set_dict})
                    ])
                else:
                    self.session.completer = self._create_completer()
                    
                user_input = self.session.prompt(self._get_prompt_text())
                running = self.handler.handle(user_input)
                
            except KeyboardInterrupt:
                continue
            except EOFError:
                running = False
            except Exception as e:
                self.ui.error(f"Unexpected error: {e}")
                self.logger.exception("CLI loop error")
                
        self.ui.info('Goodbye!')
