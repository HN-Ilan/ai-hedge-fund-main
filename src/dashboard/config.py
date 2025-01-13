# In src/dashboard/config.py

from typing import Dict, Any
import json
from pathlib import Path

class ConfigManager:
    DEFAULT_CONFIG = {
        # Risk Management
        "max_position_size": 0.20,
        "stop_loss": 0.10,
        "max_drawdown": 0.20,
        
        # Technical Analysis
        "ma_short_period": 8,
        "ma_medium_period": 21,
        "ma_long_period": 55,
        "rsi_oversold": 30,
        "rsi_overbought": 70,
        "volatility_threshold": 0.30,
        
        # Fundamentals
        "min_roe": 0.15,
        "min_profit_margin": 0.10,
        "max_debt_equity": 2.0,
        "min_revenue_growth": 0.10,
        
        # Valuation
        "required_return": 0.15,
        "growth_rate": 0.05,
        "margin_of_safety": 0.25
    }
    
    def __init__(self, config_path: str = 'trading_config.json'):
        self.config_path = Path(config_path)
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file, using defaults for missing values."""
        if self.config_path.exists():
            try:
                with open(self.config_path) as f:
                    loaded_config = json.load(f)
                    # Merge with defaults, ensuring all parameters exist
                    return {**self.DEFAULT_CONFIG, **loaded_config}
            except json.JSONDecodeError:
                print(f"Error reading config file {self.config_path}, using defaults")
                return self.DEFAULT_CONFIG.copy()
        return self.DEFAULT_CONFIG.copy()
    
    def save_config(self, config: Dict[str, Any]):
        """Save configuration to file."""
        # Merge with existing config to preserve any additional fields
        self.config = {**self.config, **config}
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=4)
    
    def get_technical_params(self) -> Dict[str, Any]:
        """Get technical analysis parameters with defaults."""
        return {
            "ma_periods": {
                "short": self.config.get("ma_short_period", self.DEFAULT_CONFIG["ma_short_period"]),
                "medium": self.config.get("ma_medium_period", self.DEFAULT_CONFIG["ma_medium_period"]),
                "long": self.config.get("ma_long_period", self.DEFAULT_CONFIG["ma_long_period"])
            },
            "rsi": {
                "oversold": self.config.get("rsi_oversold", self.DEFAULT_CONFIG["rsi_oversold"]),
                "overbought": self.config.get("rsi_overbought", self.DEFAULT_CONFIG["rsi_overbought"])
            },
            "volatility_threshold": self.config.get("volatility_threshold", 
                                                  self.DEFAULT_CONFIG["volatility_threshold"])
        }
    
    def get_fundamental_params(self) -> Dict[str, Any]:
        """Get fundamental analysis parameters with defaults."""
        return {
            "min_roe": self.config.get("min_roe", self.DEFAULT_CONFIG["min_roe"]),
            "min_profit_margin": self.config.get("min_profit_margin", 
                                               self.DEFAULT_CONFIG["min_profit_margin"]),
            "max_debt_equity": self.config.get("max_debt_equity", 
                                             self.DEFAULT_CONFIG["max_debt_equity"]),
            "min_revenue_growth": self.config.get("min_revenue_growth", 
                                                self.DEFAULT_CONFIG["min_revenue_growth"])
        }
    
    def get_risk_params(self) -> Dict[str, Any]:
        """Get risk management parameters with defaults."""
        return {
            "max_position_size": self.config.get("max_position_size", 
                                               self.DEFAULT_CONFIG["max_position_size"]),
            "stop_loss": self.config.get("stop_loss", self.DEFAULT_CONFIG["stop_loss"]),
            "max_drawdown": self.config.get("max_drawdown", self.DEFAULT_CONFIG["max_drawdown"])
        }
    
    def get_valuation_params(self) -> Dict[str, Any]:
        """Get valuation parameters with defaults."""
        return {
            "required_return": self.config.get("required_return", 
                                             self.DEFAULT_CONFIG["required_return"]),
            "growth_rate": self.config.get("growth_rate", self.DEFAULT_CONFIG["growth_rate"]),
            "margin_of_safety": self.config.get("margin_of_safety", 
                                              self.DEFAULT_CONFIG["margin_of_safety"])
        }