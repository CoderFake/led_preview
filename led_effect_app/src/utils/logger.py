import flet as ft
from enum import Enum
from typing import Optional
import logging
import sys
from datetime import datetime


class LogLevel(Enum):
    """Log levels for different types of messages"""
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"


class TerminalLogger:
    """Terminal-based logger for services"""
    
    def __init__(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def info(self, message: str):
        """Log info message to terminal"""
        self.logger.info(message)
    
    def success(self, message: str):
        """Log success message to terminal"""
        self.logger.info(f"✓ {message}")
    
    def warning(self, message: str):
        """Log warning message to terminal"""
        self.logger.warning(message)
    
    def error(self, message: str):
        """Log error message to terminal"""
        self.logger.error(message)


class AppLogger:
    """Global terminal logger instance for services"""
    _terminal_logger = None
    
    @classmethod
    def initialize(cls):
        """Initialize the global terminal logger"""
        if cls._terminal_logger is None:
            cls._terminal_logger = TerminalLogger()
    
    @classmethod
    def get_logger(cls) -> TerminalLogger:
        """Get the global terminal logger instance"""
        if cls._terminal_logger is None:
            cls.initialize()
        return cls._terminal_logger
    
    @classmethod
    def info(cls, message: str):
        """Log info message to terminal"""
        cls.get_logger().info(message)
    
    @classmethod
    def success(cls, message: str):
        """Log success message to terminal"""
        cls.get_logger().success(message)
    
    @classmethod
    def warning(cls, message: str):
        """Log warning message to terminal"""
        cls.get_logger().warning(message)
    
    @classmethod
    def error(cls, message: str):
        """Log error message to terminal"""
        cls.get_logger().error(message)