"""
Tests for parser.py bug fixes
Tests cognitive complexity reduction and variable shadowing fix
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock

from src.parser import (
    parse_codebase,
    parse_file,
    _collect_all_files,
    _filter_files_by_language_and_size,
    _validate_filtered_files,
    _parse_files_with_progress
)


class TestCognitiveComplexityReduction:
    """Test that parse_codebase has been refactored to reduce complexity"""
    
    def test_helper_functions_exist(self):
        """Bug fix: Helper functions should exist to reduce cognitive complexity"""
        # All helper functions should be defined
        assert callable(_collect_all_files)
        assert callable(_filter_files_by_language_and_size)
        assert callable(_validate_filtered_files)
        assert callable(_parse_files_with_progress)
    
    def test_collect_all_files_function(self, tmp_path):
        """Test _collect_all_files helper"""
        # Create test structure
        (tmp_path / "test.py").write_text("# test")
        (tmp_path / "node_modules").mkdir()
        (tmp_path / "node_modules" / "lib.js").write_text("// lib")
        
        files = _collect_all_files(tmp_path)
        
        # Should find test.py but not node_modules/lib.js
        file_names = [f.name for f in files]
        assert "test.py" in file_names
        assert "lib.js" not in file_names
    
    def test_filter_files_by_language_and_size(self, tmp_path):
        """Test _filter_files_by_language_and_size helper"""
        # Create test files
        py_file = tmp_path / "test.py"
        py_file.write_text("# test")
        
        txt_file = tmp_path / "readme.txt"
        txt_file.write_text("readme")
        
        all_files = [py_file, txt_file]
        supported_languages = ["py", "python"]
        max_size = 1024 * 1024  # 1MB
        
        filtered = _filter_files_by_language_and_size(
            all_files,
            supported_languages,
            max_size
        )
        
        # Should only include .py file
        assert len(filtered) == 1
        assert filtered[0].name == "test.py"
    
    def test_validate_filtered_files_raises_on_empty(self):
        """Test _validate_filtered_files helper"""
        with pytest.raises(ValueError) as exc_info:
            _validate_filtered_files([], [], ["python"])
        
        assert "No files found" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_parse_files_with_progress(self, tmp_path):
        """Test _parse_files_with_progress helper"""
        # Create a test file
        test_file = tmp_path / "test.py"
        test_file.write_text("# test file\n")
        
        parsed_files, import_graph = await _parse_files_with_progress(
            [test_file],
            tmp_path,
            None  # No job_id
        )
        
        assert len(parsed_files) == 1
        assert isinstance(import_graph, dict)


class TestVariableShadowingFix:
    """Test that variable shadowing in parse_file is fixed"""
    
    @pytest.mark.asyncio
    async def test_parse_file_no_variable_shadowing(self, tmp_path):
        """Bug fix: rel_path should not be declared twice with type annotations"""
        test_file = tmp_path / "test.py"
        test_file.write_text("# test\n")
        
        # This should not raise any errors
        parsed = await parse_file(test_file, tmp_path)
        
        assert parsed is not None
        assert parsed.path is not None


class TestParseCodebaseIntegration:
    """Integration tests for parse_codebase"""
    
    @pytest.mark.asyncio
    async def test_parse_codebase_basic(self, tmp_path):
        """Test basic codebase parsing"""
        # Create test structure
        (tmp_path / "main.py").write_text("# main\n")
        (tmp_path / "utils.py").write_text("# utils\n")
        
        with patch('src.parser.settings') as mock_settings:
            mock_settings.get_supported_languages_list.return_value = ["py"]
            mock_settings.get_max_file_size_bytes.return_value = 1024 * 1024
            mock_settings.max_files_per_analysis = 1000
            
            result = await parse_codebase(str(tmp_path))
            
            assert result is not None
            assert len(result.files) == 2
    
    @pytest.mark.asyncio
    async def test_parse_codebase_with_job_tracking(self, tmp_path):
        """Test codebase parsing with job progress tracking"""
        (tmp_path / "test.py").write_text("# test\n")
        
        with patch('src.parser.settings') as mock_settings:
            mock_settings.get_supported_languages_list.return_value = ["py"]
            mock_settings.get_max_file_size_bytes.return_value = 1024 * 1024
            mock_settings.max_files_per_analysis = 1000
            
            with patch('src.parser.update_job_progress') as mock_update:
                result = await parse_codebase(str(tmp_path), job_id="test_job")
                
                # Should have called update_job_progress
                assert mock_update.called
    
    @pytest.mark.asyncio
    async def test_parse_codebase_filters_ignored_dirs(self, tmp_path):
        """Test that ignored directories are skipped"""
        # Create files in ignored directories
        (tmp_path / "node_modules").mkdir()
        (tmp_path / "node_modules" / "lib.js").write_text("// lib")
        (tmp_path / ".git").mkdir()
        (tmp_path / ".git" / "config").write_text("config")
        (tmp_path / "main.py").write_text("# main")
        
        with patch('src.parser.settings') as mock_settings:
            mock_settings.get_supported_languages_list.return_value = ["py", "js"]
            mock_settings.get_max_file_size_bytes.return_value = 1024 * 1024
            mock_settings.max_files_per_analysis = 1000
            
            result = await parse_codebase(str(tmp_path))
            
            # Should only find main.py, not files in ignored dirs
            assert len(result.files) == 1
            assert result.files[0].path == "main.py"
    
    @pytest.mark.asyncio
    async def test_parse_codebase_respects_file_limit(self, tmp_path):
        """Test that max_files_per_analysis is respected"""
        # Create many files
        for i in range(10):
            (tmp_path / f"file{i}.py").write_text(f"# file {i}\n")
        
        with patch('src.parser.settings') as mock_settings:
            mock_settings.get_supported_languages_list.return_value = ["py"]
            mock_settings.get_max_file_size_bytes.return_value = 1024 * 1024
            mock_settings.max_files_per_analysis = 5  # Limit to 5 files
            
            result = await parse_codebase(str(tmp_path))
            
            # Should only parse 5 files
            assert len(result.files) == 5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

# Made with Bob
