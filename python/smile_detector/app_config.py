import json
import logging
from logging import Logger, getLogger
from logging.config import dictConfig
import os
from typing import Any

class _AppConfig:
    """Configuration class for the application."""
    def __init__(self) -> None:
        with open(f"{os.path.dirname(__file__)}/../conf/config.json", "r") as config_file:
            cfg = json.load(config_file)
        self.database_path: str = cfg['sqlite']["db_path"]
        self.app_name: str = cfg['python']["flask_app_name"]
        self.logging_config: dict[str, Any] = cfg['python']["logging"]
        self.hostname: str = cfg['python']["network"]["hostname"]
        self.port: int  = cfg['python']["network"]["port"]
        self.webcam_index: int = cfg['python'].get("webcam_index", 0)
        self.pid: int = os.getpid()

        dictConfig(self.logging_config)
        self.logger: Logger = logging.getLogger(self.app_name)

config: _AppConfig = _AppConfig()
logger: Logger = config.logger
