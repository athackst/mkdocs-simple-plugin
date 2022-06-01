#!/usr/bin/env python
"""Test mkdocs_simple_plugin.semiliterate"""
import unittest
from unittest.mock import patch, mock_open, MagicMock
import os

from mkdocs_simple_plugin import semiliterate


class TestExtractionPattern(unittest.TestCase):
    """Test ExtractionPattern interface."""

    def test_default(self):
        """Test the default configuration without any additional options."""
        pattern = semiliterate.ExtractionPattern()
        # replace_line should just return the line
        self.assertEqual(pattern.replace_line("/** md "), "/** md ")
        self.assertEqual(pattern.replace_line("## Hello"), "## Hello")
        self.assertEqual(pattern.replace_line("**/"), "**/")

        # Start should return Falsy
        self.assertFalse(pattern.start)

        # Stop should return Falsy
        self.assertFalse(pattern.stop)

    def test_setup_filename(self):
        """Test in-line setup for filename."""
        pattern = semiliterate.ExtractionPattern()

        # Set filename
        pattern.setup("//md file=new_name.snippet")
        self.assertEqual(pattern.get_filename(), "new_name.snippet")

    def test_setup_trim(self):
        """Test in-line setup for trimming front."""

        pattern = semiliterate.ExtractionPattern()

        # Set trim
        pattern.setup("//md trim=2")
        line = "1234"
        self.assertEqual(pattern.replace_line(line), "34")
        line = "1"
        self.assertEqual(pattern.replace_line(line), "")

    def test_setup_content(self):
        """Test in-line setup for capturing content."""

        pattern = semiliterate.ExtractionPattern()

        # Set content
        pattern.setup("//md content='(hello)'")
        line = "hello world"
        self.assertEqual(pattern.replace_line(line), "hello")

    def test_block_comment(self):
        """Test a nominal block start/replace/end pattern."""
        pattern = semiliterate.ExtractionPattern(
            start=r'^\s*\/\*+\W?md\b',
            stop=r'^\s*\*\*/\s*$')

        # replace_line should just return the line
        self.assertEqual(pattern.replace_line("    /** md "), "    /** md ")
        self.assertEqual(pattern.replace_line("## Hello"), "## Hello")
        self.assertEqual(pattern.replace_line("    **/"), "    **/")

        # Start should return Falsy for all except the start line
        self.assertEqual(pattern.start.match("    /** md").string, "    /** md")
        self.assertFalse(pattern.start.match("## Hello"))
        self.assertFalse(pattern.start.match("    **/"))

        # Stop should return Falsy for all except the stop line
        self.assertFalse(pattern.stop.match("    /** md "))
        self.assertFalse(pattern.stop.match("    ## Hello world"))
        self.assertEqual(pattern.stop.match("    **/").string, "    **/")

    def test_line_comment(self):
        """Test replacing characters from a line."""
        pattern = semiliterate.ExtractionPattern(
            start=r'^\s*\/\/+\W?md\b',
            stop=r'^\s*\/\/\send\smd\s*$',
            replace=[r'^\s*\/\/\s?(.*\n?)$', r'^.*$'])

        # replace_line should replace // with ''
        self.assertEqual(pattern.replace_line("    // md"), "md")
        self.assertEqual(
            pattern.replace_line("  // ## Hello world"), "## Hello world")
        self.assertEqual(pattern.replace_line("    // \\md"), "\\md")
        # Should return Falsy for strings without the line comment
        self.assertFalse(pattern.replace_line(' ## Hello World'))

        # Start should return Falsy for all except the start line
        self.assertEqual(pattern.start.match("  // md").string, "  // md")
        self.assertFalse(pattern.start.match(" // ## Hello world"))
        self.assertFalse(pattern.start.match("  // \\md"))

        # Stop should return Falsy for all except the stop line
        self.assertFalse(pattern.stop.match("  // md"))
        self.assertFalse(pattern.stop.match("  // ## Hello world"))
        self.assertEqual(
            pattern.stop.match("  // end md").string, "  // end md")


