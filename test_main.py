import unittest
from unittest.mock import patch, mock_open, MagicMock
import os
import json
import sys

# Import functions from our main program
import main

class TestPortfolioGenerator(unittest.TestCase):
    
    @patch('builtins.print')
    def test_1_missing_resume(self, mock_print):
        """Test Case: Missing resume.txt -> Show clear error and stop safely."""
        with self.assertRaises(SystemExit) as cm:
            main.read_resume("does_not_exist.txt")
        self.assertEqual(cm.exception.code, 1)
        mock_print.assert_called_with("Error: Could not find 'does_not_exist.txt'. Please create this file and add your resume text.")

    @patch('builtins.print')
    def test_2_empty_resume(self, mock_print):
        """Test Case: Empty or very short resume -> Reject input with useful message."""
        # Test completely empty file
        with patch('builtins.open', mock_open(read_data="   ")):
            with patch('os.path.exists', return_value=True):
                with self.assertRaises(SystemExit) as cm:
                    main.read_resume("empty.txt")
                self.assertEqual(cm.exception.code, 1)
                mock_print.assert_called_with("Error: The file 'empty.txt' is empty.")
                
        # Test very short file
        with patch('builtins.open', mock_open(read_data="Too short to be a valid resume text")):
            with patch('os.path.exists', return_value=True):
                with self.assertRaises(SystemExit) as cm:
                    main.read_resume("short.txt")
                self.assertEqual(cm.exception.code, 1)
                mock_print.assert_called_with("Error: The file 'short.txt' is too short to be a valid resume.")
                
    @patch('os.path.exists', return_value=True)
    def test_3_valid_resume_reading(self, mock_exists):
        """Test Case: Valid resume -> Should read and clean text correctly."""
        valid_text = "This is a valid resume text that exceeds the fifty character minimum requirement for the application to proceed."
        with patch('builtins.open', mock_open(read_data=valid_text)):
            result = main.read_resume("valid.txt")
            self.assertEqual(result, valid_text.strip())

    @patch('builtins.print')
    @patch('os.getenv', return_value="")
    def test_4_missing_api_key(self, mock_getenv, mock_print):
        """Test Case: Missing API key -> Show a configuration error."""
        with self.assertRaises(SystemExit) as cm:
            main.load_environment()
        self.assertEqual(cm.exception.code, 1)
        mock_print.assert_called_with("Error: GEMINI_API_KEY not found or not set in .env file.")
        
    @patch('builtins.print')
    def test_5_api_failure(self, mock_print):
        """Test Case: API failure -> Handle the failure without crashing."""
        main.client = MagicMock()
        # Simulate network or API error
        main.client.models.generate_content.side_effect = Exception("503 Service Unavailable")
        with self.assertRaises(SystemExit) as cm:
            main.extract_json_with_gemini("Valid resume text")
        self.assertEqual(cm.exception.code, 1)
        mock_print.assert_called_with("Error communicating with Gemini API: 503 Service Unavailable")

    @patch('builtins.print')
    def test_6_invalid_json(self, mock_print):
        """Test Case: Invalid JSON response -> Show a clear error and stop safely."""
        invalid_json = "{ name: 'Missing quotes around keys', this_is_invalid: true }"
        with self.assertRaises(SystemExit) as cm:
            main.parse_json(invalid_json)
        self.assertEqual(cm.exception.code, 1)
        
        # Verify the custom error message was printed
        printed_messages = [call.args[0] for call in mock_print.call_args_list]
        self.assertTrue(any("Failed to parse JSON" in msg for msg in printed_messages))

    @patch('builtins.open', new_callable=mock_open)
    @patch('os.path.exists', return_value=True)
    @patch('builtins.print')
    def test_7_html_generation_with_missing_sections(self, mock_print, mock_exists, mock_file):
        """Test Case: Resume with missing sections -> Generate available sections without inventing information."""
        
        # We simulate the template.html reading process
        mock_file.return_value.read.return_value = "<html><body><h1>{NAME}</h1>{SKILLS_SECTION}{EXPERIENCE_SECTION}</body></html>"
        
        # Data reflecting missing information (e.g. empty skills or experience lists)
        test_data = {
            "Name": "Jane Doe",
            "Headline": "Software Engineer",
            "Skills": [],         # Emulating a section completely missing in resume
            "Experience": []      # Emulating a section completely missing in resume
        }
        
        # Call generate_html
        main.generate_html(test_data, "template.html", "output.html")
        
        # Check what was written to output.html. 
        # The empty sections should have been replaced with "" rather than keeping the placeholder or crashing.
        mock_file.assert_called_with('output.html', 'w', encoding='utf-8')
        handle = mock_file()
        handle.write.assert_called_with("<html><body><h1>Jane Doe</h1></body></html>")

if __name__ == '__main__':
    unittest.main()
