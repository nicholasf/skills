import pytest
from tools.read_file import read_file


def test_read_file_existing_file(set_working_directory):
    """Test that reading an existing file returns its content."""
    tmp_path = set_working_directory
    test_file = tmp_path / "test.txt"
    test_file.write_text("Hello, World!")
    
    result = read_file.invoke({"path": "test.txt"})
    assert result == "Hello, World!"


def test_read_file_missing_file(set_working_directory):
    """Test that reading a missing file returns a string starting with 'Error'."""
    tmp_path = set_working_directory
    
    result = read_file.invoke({"path": "nonexistent.txt"})
    assert result.startswith("Error reading")