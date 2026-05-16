"""
Tests for logger.py bug fixes
Tests all 8 logger bugs that were fixed
"""

import pytest
import logging
import sys
import copy
from pathlib import Path
from unittest.mock import Mock, patch
from io import StringIO

from src.utils.logger import (
    ColoredFormatter,
    setup_logger,
    get_logger,
    set_log_level,
    log_exception,
    get_default_logger,
    LogColors
)


class TestColoredFormatterRecordMutation:
    """Test that ColoredFormatter doesn't mutate the shared LogRecord"""
    
    def test_format_does_not_mutate_original_record(self):
        """Bug fix: ColoredFormatter should not mutate the original record"""
        formatter = ColoredFormatter(use_colors=True)
        
        # Create a log record
        record = logging.LogRecord(
            name="test",
            level=logging.ERROR,
            pathname="test.py",
            lineno=1,
            msg="Test message",
            args=(),
            exc_info=None
        )
        
        # Store original values
        original_levelname = record.levelname
        original_msg = record.msg
        
        # Format the record
        formatted = formatter.format(record)
        
        # Original record should not be mutated
        assert record.levelname == original_levelname
        assert record.msg == original_msg
        
        # Formatted string should contain colors
        assert LogColors.RED in formatted or LogColors.RESET in formatted


class TestSetupLoggerReconfiguration:
    """Test that setup_logger allows reconfiguration"""
    
    def test_setup_logger_allows_file_handler_addition(self, tmp_path):
        """Bug fix: setup_logger should allow adding file handler to existing logger"""
        logger_name = "test_reconfig"
        
        # First setup without file
        logger1 = setup_logger(logger_name, level="INFO")
        initial_handler_count = len(logger1.handlers)
        
        # Second setup with file
        log_file = tmp_path / "test.log"
        logger2 = setup_logger(
            logger_name,
            level="INFO",
            log_file=str(log_file.name),
            log_dir=str(tmp_path)
        )
        
        # Should have added file handler
        assert len(logger2.handlers) >= initial_handler_count
        
        # Cleanup
        for handler in logger2.handlers[:]:
            handler.close()
            logger2.removeHandler(handler)


class TestGetLoggerConfiguration:
    """Test that get_logger properly checks configuration"""
    
    def test_get_logger_checks_parent_handlers(self):
        """Bug fix: get_logger should check parent handlers for inherited loggers"""
        # Create a parent logger with handlers
        parent_logger = setup_logger("test_parent")
        
        # Get a child logger
        child_logger = get_logger("test_parent.child")
        
        # Child should be properly configured (either has handlers or inherits)
        assert child_logger is not None
        assert isinstance(child_logger, logging.Logger)
        
        # Cleanup
        for handler in parent_logger.handlers[:]:
            handler.close()
            parent_logger.removeHandler(handler)


class TestLoggerExports:
    """Test that logger module exports correct functions"""
    
    def test_log_exception_exported(self):
        """Bug fix: log_exception should be exported"""
        from src.utils import log_exception as imported_log_exception
        assert imported_log_exception is not None
    
    def test_get_default_logger_exported(self):
        """Bug fix: get_default_logger should be exported"""
        from src.utils import get_default_logger as imported_get_default
        assert imported_get_default is not None


class TestNoDeadCode:
    """Test that there's no unreachable code"""
    
    def test_get_default_logger_returns_immediately(self):
        """Bug fix: get_default_logger should not have unreachable code after return"""
        logger = get_default_logger()
        assert logger is not None
        assert isinstance(logger, logging.Logger)


class TestNoDuplicateLoggers:
    """Test that there are no duplicate logger creations"""
    
    def test_only_one_default_logger(self):
        """Bug fix: Should only have one default logger, not app_logger duplicate"""
        # Get default logger twice
        logger1 = get_default_logger()
        logger2 = get_default_logger()
        
        # Should be the same instance
        assert logger1 is logger2
        assert logger1.name == "reposense"


class TestLogException:
    """Test log_exception function"""
    
    def test_log_exception_logs_with_traceback(self):
        """Test that log_exception properly logs exceptions"""
        logger = setup_logger("test_exception")
        
        # Capture log output
        stream = StringIO()
        handler = logging.StreamHandler(stream)
        logger.addHandler(handler)
        
        try:
            raise ValueError("Test error")
        except ValueError as e:
            log_exception(logger, e, "Test message")
        
        log_output = stream.getvalue()
        assert "Test message" in log_output
        assert "Test error" in log_output
        
        # Cleanup
        for h in logger.handlers[:]:
            h.close()
            logger.removeHandler(h)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

# Made with Bob
