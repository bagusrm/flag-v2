from core.registry import ModuleRegistry
from core.ui import UI
from core.session import Session
from core.config import Config
from core.logger import get_logger
from core.base_tool import BaseTool
from core.constants import DEFAULT_PROMPT, VERSION
from core.exceptions import ValidationError, ExecutionError, InvalidOptionError, SessionError

class CommandHandler:
    """Routes CLI commands to their respective handlers."""
    def __init__(self, registry: ModuleRegistry, ui: UI, session: Session, config: Config):
        self.registry = registry
        self.ui = ui
        self.session = session
        self.config = config
        self.logger = get_logger('command_handler')
        self._current_tool: BaseTool | None = None
        self._commands: dict[str, tuple[callable, str]] = {}
        self._register_commands()
    
    def _register_commands(self):
        """Register all built-in commands with their handlers and descriptions."""
        self._commands = {
            'help': (self._cmd_help, 'Show help information'),
            'modules': (self._cmd_modules, 'List all module categories'),
            'search': (self._cmd_search, 'Search for tools by keyword'),
            'use': (self._cmd_use, 'Select a tool to use (e.g., use crypto/base64)'),
            'info': (self._cmd_info, 'Show information about current tool'),
            'run': (self._cmd_run, 'Execute current tool (supports: run > output.txt)'),
            'set': (self._cmd_set, 'Set an option value (e.g., set DATA hello)'),
            'show': (self._cmd_show, 'Show options/modules/tools'),
            'back': (self._cmd_back, 'Deselect current tool'),
            'spool': (self._cmd_spool, 'Write console output to file (e.g., spool out.txt / spool off)'),
            'history': (self._cmd_history, 'Show command history'),
            'clear': (self._cmd_clear, 'Clear the screen'),
            'exit': (self._cmd_exit, 'Exit the framework'),
            'quit': (self._cmd_exit, 'Exit the framework'),
            'version': (self._cmd_version, 'Show version information'),
            'update': (self._cmd_update, 'Check for updates'),
            'sessions': (self._cmd_sessions, 'Manage sessions'),
            'save': (self._cmd_save, 'Save current session'),
            'load': (self._cmd_load, 'Load a saved session'),
        }
        self._spool_file = None
    
    def handle(self, raw_input: str) -> bool:
        """Parse command and args, route to handler."""
        raw_input = raw_input.strip()
        if not raw_input:
            return True
            
        self.session.add_to_history(raw_input)
        parts = raw_input.split(maxsplit=1)
        cmd = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ''
        
        if cmd in self._commands:
            handler, _ = self._commands[cmd]
            return handler(args)
        else:
            self.ui.error(f'Unknown command: {cmd}. Type "help" for available commands.')
            return True
    
    def _cmd_help(self, args: str):
        if args:
            cmd = args.strip().lower()
            if cmd in self._commands:
                _, desc = self._commands[cmd]
                self.ui.info(f"{cmd}: {desc}")
            else:
                self.ui.error(f"Unknown command: {cmd}")
        else:
            self.ui.show_help({name: desc for name, (_, desc) in self._commands.items()})
        return True
    
    def _cmd_modules(self, args: str):
        categories = self.registry.get_all_categories()
        self.ui.show_modules(categories)
        return True
    
    def _cmd_search(self, args: str):
        if not args:
            self.ui.warning('Usage: search <keyword>')
            return True
        results = self.registry.search(args)
        if results:
            self.ui.show_search_results(results)
        else:
            self.ui.warning(f'No results found for: {args}')
        return True
    
    def _cmd_use(self, args: str):
        if not args:
            self.ui.warning('Usage: use <category/tool>')
            return True
            
        if '/' not in args:
            tools = self.registry.get_category_tools(args)
            if tools:
                self.ui.show_tools(args, tools)
            else:
                self.ui.error(f'Category not found: {args}')
            return True
            
        category, tool_name = args.split('/', 1)
        tool = self.registry.get_tool(category, tool_name)
        
        if tool:
            self._current_tool = tool
            self.session.set_current_tool(tool.full_name)
            self.ui.success(f'Using {tool.full_name}')
        else:
            self.ui.error(f'Tool not found: {args}')
        return True
    
    def _cmd_info(self, args: str):
        if self._current_tool:
            self.ui.show_tool_info(self._current_tool.get_info())
        else:
            self.ui.warning('No tool selected. Use "use <category/tool>" first.')
        return True
    
    def _cmd_run(self, args: str):
        if not self._current_tool:
            self.ui.warning('No tool selected. Use "use <category/tool>" first.')
            return True
        try:
            result = self._current_tool.execute()
            self.ui.show_result(result)
            self.session.add_result(self._current_tool.full_name, result)
        except (ValidationError, ExecutionError) as e:
            self.ui.error(str(e))
        except Exception as e:
            self.ui.error(f'Execution error: {e}')
            self.logger.exception('Tool execution failed')
        return True
    
    def _cmd_set(self, args: str):
        if not self._current_tool:
            self.ui.warning('No tool selected.')
            return True
        parts = args.split(maxsplit=1)
        if len(parts) < 2:
            self.ui.warning('Usage: set <option> <value>')
            return True
        name, value = parts
        try:
            self._current_tool.set_option(name, value)
            self.ui.success(f'{name.upper()} => {value}')
        except InvalidOptionError as e:
            self.ui.error(str(e))
        return True
    
    def _cmd_show(self, args: str):
        arg = args.strip().lower()
        if arg == 'options':
            if self._current_tool:
                self.ui.show_options(self._current_tool.get_info(), self._current_tool.options)
            else:
                self.ui.warning('No tool selected.')
        elif arg == 'modules':
            return self._cmd_modules('')
        else:
            self.ui.warning('Usage: show options | show modules')
        return True
    
    def _cmd_back(self, args: str):
        if self._current_tool:
            self._current_tool = None
            self.session.set_current_tool(None)
            self.ui.info('Returned to main context.')
        return True
    
    def _cmd_history(self, args: str):
        self.ui.show_history(self.session.get_history())
        return True
    
    def _cmd_clear(self, args: str):
        self.ui.console.clear()
        return True
    
    def _cmd_exit(self, args: str):
        self.ui.info('Exiting CAPTURE THE FLAG framework. Goodbye!')
        return False
    
    def _cmd_version(self, args: str):
        self.ui.show_version()
        return True
    
    def _cmd_update(self, args: str):
        self.ui.info(f'Current version: {VERSION}')
        self.ui.info('Update checking is not yet implemented.')
        return True
    
    def _cmd_sessions(self, args: str):
        sessions = self.session.list_sessions()
        if sessions:
            from rich.table import Table
            from rich import box as richbox
            table = Table(title="Saved Sessions", box=richbox.ROUNDED)
            table.add_column("Name", style="cyan")
            table.add_column("Created At", style="green")
            table.add_column("Tools Run", justify="right")
            for s in sessions:
                table.add_row(s['name'], s['created_at'], str(s['tools_run']))
            self.ui.console.print(table)
            self.ui.console.print()
        else:
            self.ui.info('No saved sessions found.')
        return True
    
    def _cmd_save(self, args: str):
        name = args.strip() or None
        try:
            path = self.session.save(name)
            self.ui.success(f'Session saved: {path}')
        except SessionError as e:
            self.ui.error(str(e))
        return True
    
    def _cmd_load(self, args: str):
        if not args.strip():
            self.ui.warning('Usage: load <session_name>')
            return True
        try:
            data = self.session.load(args.strip())
            self.ui.success(f'Session loaded: {args.strip()}')
        except SessionError as e:
            self.ui.error(str(e))
        return True
    
    @property
    def current_tool(self) -> BaseTool | None:
        return self._current_tool
    
    @property
    def prompt_text(self) -> str:
        if self._current_tool:
            return f'{DEFAULT_PROMPT} {self._current_tool.category}({self._current_tool.name})'
        return DEFAULT_PROMPT
    
    def get_command_names(self) -> list[str]:
        return list(self._commands.keys())
