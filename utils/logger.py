import logging
from typing import List, Dict, Any, Optional

class AppLogger:
    def __init__(self, name: str = "app_logger"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        self.warnings: List[Dict[str, Any]] = []
        self.errors: List[Dict[str, Any]] = []

        # Configure console handler
        console_handler = logging.StreamHandler()
        console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)

        # Optional: Configure file handler for log.txt (for CLI output)
        # This part might be better managed by the CLI/API main entry points
        # For now, we'll focus on in-memory collection and console output.

    def info(self, message: str, context: Optional[Dict[str, Any]] = None):
        full_message = f"{message} (Context: {context})" if context else message
        self.logger.info(full_message)

    def warning(self, message: str, context: Optional[Dict[str, Any]] = None):
        full_message = f"{message} (Context: {context})" if context else message
        self.logger.warning(full_message)
        self.warnings.append({"level": "WARNING", "message": message, "context": context if context else {}})

    def error(self, message: str, context: Optional[Dict[str, Any]] = None):
        full_message = f"{message} (Context: {context})" if context else message
        self.logger.error(full_message)
        self.errors.append({"level": "ERROR", "message": message, "context": context if context else {}})

    def get_warnings(self) -> List[Dict[str, Any]]:
        return self.warnings

    def get_errors(self) -> List[Dict[str, Any]]:
        return self.errors

    def clear_messages(self):
        self.warnings = []
        self.errors = [] 