"""
JSON Storage Utility for QuickTradeApp
Handles data persistence using JSON files instead of database
"""
import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

class JSONStorage:
    """JSON-based storage system for QuickTradeApp"""
    
    def __init__(self, storage_dir: str = "data"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
        
        # Initialize data files
        self.users_file = self.storage_dir / "users.json"
        self.sessions_file = self.storage_dir / "sessions.json"
        self.trades_file = self.storage_dir / "trades.json"
        self.portfolio_file = self.storage_dir / "portfolio.json"
        
        # Create files if they don't exist
        self._initialize_files()
    
    def _initialize_files(self):
        """Initialize JSON files with default structure"""
        files_to_init = {
            self.users_file: {"users": []},
            self.sessions_file: {"sessions": {}},
            self.trades_file: {"trades": []},
            self.portfolio_file: {"portfolios": {}}
        }
        
        for file_path, default_data in files_to_init.items():
            if not file_path.exists():
                self._write_json(file_path, default_data)
    
    def _read_json(self, file_path: Path) -> Dict:
        """Read JSON file safely"""
        try:
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except (json.JSONDecodeError, FileNotFoundError):
            return {}
    
    def _write_json(self, file_path: Path, data: Dict):
        """Write JSON file safely"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error writing to {file_path}: {e}")
    
    # User Management
    def save_user_session(self, user_id: str, session_data: Dict):
        """Save user session data"""
        data = self._read_json(self.sessions_file)
        data["sessions"][user_id] = {
            "data": session_data,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        self._write_json(self.sessions_file, data)
    
    def get_user_session(self, user_id: str) -> Optional[Dict]:
        """Get user session data"""
        data = self._read_json(self.sessions_file)
        session = data.get("sessions", {}).get(user_id)
        if session:
            # Update last accessed time
            session["updated_at"] = datetime.now().isoformat()
            self._write_json(self.sessions_file, data)
            return session.get("data", {})
        return None
    
    def delete_user_session(self, user_id: str):
        """Delete user session data"""
        data = self._read_json(self.sessions_file)
        if user_id in data.get("sessions", {}):
            del data["sessions"][user_id]
            self._write_json(self.sessions_file, data)
    
    # Trade Management
    def save_trade(self, trade_data: Dict):
        """Save a trade record"""
        data = self._read_json(self.trades_file)
        trade_data["id"] = len(data.get("trades", [])) + 1
        trade_data["created_at"] = datetime.now().isoformat()
        data["trades"].append(trade_data)
        self._write_json(self.trades_file, data)
        return trade_data["id"]
    
    def get_user_trades(self, user_id: str) -> List[Dict]:
        """Get trades for a specific user"""
        data = self._read_json(self.trades_file)
        return [trade for trade in data.get("trades", []) if trade.get("user_id") == user_id]
    
    def get_all_trades(self) -> List[Dict]:
        """Get all trades"""
        data = self._read_json(self.trades_file)
        return data.get("trades", [])
    
    # Portfolio Management
    def save_portfolio(self, user_id: str, portfolio_data: Dict):
        """Save user portfolio data"""
        data = self._read_json(self.portfolio_file)
        data["portfolios"][user_id] = {
            "data": portfolio_data,
            "updated_at": datetime.now().isoformat()
        }
        self._write_json(self.portfolio_file, data)
    
    def get_portfolio(self, user_id: str) -> Optional[Dict]:
        """Get user portfolio data"""
        data = self._read_json(self.portfolio_file)
        portfolio = data.get("portfolios", {}).get(user_id)
        return portfolio.get("data", {}) if portfolio else None
    
    # Utility Methods
    def clear_expired_sessions(self, max_age_hours: int = 24):
        """Clear expired sessions"""
        data = self._read_json(self.sessions_file)
        current_time = datetime.now()
        expired_sessions = []
        
        for user_id, session in data.get("sessions", {}).items():
            updated_at = datetime.fromisoformat(session.get("updated_at", "1970-01-01T00:00:00"))
            if (current_time - updated_at).total_seconds() > max_age_hours * 3600:
                expired_sessions.append(user_id)
        
        for user_id in expired_sessions:
            del data["sessions"][user_id]
        
        if expired_sessions:
            self._write_json(self.sessions_file, data)
            print(f"Cleared {len(expired_sessions)} expired sessions")
    
    def backup_data(self, backup_dir: str = "backups"):
        """Create a backup of all data"""
        backup_path = Path(backup_dir)
        backup_path.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = backup_path / f"backup_{timestamp}.json"
        
        backup_data = {
            "backup_created": datetime.now().isoformat(),
            "users": self._read_json(self.users_file),
            "sessions": self._read_json(self.sessions_file),
            "trades": self._read_json(self.trades_file),
            "portfolio": self._read_json(self.portfolio_file)
        }
        
        self._write_json(backup_file, backup_data)
        return backup_file

# Global instance
json_storage = JSONStorage() 