class TestLazyFile(unittest.TestCase):
    """Test LazyFile interface."""

    def test_write(self):
        """Test writing to lazy file."""
        directory = "/tmp/test_semiliterate/TestLazyFile"
        file = "test_init"
        lazy_file = semiliterate.LazyFile(directory=directory, name=file)
        full_path = os.path.join(directory, file)
        self.assertEqual(str(lazy_file), full_path)
        mock = mock_open()
        with patch('mkdocs_simple_plugin.semiliterate.open',
                   mock,
                   create=True) as patched:
            self.assertIs(patched, mock)
            lazy_file.write('test line')
            lazy_file.write('second_line')
            lazy_file.close()

        mock.assert_called_once_with(full_path, 'a+')
        self.assertEqual(mock.return_value.write.call_count, 2)
        mock.return_value.close.assert_called_once()

        self.assertEqual(
            lazy_file,
            semiliterate.LazyFile(directory=directory, name=file))


class TestStreamExtract(unittest.TestCase):
    """Test extracting data to a stream."""

    def setUp(self):
        self.input_mock = MagicMock()
        self.output_mock = MagicMock()
        self.test_stream = semiliterate.StreamExtract(
            self.input_mock, self.output_mock)

    def test_transcribe(self):
        """Transcribing data should write data."""
        self.assertFalse(self.test_stream.wrote_something)

        self.test_stream.transcribe("test input")
        self.output_mock.write.assert_called_once_with("test input")
        self.assertTrue(self.test_stream.wrote_something)

    def test_transcribe_none(self):
        """Transcribing nothing should do nothing."""
        self.assertFalse(self.test_stream.wrote_something)

        self.test_stream.transcribe("")
        self.assertFalse(self.test_stream.wrote_something)

    def test_extract_match(self):
        """Test extracting from a regex match."""
        self.assertFalse(self.test_stream.wrote_something)

        self.test_stream.try_extract_match(None)
        self.assertFalse(self.test_stream.wrote_something)

        mock_value = ("test first", "test second")

        def index_func(self, value):
            return mock_value[value]
        mock_match = MagicMock(return_value=mock_value)
        mock_match.__getitem__ = index_func
        mock_match.lastindex.return_value = 1
        self.test_stream.try_extract_match(mock_match)
        self.output_mock.write.assert_called_once_with("test second\n")
        self.assertTrue(self.test_stream.wrote_something)

    def test_set_output_stream_new(self):
        """Setting the filename to a new file should create a new stream."""
        self.output_mock.file_name = "test_name"
        self.output_mock.file_directory = "/test/dir/"

        self.test_stream.set_output_stream("new_name.snippet")
        self.output_mock.close.assert_called_once()
        self.assertEqual(
            self.test_stream.output_stream.file_name, "new_name.snippet")

    def test_set_output_stream_same(self):
        """Setting the output stream to the same file should do nothing."""
        self.output_mock.file_name = "test_name"
        self.output_mock.file_directory = "/test/dir/"
        self.test_stream.set_output_stream("test_name")
        self.output_mock.close.assert_not_called()


class TestSemiliterate(unittest.TestCase):
    """Test the Semiliterate base class."""

    @patch('mkdocs_simple_plugin.semiliterate.StreamExtract')
    def test_try_extraction_default(self, mock_stream_extract):
        """Test extraction."""
        test_semiliterate = semiliterate.Semiliterate(
            pattern=r".*")
        mock_stream_extract.extract.return_value = True
        mock = mock_open()
        with patch('mkdocs_simple_plugin.semiliterate.open',
                   mock,
                   create=True) as patched:
            self.assertIs(patched, mock)
            self.assertTrue(test_semiliterate.try_extraction(
                from_directory="/test/dir",
                from_file="test_file.md",
                destination_directory="/out/dir"))
        mock.assert_called_once_with("/test/dir/test_file.md")
        assert mock_stream_extract is semiliterate.StreamExtract
        mock_stream_extract.called_once()

    @patch('mkdocs_simple_plugin.semiliterate.StreamExtract')
    def test_try_extraction_skip(self, mock_stream_extract):
        """Test skipping extraction for name mismatch with pattern filter"""
        test_semiliterate = semiliterate.Semiliterate(
            pattern=r".py")
        mock_stream_extract.extract.return_value = True
        mock = mock_open()
        with patch('mkdocs_simple_plugin.semiliterate.open',
                   mock,
                   create=True) as patched:
            self.assertIs(patched, mock)
            self.assertFalse(test_semiliterate.try_extraction(
                from_directory="/test/dir",
                from_file="test_file.md",
                destination_directory="/out/dir"))
        mock.assert_not_called()
        assert mock_stream_extract is semiliterate.StreamExtract
        mock_stream_extract.assert_not_called()


if __name__ == '__main__':
    unittest.main()
