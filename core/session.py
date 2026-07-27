import json
from pathlib import Path
from datetime import datetime

from core.exceptions import SessionError

class Session:
    """Manages CLI sessions, history, and results."""
    def __init__(self, session_dir: str | Path = 'sessions'):
        self.session_dir = Path(session_dir)
        self.session_dir.mkdir(parents=True, exist_ok=True)
        self.current: dict = {
            'current_tool': None,
            'tool_options': {},
            'history': [],
            'results': [],
            'created_at': datetime.now().isoformat(),
        }
    
    def save(self, name: str | None = None) -> Path:
        """Save current session to JSON file."""
        if not name:
            name = datetime.now().strftime("session_%Y%m%d_%H%M%S")
        if not name.endswith('.json'):
            name += '.json'
            
        filepath = self.session_dir / name
        try:
            with open(filepath, 'w') as f:
                json.dump(self.current, f, indent=4)
            return filepath
        except IOError as e:
            raise SessionError(f"Failed to save session: {e}")
    
    def load(self, name: str) -> dict:
        """Load session from JSON file."""
        if not name.endswith('.json'):
            name += '.json'
            
        filepath = self.session_dir / name
        if not filepath.exists():
            raise SessionError(f"Session file not found: {name}")
            
        try:
            with open(filepath, 'r') as f:
                self.current = json.load(f)
            return self.current
        except (IOError, json.JSONDecodeError) as e:
            raise SessionError(f"Failed to load session: {e}")
    
    def list_sessions(self) -> list[dict]:
        """List all saved sessions with metadata."""
        sessions = []
        for file in self.session_dir.glob('*.json'):
            try:
                with open(file, 'r') as f:
                    data = json.load(f)
                    sessions.append({
                        'name': file.name,
                        'created_at': data.get('created_at', 'Unknown'),
                        'size': file.stat().st_size,
                        'tools_run': len(data.get('results', []))
                    })
            except Exception:
                pass
        return sorted(sessions, key=lambda x: x['created_at'], reverse=True)
    
    def delete(self, name: str) -> bool:
        """Delete a saved session."""
        if not name.endswith('.json'):
            name += '.json'
        filepath = self.session_dir / name
        if filepath.exists():
            filepath.unlink()
            return True
        return False
    
    def add_to_history(self, command: str):
        """Add a command to session history."""
        self.current['history'].append({
            'timestamp': datetime.now().isoformat(),
            'command': command
        })
    
    def add_result(self, tool_name: str, result: dict):
        """Add an execution result to the session."""
        self.current['results'].append({
            'timestamp': datetime.now().isoformat(),
            'tool': tool_name,
            'result': result
        })
    
    def set_current_tool(self, tool_full_name: str | None):
        """Set the currently active tool in the session."""
        self.current['current_tool'] = tool_full_name
    
    def get_history(self) -> list[str]:
        """Get list of executed commands as strings."""
        return [h['command'] for h in self.current.get('history', [])]
