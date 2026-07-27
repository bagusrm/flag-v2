from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.columns import Columns
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.syntax import Syntax
from rich.markdown import Markdown
from rich import box
import binascii

from core.constants import BANNER, APP_NAME, FULL_NAME, VERSION, CATEGORY_ICONS

class UI:
    """Rich-based UI component class. Handles all visual output."""
    def __init__(self, console: Console | None = None):
        self.console = console or Console()
    
    def show_banner(self):
        """Show the application banner with version info."""
        self.console.print(BANNER)
        self.console.print(
            f"  [dim]{'─' * 50}[/dim]\n"
            f"  [bold cyan]⚡ {FULL_NAME}[/bold cyan] [dim]|[/dim] "
            f"[bold green]v{VERSION}[/bold green] [dim]|[/dim] "
            f"[yellow]Type 'help' for commands[/yellow]\n"
            f"  [dim]{'─' * 50}[/dim]\n"
        )
    
    def show_modules(self, categories: list[dict]):
        """Show table with category name, icon, description, tool count."""
        table = Table(
            title="Available Categories",
            box=box.ROUNDED,
            header_style="bold magenta",
            border_style="cyan"
        )
        table.add_column("Category", style="bold cyan", no_wrap=True)
        table.add_column("Tools", style="bold green", justify="center")
        table.add_column("Description")
        
        for cat in categories:
            name = cat.get('name', 'Unknown')
            desc = cat.get('description', '')
            count = str(cat.get('tool_count', 0))
            icon = CATEGORY_ICONS.get(name, '🔧')
            table.add_row(f"{icon} {name}", count, desc)
            
        self.console.print(table)
        self.console.print()
    
    def show_tools(self, category: str, tools: list[dict]):
        """Show table of tools in a category."""
        icon = CATEGORY_ICONS.get(category, '🔧')
        table = Table(
            title=f"Tools in {icon} [bold cyan]{category}[/bold cyan]",
            box=box.ROUNDED,
            header_style="bold magenta",
            border_style="blue"
        )
        table.add_column("Name", style="bold green", no_wrap=True)
        table.add_column("Description")
        
        for t in tools:
            table.add_row(t.get('name', ''), t.get('description', ''))
            
        self.console.print(table)
        self.console.print()
    
    def show_options(self, tool_info: dict, options: dict):
        """Show table of options for current tool."""
        table = Table(
            title=f"Options for [bold cyan]{tool_info.get('category', '')}/{tool_info.get('name', '')}[/bold cyan]",
            box=box.ROUNDED,
            header_style="bold magenta",
            border_style="blue"
        )
        table.add_column("Name", style="bold cyan")
        table.add_column("Current Setting", style="green")
        table.add_column("Required", justify="center")
        table.add_column("Description")
        
        for name, opt in options.items():
            req = "[bold red]yes[/bold red]" if opt.required else "[bold yellow]no[/bold yellow]"
            val = str(opt.current_value) if opt.current_value is not None else ""
            if not val and opt.default is not None:
                val = str(opt.default)
            table.add_row(name, val, req, opt.description)
            
        self.console.print(table)
        self.console.print()
    
    def show_tool_info(self, info: dict):
        """Show detailed info panel for a tool."""
        text = Text()
        text.append(f"Name:        ", style="bold cyan")
        text.append(f"{info.get('name', '')}\n")
        
        text.append(f"Category:    ", style="bold cyan")
        text.append(f"{info.get('category', '')}\n")
        
        text.append(f"Author:      ", style="bold cyan")
        text.append(f"{info.get('author', '')}\n")
        
        text.append(f"Version:     ", style="bold cyan")
        text.append(f"{info.get('version', '')}\n\n")
        
        text.append(f"Description:\n", style="bold cyan")
        text.append(f"  {info.get('description', '')}\n\n")
        
        if info.get('references'):
            text.append(f"References:\n", style="bold cyan")
            for ref in info.get('references', []):
                text.append(f"  - {ref}\n")
                
        panel = Panel(
            text,
            title=f"[bold green]Tool Info[/bold green]",
            box=box.ROUNDED,
            border_style="magenta",
            padding=(1, 2)
        )
        self.console.print(panel)
        self.console.print()
    
    def show_result(self, result: dict):
        """Show result in a styled panel."""
        status = result.get('status', 'success')
        data = result.get('result', '')
        details = result.get('details', '')
        
        border_style = "green" if status == "success" else "red"
        title = f"[bold {border_style}]Execution Result[/bold {border_style}]"
        
        content = Text()
        content.append(f"Status: {status.upper()}\n\n", style=f"bold {border_style}")
        
        if isinstance(data, dict):
            for k, v in data.items():
                content.append(f"{k}: ", style="bold cyan")
                content.append(f"{v}\n")
        else:
            content.append(f"{data}\n")
            
        if details:
            content.append(f"\nDetails:\n{details}")
            
        panel = Panel(content, title=title, box=box.ROUNDED, border_style=border_style, padding=(1, 2))
        self.console.print(panel)
        self.console.print()
    
    def show_search_results(self, results: list[dict]):
        """Show search results table."""
        table = Table(
            title="Search Results",
            box=box.ROUNDED,
            header_style="bold magenta",
            border_style="blue"
        )
        table.add_column("Category", style="bold cyan")
        table.add_column("Name", style="bold green")
        table.add_column("Description")
        
        for r in results:
            table.add_row(r.get('category', ''), r.get('name', ''), r.get('description', ''))
            
        self.console.print(table)
        self.console.print()
    
    def show_help(self, commands: dict[str, str]):
        """Show help table with command descriptions."""
        table = Table(
            title="Core Commands",
            box=box.ROUNDED,
            header_style="bold magenta",
            border_style="blue"
        )
        table.add_column("Command", style="bold cyan")
        table.add_column("Description")
        
        for cmd, desc in commands.items():
            table.add_row(cmd, desc)
            
        self.console.print(table)
        self.console.print()
    
    def show_history(self, history: list[str]):
        """Show command history."""
        table = Table(
            title="Command History",
            box=box.ROUNDED,
            header_style="bold magenta",
            border_style="blue"
        )
        table.add_column("#", style="dim", justify="right")
        table.add_column("Command", style="green")
        
        for i, cmd in enumerate(history, 1):
            table.add_row(str(i), cmd)
            
        self.console.print(table)
        self.console.print()
    
    def info(self, msg: str):
        """Print an info message."""
        self.console.print(f"[bold blue][*][/bold blue] {msg}")
        
    def success(self, msg: str):
        """Print a success message."""
        self.console.print(f"[bold green][+][/bold green] {msg}")
        
    def error(self, msg: str):
        """Print an error message."""
        self.console.print(f"[bold red][-][/bold red] {msg}")
        
    def warning(self, msg: str):
        """Print a warning message."""
        self.console.print(f"[bold yellow][!][/bold yellow] {msg}")
        
    def debug(self, msg: str):
        """Print a debug message."""
        self.console.print(f"[dim gray][?][/dim gray] [dim]{msg}[/dim]")
    
    def show_version(self):
        """Show version info panel."""
        panel = Panel(
            f"[bold cyan]{FULL_NAME}[/bold cyan]\nVersion: {VERSION}",
            box=box.ROUNDED,
            border_style="blue",
            padding=(1, 2)
        )
        self.console.print(panel)
        self.console.print()
    
    def progress(self, description: str):
        """Return a Rich Progress context manager."""
        return Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
            console=self.console
        )
    
    def show_hex_dump(self, data: bytes, title: str = ''):
        """Show formatted hex dump in a panel."""
        if not data:
            self.warning("No data to dump")
            return
            
        hex_data = binascii.hexlify(data).decode('ascii')
        formatted = ""
        for i in range(0, len(hex_data), 32):
            chunk = hex_data[i:i+32]
            spaced = " ".join([chunk[j:j+2] for j in range(0, len(chunk), 2)])
            
            ascii_chars = ""
            for j in range(0, len(chunk), 2):
                byte = int(chunk[j:j+2], 16)
                if 32 <= byte <= 126:
                    ascii_chars += chr(byte)
                else:
                    ascii_chars += "."
                    
            offset = f"{i//2:08x}"
            formatted += f"{offset}  {spaced:<47}  |{ascii_chars}|\n"
            
        panel = Panel(
            formatted,
            title=title or "Hex Dump",
            box=box.ROUNDED,
            border_style="cyan"
        )
        self.console.print(panel)
        self.console.print()
