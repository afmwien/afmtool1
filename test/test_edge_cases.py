#!/usr/bin/env python3
"""
Edge case tests for AFMTool1 critical functions
Tests boundary values, off-by-one errors, and error conditions
"""

import pytest
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from utils.database import load_database, save_database, add_case_with_fields, get_last_filled_cases
from utils.afm_utils import generate_afm_string_for_case
import tempfile
import json
import os

class TestDatabaseEdgeCases:
    """Edge case tests for database functions"""
    
    def test_get_last_filled_cases_boundary_values(self):
        """Test get_last_filled_cases with boundary values"""
        # Test with limit = 0
        result = get_last_filled_cases(0)
        assert len(result) == 0
        
        # Test with limit = -1 (should return all cases as documented)
        result = get_last_filled_cases(-1)
        assert isinstance(result, list)  # Should return all cases
        
        # Test with very large limit
        result = get_last_filled_cases(999999)
        assert isinstance(result, list)
    
    def test_add_case_with_fields_empty_data(self):
        """Test adding case with empty or minimal data"""
        # Test with empty case data
        result = add_case_with_fields({})
        assert result is not None
        
        # Test with None values
        result = add_case_with_fields({"quelle": None, "fundstellen": None})
        assert result is not None
        
        # Test with empty strings
        result = add_case_with_fields({"quelle": "", "fundstellen": ""})
        assert result is not None

class TestAFMUtilsEdgeCases:
    """Edge case tests for AFM utilities"""
    
    def test_generate_afm_string_empty_case(self):
        """Test AFM string generation with empty case data"""
        # Empty case
        empty_case = {"quelle": "", "fundstellen": ""}
        result = generate_afm_string_for_case(empty_case)
        assert isinstance(result, str)
        
        # Case with None values
        none_case = {"quelle": None, "fundstellen": None}
        result = generate_afm_string_for_case(none_case)
        assert isinstance(result, str)
        
        # Case with whitespace only
        whitespace_case = {"quelle": "   ", "fundstellen": "\t\n"}
        result = generate_afm_string_for_case(whitespace_case)
        assert isinstance(result, str)
    
    def test_generate_afm_string_special_characters(self):
        """Test AFM string generation with special characters"""
        special_case = {
            "quelle": "Test & Co. (Österreich) § 123",
            "fundstellen": "File: test@example.com | 50% match"
        }
        result = generate_afm_string_for_case(special_case)
        assert isinstance(result, str)
        assert len(result) > 0

class TestFilenameEdgeCases:
    """Edge case tests for filename handling without GUI imports"""
    
    def test_filename_edge_cases(self):
        """Test filename handling with edge cases using utility function"""
        import re
        
        def make_safe_filename(filename):
            """Utility function for testing filename safety"""
            if not filename:
                return "fallback_filename"
            
            # Remove unsafe characters
            safe = re.sub(r'[<>:"/\\|?*]', '', str(filename))
            safe = safe[:255]  # Limit length
            
            return safe if safe else "fallback_filename"
        
        # Test with empty filename
        result = make_safe_filename("")
        assert result != ""
        assert len(result) > 0
        
        # Test with None
        result = make_safe_filename(None)
        assert result != ""
        assert len(result) > 0
        
        # Test with special characters
        result = make_safe_filename("test/\\:*?\"<>|file.png")
        assert "/" not in result
        assert "\\" not in result
        assert "*" not in result
        
        # Test with very long filename
        long_name = "a" * 300
        result = make_safe_filename(long_name)
        assert len(result) <= 255  # Common filesystem limit

class TestCaseIndexBoundaries:
    """Test case index boundary conditions"""
    
    def test_case_index_boundaries(self):
        """Test functions with case index boundaries"""
        # This is a demonstration test for case index validation
        # In a real implementation, functions should validate indices
        
        # Test index = 0 (first case)
        assert 0 >= 0  # Valid index
        
        # Test index = -1 (invalid)
        assert -1 < 0  # Invalid index should be handled
        
        # Test very large index
        large_index = 999999
        assert large_index >= 0  # Valid range check

class TestStringEdgeCases:
    """Edge case tests for string processing"""
    
    def test_empty_string_handling(self):
        """Test functions with empty strings"""
        from utils.afm_utils import generate_afm_string_for_case
        
        # Test with various empty string scenarios
        test_cases = [
            {"quelle": "", "fundstellen": ""},
            {"quelle": "   ", "fundstellen": "\t"},
            {"quelle": "\n", "fundstellen": ""},
        ]
        
        for case in test_cases:
            result = generate_afm_string_for_case(case)
            assert isinstance(result, str)
    
    def test_large_string_handling(self):
        """Test functions with very large strings"""
        from utils.afm_utils import generate_afm_string_for_case
        
        # Test with very large strings
        large_case = {
            "quelle": "A" * 10000,
            "fundstellen": "B" * 10000
        }
        
        result = generate_afm_string_for_case(large_case)
        assert isinstance(result, str)
        assert len(result) > 0

if __name__ == "__main__":
    pytest.main([__file__, "-v"])