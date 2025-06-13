"""Tests for the prompts module."""

import pytest
from pathlib import Path
from unittest.mock import patch, mock_open, MagicMock

from src.utils.prompts import load_prompt


class TestLoadPrompt:
    """Test cases for load_prompt function."""

    @patch('pathlib.Path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data='This is a test prompt\n')
    def test_load_prompt_success(self, mock_file, mock_exists):
        """Test successfully loading a prompt file."""
        mock_exists.return_value = True

        result = load_prompt('test_prompt.md')

        assert result == 'This is a test prompt'
        mock_exists.assert_called_once()
        mock_file.assert_called_once()

    @patch('pathlib.Path.exists')
    def test_load_prompt_file_not_found(self, mock_exists):
        """Test loading a non-existent prompt file."""
        mock_exists.return_value = False

        with pytest.raises(FileNotFoundError) as excinfo:
            load_prompt('non_existent.md')

        assert "Prompt file not found:" in str(excinfo.value)
        mock_exists.assert_called_once()

    @patch('pathlib.Path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data='  \n  Prompt with whitespace  \n  ')
    def test_load_prompt_strips_whitespace(self, mock_file, mock_exists):
        """Test that prompt content is stripped of leading/trailing whitespace."""
        mock_exists.return_value = True

        result = load_prompt('whitespace_prompt.md')

        assert result == 'Prompt with whitespace'
        mock_exists.assert_called_once()
        mock_file.assert_called_once()

    @patch('pathlib.Path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data='')
    def test_load_prompt_empty_file(self, mock_file, mock_exists):
        """Test loading an empty prompt file."""
        mock_exists.return_value = True

        result = load_prompt('empty.md')

        assert result == ''
        mock_exists.assert_called_once()
        mock_file.assert_called_once()

    @patch('pathlib.Path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data='Multi\nLine\nPrompt\n')
    def test_load_prompt_multiline(self, mock_file, mock_exists):
        """Test loading a multi-line prompt file."""
        mock_exists.return_value = True

        result = load_prompt('multiline.md')

        assert result == 'Multi\nLine\nPrompt'
        mock_exists.assert_called_once()
        mock_file.assert_called_once()

    def test_load_prompt_path_construction(self):
        """Test that the prompt path is constructed correctly."""
        with patch('pathlib.Path.exists') as mock_exists:
            mock_exists.return_value = False

            try:
                load_prompt('subdir/prompt.md')
            except FileNotFoundError as e:
                error_message = str(e)
                # Check that the path contains the expected components
                assert 'tools' in error_message
                assert 'prompts' in error_message
                assert 'subdir/prompt.md' in error_message

    @patch('pathlib.Path.exists')
    @patch('builtins.open')
    def test_load_prompt_file_read_error(self, mock_file, mock_exists):
        """Test handling of file read errors."""
        mock_exists.return_value = True
        mock_file.side_effect = IOError("Permission denied")

        with pytest.raises(IOError) as excinfo:
            load_prompt('error_prompt.md')

        assert "Permission denied" in str(excinfo.value)
        mock_exists.assert_called_once()

    @patch('pathlib.Path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data='Test prompt content')
    def test_load_prompt_different_paths(self, mock_file, mock_exists):
        """Test loading prompts from different subdirectories."""
        mock_exists.return_value = True

        # Test various path formats
        test_paths = [
            'simple.md',
            'subdir/nested.md',
            'deep/nested/path/prompt.md',
            'special-chars_123.md'
        ]

        for path in test_paths:
            result = load_prompt(path)
            assert result == 'Test prompt content'

        assert mock_exists.call_count == len(test_paths)
        assert mock_file.call_count == len(test_paths)

    @patch('pathlib.Path.__new__')
    def test_load_prompt_path_resolution(self, mock_path_class):
        """Test the path resolution logic."""
        # Create mock path instances
        mock_file_path = MagicMock()
        mock_parent1 = MagicMock()
        mock_parent2 = MagicMock()
        mock_tools_dir = MagicMock()
        mock_prompts_dir = MagicMock()
        mock_full_path = MagicMock()

        # Set up the chain of path operations
        mock_path_class.return_value = mock_file_path
        mock_file_path.parent = mock_parent1
        mock_parent1.parent = mock_parent2
        mock_parent2.__truediv__.return_value = mock_tools_dir
        mock_tools_dir.__truediv__.return_value = mock_prompts_dir
        mock_prompts_dir.__truediv__.return_value = mock_full_path

        # Configure the final path
        mock_full_path.exists.return_value = True
        mock_full_path.__str__.return_value = '/path/to/prompt.md'

        # Mock the open function
        with patch('builtins.open', mock_open(read_data='Test content')):
            result = load_prompt('test.md')

        assert result == 'Test content'

        # Verify the path construction
        mock_parent2.__truediv__.assert_called_with('tools')
        mock_tools_dir.__truediv__.assert_called_with('prompts')
        mock_prompts_dir.__truediv__.assert_called_with('test.md')
