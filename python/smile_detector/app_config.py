import json
import logging
import os

class _AppConfig:
    """Configuration class for the application."""
    def __init__(self):
        self.app_name = None
        self.logging_config = None
        self.database_path = None
        self.logger = None
        self.hostname = None
        self.port = None
        self.webcam_index = None
        self.pid = None
        self._initialize()
        


    def _initialize(self):
        """Get the application configuration."""
        with open(f"{os.path.dirname(__file__)}/../conf/config.json", "r") as config_file:
            cfg = json.load(config_file)

        self.app_name = cfg['python']["flask_app_name"]
        self.logging_config = cfg['python']["logging"]
        self.database_path = cfg['sqlite']["db_path"]
        self.hostname = cfg['python']["network"]["hostname"]
        self.port = cfg['python']["network"]["port"]
        self.webcam_index = cfg['python'].get("webcam_index", 0)
        self.pid = os.getpid()

        self.logger = self._get_logger()


    def _get_logger(self):
        """Setup the logger for the application."""
        logging.config.dictConfig(self.logging_config)
        logger = logging.getLogger(self.app_name)
        return logger


config = _AppConfig()
logger = config.logger
