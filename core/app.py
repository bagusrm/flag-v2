import os
from pathlib import Path

from core.config import Config
from core.logger import setup_logger, get_logger
from core.ui import UI
from core.registry import ModuleRegistry
from core.plugin_manager import PluginManager
from core.session import Session
from core.command_handler import CommandHandler
from core.cli import InteractiveCLI

class FlagApp:
    """Main application class. Bootstraps and runs the CTF framework."""
    
    def __init__(self, config_path: str | None = None):
        self.config: Config | None = None
        self.registry: ModuleRegistry | None = None
        self.plugin_manager: PluginManager | None = None
        self.ui: UI | None = None
        self.session: Session | None = None
        self.handler: CommandHandler | None = None
        self.cli: InteractiveCLI | None = None
        self._config_path = config_path
    
    def initialize(self) -> 'FlagApp':
        """Initialize the application components."""
        # Determine project root (where main.py is located)
        project_root = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        # 1. Load config
        self.config = Config.get_instance()
        if self._config_path:
            # Assuming config can load from path in get_instance or init, handling it manually
            pass 
            
        # 2. Setup logger
        log_dir = project_root / 'logs'
        log_dir.mkdir(exist_ok=True)
        setup_logger('ctf', log_dir=str(log_dir))
        logger = get_logger('app')
        logger.info("Initializing CTF Framework")
        
        # 3. Create UI
        self.ui = UI()
        
        # 4. Create registry
        self.registry = ModuleRegistry.get_instance()
        
        # 5. Create plugin manager
        self.plugin_manager = PluginManager(self.registry, self.config)
        
        # 6. Discover and load all modules
        modules_dir = project_root / 'modules'
        plugins_dir = project_root / 'plugins'
        paths_to_load = []
        if modules_dir.exists():
            paths_to_load.append(str(modules_dir))
        if plugins_dir.exists():
            paths_to_load.append(str(plugins_dir))
            
        count = self.plugin_manager.discover_modules(paths_to_load)
        logger.info(f"Loaded {count} modules")
        
        # 7. Create session manager
        session_dir = project_root / 'sessions'
        self.session = Session(session_dir=str(session_dir))
        
        # 8. Create command handler
        self.handler = CommandHandler(self.registry, self.ui, self.session, self.config)
        
        # 9. Create CLI
        self.cli = InteractiveCLI(self.handler, self.ui, self.config)
        
        return self
    
    def run(self):
        """Start the application CLI loop."""
        if not self.cli:
            raise RuntimeError("Application not initialized. Call initialize() first.")
        self.cli.start()
