#!/usr/bin/env python
"""Test mkdocs_simple_plugin.semiliterate"""
import unittest
from unittest.mock import MagicMock
import os
import re
from io import TextIOWrapper

from pyfakefs import fake_filesystem_unittest

from mkdocs_simple_plugin.semiliterate import (
    ExtractionPattern,
    LazyFile,
    Semiliterate,
    StreamExtract,
)


class FakeFsTestCase(fake_filesystem_unittest.TestCase):
    """Custom common helper test functions."""

    # pylint: disable=invalid-name
    def assertContentsIn(self, path, contents):
        """Assert that a file path contains contents"""
        # Read the content of the fake file
        with open(path, "r") as file:
            file_content = file.read()

        # Assert that the file contains a specific string
        self.assertIn(contents, file_content)

    # pylint: disable=invalid-name
    def assertContentsEqual(self, path, expected_contents):
        """Assert that the file matches the expected contents"""
        with open(path, "r") as file:
            file_contents = file.read().splitlines()
        self.assertEqual(
            file_contents,
            expected_contents,
            f"File at {path} does not contain the expected contents.")


class TestExtractionPattern(unittest.TestCase):
    """Test ExtractionPattern interface."""

    def test_default(self):
        """Test the default configuration without any additional options."""
        pattern = ExtractionPattern()
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
        pattern = ExtractionPattern()
        # Set filename
        pattern.setup("//md file=new_name.snippet")
        self.assertEqual(pattern.get_filename(), "new_name.snippet")

    def test_setup_trim(self):
        """Test in-line setup for trimming front."""
        pattern = ExtractionPattern()
        # Set trim
        pattern.setup("//md trim=2")
        self.assertEqual(pattern.replace_line("1234"), "34")
        self.assertEqual(pattern.replace_line("1"), "")

    def test_setup_content(self):
        """Test in-line setup for capturing content."""
        pattern = ExtractionPattern()
        # Set content
        pattern.setup("//md content='(hello)'")
        self.assertEqual(pattern.replace_line("hello world"), "hello")

    def test_setup_stop(self):
        """Test in-line setup for stopping capture."""
        pattern = ExtractionPattern()
        # Set stop
        pattern.setup("//md stop='.*(world)'")
        stop_pattern = re.compile(".*(world)")
        self.assertEqual(stop_pattern, pattern.stop)

    def test_block_comment(self):
        """Test a nominal block start/replace/end pattern."""
        pattern = ExtractionPattern(
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
        pattern = ExtractionPattern(
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


class TestLazyFile(FakeFsTestCase):
    """Test LazyFile interface."""

    def setUp(self):
        """Set up fake filesystem."""
        self.setUpPyfakefs()
        self.directory = "/tmp/test_semiliterate/TestLazyFile"
        self.file = "test_init"
        self.full_path = os.path.join(self.directory, self.file)
        self.fs.create_file(self.full_path)

    def test_write(self):
        """Test writing to lazy file."""
        lazy_file = LazyFile(directory=self.directory, name=self.file)
        lazy_file.write('test line')
        lazy_file.write('second_line')
        output = lazy_file.close()
        self.assertEqual(output, self.full_path)
        self.assertContentsEqual(self.full_path, ['test line', 'second_line'])

    def test_write_none(self):
        """Test that writing none results in none."""
        lazy_file = LazyFile(directory=self.directory, name=self.file)
        lazy_file.write(None)
        output = lazy_file.close()
        self.assertIsNone(output)

    def test_write_empty(self):
        """Test that writing an empty string results in empty line."""
        lazy_file = LazyFile(directory=self.directory, name=self.file)
        lazy_file.write('')
        output = lazy_file.close()
        self.assertEqual(output, self.full_path)
        self.assertContentsEqual(self.full_path, [''])

    def test_same_path_should_be_equal(self):
        """Test that two LazyFiles are equal if they have the same path."""
        lazy_file = LazyFile(directory=self.directory, name=self.file)
        self.assertEqual(
            lazy_file,
            LazyFile(directory=self.directory, name=self.file))


class TestStreamExtract(FakeFsTestCase):
    """Test extracting data to a stream."""

    def setUp(self):
        """Set up the mock for input, output, and stream."""
        self.setUpPyfakefs()
        self.input_stream = MagicMock(spec=TextIOWrapper)
        self.output_dir = "test"
        self.output_filename = "output.md"
        self.output_path = os.path.join(self.output_dir, self.output_filename)
        self.output_stream = LazyFile(
            directory=self.output_dir,
            name=self.output_filename)
        self.output_stream.file_name = "output.md"
        self.stream_extract = StreamExtract(
            input_stream=self.input_stream, output_stream=self.output_stream)

    def test_set_output_file_with_filename(self):
        """Should set output file by filename."""
        filename = "test_output.md"
        file = self.stream_extract.set_output_file(filename)
        # It returns the stream
        self.assertEqual(file, self.stream_extract.output_stream)
        # It is the right type
        self.assertIsInstance(file, LazyFile)
        # It saved the filename
        self.assertEqual(file.file_name, filename)

    def test_set_output_file_with_empty_filename(self):
        """Empty file should not change output stream."""
        original = self.stream_extract.output_stream
        self.stream_extract.set_output_file("")
        self.assertEqual(
            self.stream_extract.output_stream, original)

    def test_set_output_stream(self):
        """Should set output stream from a new LazyFile."""
        new_output_stream = LazyFile(directory="new", name="test.md")
        self.stream_extract.set_output_stream(new_output_stream)
        self.assertEqual(self.stream_extract.output_stream, new_output_stream)

    def test_close_multiple_files(self):
        """Setting the filename to a new file should create a new stream."""
        self.output_stream.write("test output 1")

        test_filename = "new_name.snippet"
        test_path = os.path.join(self.output_dir, test_filename)
        new_stream = self.stream_extract.set_output_file(test_filename)
        new_stream.write("test output 2")

        files = self.stream_extract.close()

        self.assertEqual(
            self.stream_extract.output_stream.file_name, test_filename)
        self.assertEqual(len(files), 2)
        self.assertIn(self.output_path, files, str(files))
        self.assertIn(test_path, files, str(files))

    def test_close_same_file(self):
        """Setting the output stream to the same file should do nothing."""
        self.output_stream.write("test output 1")

        # Try setting same file
        new_stream = self.stream_extract.set_output_file(self.output_filename)
        new_stream.write("test output 2")

        files = self.stream_extract.close()

        self.assertEqual(
            self.stream_extract.output_stream.file_name, self.output_filename)
        self.assertEqual(len(files), 1)

    def test_extract(self):
        """Test extraction"""
        self.stream_extract.patterns = [
            ExtractionPattern(start=r'START', stop=r'STOP')
        ]
        lines = ['Line 1', 'START', 'Extracted Text', 'STOP', 'Line 2']

        # Set up mock behavior for input_stream
        input_stream_iterator = iter(lines)
        self.input_stream.__iter__.return_value = input_stream_iterator

        # Perform the extraction
        output_files = self.stream_extract.extract()

        # Assertions
        self.assertEqual(len(output_files), 1)
        # extracted text between start and stop
        self.assertContentsEqual(self.output_path, ['Extracted Text'])

    def test_extract_no_patterns(self):
        """Extraction without patterns should extract the whole file."""
        lines = ['Line 1', 'Line 2', 'Line 3']
        input_stream_iterator = iter(lines)
        self.input_stream.__iter__.return_value = input_stream_iterator
        output_files = self.stream_extract.extract()

        # one file extracted
        self.assertEqual(len(output_files), 1)
        # each line extracted
        self.assertContentsEqual(self.output_path, lines)

    def test_extract_pattern_without_start(self):
        """Extraction without the start attribute should extract until stop."""
        self.stream_extract.patterns = [ExtractionPattern(stop=r'STOP')]
        lines = ['Line 1', 'START', 'STOP', 'Line 2']
        input_stream_iterator = iter(lines)
        self.input_stream.__iter__.return_value = input_stream_iterator
        output_files = self.stream_extract.extract()

        # one file extracted
        self.assertEqual(len(output_files), 1)
        # lines extracted until stop
        self.assertContentsEqual(self.output_path, ['Line 1', 'START'])

    def test_extract_multiple_patterns(self):
        """Test extraction with multiple patterns."""
        self.stream_extract.patterns = [
            ExtractionPattern(start=r'START1', stop=r'STOP1'),
            ExtractionPattern(start=r'START2', stop=r'STOP2')
        ]
        lines = [
            'Line 1',
            'START1',
            'Content 1',
            'STOP1',
            'START2',
            'Content 2',
            'STOP2',
            'Line 2']
        input_stream_iterator = iter(lines)
        self.input_stream.__iter__.return_value = input_stream_iterator
        output_files = self.stream_extract.extract()

        # one file extracted
        self.assertEqual(len(output_files), 1)
        # lines between start and stop extracted
        self.assertContentsEqual(self.output_path, ['Content 1', 'Content 2'])

    def test_extract_empty_lines(self):
        """Test extraction with empty lines in the input."""
        self.stream_extract.patterns = [
            ExtractionPattern(
                start=r'START',
                stop=r'STOP')]
        lines = ['Line 1', '', 'START', '', 'Content', 'STOP', 'Line 2']
        input_stream_iterator = iter(lines)
        self.input_stream.__iter__.return_value = input_stream_iterator
        output_files = self.stream_extract.extract()

        # one file extracted
        self.assertEqual(len(output_files), 1)
        # empty line extracted
        self.assertContentsEqual(self.output_path, ['', 'Content'])

    def test_extract_pattern_at_stop(self):
        """Test extraction with a pattern matching at the end of input."""
        self.stream_extract.patterns = [
            ExtractionPattern(
                start=r'START',
                stop=r'STOP(.*)$')]
        lines = ['Line 1', 'START', 'Content', 'STOP:Capture end']
        input_stream_iterator = iter(lines)
        self.input_stream.__iter__.return_value = input_stream_iterator
        output_files = self.stream_extract.extract()

        # one file extracted
        self.assertEqual(len(output_files), 1)
        # Lines and stop pattern extracted
        self.assertContentsEqual(self.output_path, ['Content', ':Capture end'])

    def test_extract_pattern_at_start(self):
        """Test extraction with a pattern matching at the end of input."""
        self.stream_extract.patterns = [
            ExtractionPattern(
                start=r'START(.*)$',
                stop=r'STOP')]
        lines = ['Line 1', 'START:Capture start', 'Content', 'STOP:Capture end']
        input_stream_iterator = iter(lines)
        self.input_stream.__iter__.return_value = input_stream_iterator
        output_files = self.stream_extract.extract()

        # one file extracted
        self.assertEqual(len(output_files), 1)
        # Start pattern extracted plus content
        self.assertContentsEqual(
            self.output_path,
            [':Capture start', 'Content'])


class TestSemiliterate(FakeFsTestCase):
    """Test the Semiliterate base class."""

    def setUp(self):
        """Set up fake filesystem."""
        self.setUpPyfakefs()

    def test_filename_match_with_match(self):
        """Filename match with txt should match example.txt."""
        test_semiliterate = Semiliterate(pattern=r'.*\.txt')
        match = test_semiliterate.filename_match('example.txt')
        self.assertEqual(match, 'example.md')

    def test_filename_match_without_match(self):
        """Filename match with txt should not match example.jpg."""
        test_semiliterate = Semiliterate(pattern=r'.*\.txt')
        match = test_semiliterate.filename_match('example.jpg')
        self.assertIsNone(match)

    def test_filename_match_with_destination(self):
        """Test filename matching with a destination pattern."""
        test_semiliterate = Semiliterate(pattern=r'(.*)\.txt')
        test_semiliterate.destination = r'\1_output.md'
        name = "example.txt"
        result = test_semiliterate.filename_match(name)
        self.assertEqual(result, "example_output.md")

    def test_try_extraction_successful(self):
        """Test extraction of a txt file to an md file should succeed."""
        test_semiliterate = Semiliterate(pattern=r'.*\.txt')
        directory = "/source"
        filename = "example.txt"
        path = os.path.join(directory, filename)
        output = "/output"
        expected_output_path = "/output/example.md"
        self.fs.create_file(path, contents="Sample content")

        result = test_semiliterate.try_extraction(
            from_directory=directory,
            from_file=filename,
            destination_directory=output
        )
        self.assertTrue(result)  # Extraction failed
        self.assertListEqual(result, [expected_output_path])
        self.assertTrue(self.fs.exists(expected_output_path))

    def test_try_extraction_no_match(self):
        """Test extraction of a non matching file to an md file should fail."""
        test_semiliterate = Semiliterate(pattern=r'.*\.txt')
        directory = "/source"
        filename = "example.py"
        path = os.path.join(directory, filename)
        output = "/output"
        self.fs.create_file(path, contents="Sample content")

        result = test_semiliterate.try_extraction(
            from_directory=directory,
            from_file=filename,
            destination_directory=output
        )
        self.assertFalse(result)  # Extraction failed
        self.assertListEqual(result, [])

    def test_try_extraction_io_error(self):
        """Test extraction of a non existent file should fail."""
        semiliterate = Semiliterate(pattern=r'.*\.txt')
        result = semiliterate.try_extraction(
            from_directory='/source',
            from_file='nonexistent.txt',
            destination_directory='/output'
        )
        self.assertFalse(result)  # Extraction failed
        self.assertListEqual(result, [])

    def test_unicode_filenames_and_content(self):
        """Test behavior with non-ASCII filenames and content."""
        test_semiliterate = Semiliterate(pattern=r'.*\.txt')
        directory = "/source"
        filename = "mön.txt"  # Non-ASCII filename
        path = os.path.join(directory, filename)
        output = "/output"
        expected_output_path = "/output/mön.md"  # Expected output filename

        # Create and write content with non-ASCII characters
        content = 'Non-ASCII content: mön\n'
        self.fs.create_file(path, contents=content)

        result = test_semiliterate.try_extraction(
            from_directory=directory,
            from_file=filename,
            destination_directory=output
        )
        self.assertTrue(result)  # Extraction successful
        self.assertListEqual(result, [expected_output_path])
        self.assertTrue(self.fs.exists(expected_output_path))

    def test_large_input_file(self):
        """Test behavior with a large input file."""
        test_semiliterate = Semiliterate(pattern=r'.*\.txt')
        directory = "/source"
        filename = "large.txt"
        path = os.path.join(directory, filename)
        output = "/output"
        expected_output_path = "/output/large.md"  # Expected output filename

        # Create a large content string (simulate a large file)
        large_content = 'A' * 10_000_000  # 10 MB content
        self.fs.create_file(path, contents=large_content)

        result = test_semiliterate.try_extraction(
            from_directory=directory,
            from_file=filename,
            destination_directory=output
        )
        self.assertTrue(result)  # Extraction successful
        self.assertListEqual(result, [expected_output_path])
        self.assertTrue(self.fs.exists(expected_output_path))

    def test_extract_with_custom_termination_pattern(self):
        """Test extraction with a custom termination pattern."""
        test_semiliterate = Semiliterate(
            pattern=r'.*\.txt',
            terminate=r'^END'  # Custom termination pattern
        )
        directory = "/source"
        filename = "custom_termination.txt"
        path = os.path.join(directory, filename)
        output = "/output"
        expected_output_path = "/output/custom_termination.md"

        # Create content with the custom termination pattern
        content = 'Content before END\nEND\nContent after END'
        self.fs.create_file(path, contents=content)

        result = test_semiliterate.try_extraction(
            from_directory=directory,
            from_file=filename,
            destination_directory=output
        )
        self.assertTrue(result)  # Extraction successful
        self.assertListEqual(result, [expected_output_path])
        self.assertTrue(self.fs.exists(expected_output_path))

    def test_extract_with_multiple_extraction_patterns(self):
        """Test extraction with multiple extraction patterns."""
        test_semiliterate = Semiliterate(
            pattern=r'.*\.txt',
            extract=[
                {
                    "start": r'^START',
                    "stop": r'^STOP'
                },
                {
                    "start": r'^BEGIN',
                    "stop": r'^END'
                }
            ]
        )
        directory = "/source"
        filename = "multiple_patterns.txt"
        path = os.path.join(directory, filename)
        output = "/output"
        expected_output_path = "/output/multiple_patterns.md"

        # Create content with multiple extraction patterns
        content = 'Content before START\nSTART\nExtracted Text 1\nSTOP\n' \
            'Content between BEGIN and END\nBEGIN\nExtracted Text 2\nEND'
        self.fs.create_file(path, contents=content)

        result = test_semiliterate.try_extraction(
            from_directory=directory,
            from_file=filename,
            destination_directory=output
        )
        self.assertTrue(result)  # Extraction successful
        self.assertListEqual(result, [expected_output_path])
        self.assertTrue(self.fs.exists(expected_output_path))

    def test_extract_with_destination_template(self):
        """Test extraction with a destination template."""
        test_semiliterate = Semiliterate(
            pattern=r'(.*)\.txt',
            destination=r'\1_output.md'  # Destination template
        )
        directory = "/source"
        filename = "template.txt"
        path = os.path.join(directory, filename)
        output = "/output"
        expected_output_path = "/output/template_output.md"

        # Create content
        content = 'Sample content'
        self.fs.create_file(path, contents=content)

        result = test_semiliterate.try_extraction(
            from_directory=directory,
            from_file=filename,
            destination_directory=output
        )
        self.assertTrue(result)  # Extraction successful
        self.assertListEqual(result, [expected_output_path])
        self.assertTrue(self.fs.exists(expected_output_path))


if __name__ == '__main__':
    unittest.main()
