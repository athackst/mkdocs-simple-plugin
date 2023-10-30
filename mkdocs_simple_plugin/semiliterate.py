"""Semiliterate module handles document extraction from source files."""
from io import TextIOWrapper
import os
import re

from dataclasses import dataclass

from mkdocs import utils


def _get_match(pattern: re.Pattern, line: str) -> re.Match:
    """Returns the match for the given pattern."""
    if not pattern:
        return None
    return pattern.search(line)


@dataclass
class InlineParams:
    """Inline parameters for extraction."""
    # md file=inline_params.snippet
    # These parameters should be on the same line as the start block.
    #
    # For example:
    #
    # ```
    #  /**md file="new_name.md" trim=2 content="^\s*\/\/\s?(.*)$"
    # ```
    #
    # #### Set output file name
    #
    #  Filename is relative to the folder of the file being processed.
    #
    # ```
    # file=<name>
    # ```
    filename_pattern: re.Pattern = re.compile(r"file=[\"']?(\w+.\w+)[\"']?\b")
    filename: str = None
    #
    # #### Trim the front of a line
    #
    # Useful for removing leading spaces.
    #
    # ```
    # trim=#
    # ```
    trim_pattern: re.Pattern = re.compile(r"trim=[\"']?(\d+)[\"']?\b")
    trim: int = 0
    # #### Capture content
    #
    # Regex expression to capture content, otherwise all lines are captured.
    #
    # ```
    # content=<regex>
    # ```
    content_pattern: re.Pattern = re.compile(r"content=[\"']?([^\"']*)[\"']?")
    content: str = None
    #
    # #### Stop capture
    #
    # Regex expression to indicate capture should stop.
    #
    # ```
    # stop=<regex>
    # ```
    stop_pattern: re.Pattern = re.compile(r"stop=[\"']?([^\"']*)[\"']?")
    # /md


class ExtractionPattern:
    """An ExtractionPattern for a file."""
    # md file="ExtractionPattern.snippet"
    # ##### start
    #
    # (optional) The regex pattern to indicate the start of extraction.
    #
    # Only the first mode whose `start` expression matches is activated, so at
    # most one mode of extraction can be active at any time.
    # When an extraction is active, lines from the scanned
    # file are processed into the destination file.
    #
    # !!!Note
    #       The (last) extraction mode (if any) with no `start`
    #       parameter is active starting at the first line of the scanned
    #       file; there is no way this mode can be reactivated if it stops.
    #       This convention allows for convenient "front-matter" extraction.
    #
    # ##### stop
    #
    # (optional) The regex pattern to indicate the stop of extraction.
    #
    # After the extraction has stopped, the file will continue to be searched
    # for matching patterns starting with the _next_ line of the scanned file.
    # In this way the entire file will be processed looking for start-stop
    # pairs.
    #
    # ##### replace
    #
    # The `replace` parameter allows extracted lines from a file to
    # be transformed in simple ways by regular expressions, for
    # example to strip leading comment symbols if necessary.
    #
    # The `replace` parameter is a list of substitutions to attempt.
    # Each substitution is specified either by a two-element list of a
    # regular expression and a template, or by just a regular expression.
    #
    # Once one of the
    # `replace` patterns matches, processing stops; no further expressions
    # are checked.
    #
    # <!-- todo: link to example -->
    #
    # /md

    def __init__(
            self,
            start: str = None,
            stop: str = None,
            replace: list = None):
        """Initialize an with an empty extraction pattern.

        Args:
            start (str): Start regex expression
            stop (str): Stop regex expression
            replace (list): List of (From, To) regex expressions

        """
        self.start = re.compile(start) if start else None
        self._stop_default = re.compile(stop) if stop else None
        self.stop = self._stop_default
        if not replace:
            replace = []
        self.replace = []
        for item in replace:
            if isinstance(item, str):
                self.replace.append(re.compile(item))
            else:
                self.replace.append((re.compile(item[0]), item[1]))

        self.inline = InlineParams()

    def setup(self, line: str) -> None:
        """Process input parameters."""
        setup_inline = InlineParams()

        file_match = _get_match(setup_inline.filename_pattern, line)
        if file_match and file_match.lastindex:
            setup_inline.filename = file_match[file_match.lastindex]

        trim_match = _get_match(setup_inline.trim_pattern, line)
        if trim_match and trim_match.lastindex:
            setup_inline.trim = int(trim_match[trim_match.lastindex])

        content_match = _get_match(setup_inline.content_pattern, line)
        if content_match and content_match.lastindex:
            regex_pattern = content_match[content_match.lastindex]
            setup_inline.content = re.compile(regex_pattern)

        # choose which stop option to use.
        # Order by;
        #     1. default from extraction pattern settings
        #     2. default from inline params
        self.stop = self._stop_default
        stop_match = _get_match(setup_inline.stop_pattern, line)
        if stop_match and stop_match.lastindex:
            regex_pattern = stop_match[stop_match.lastindex]
            self.stop = re.compile(regex_pattern)

        self.inline = setup_inline

    def get_filename(self) -> str:
        """Returns the filename if defined in start arguments."""
        return self.inline.filename

    def replace_line(self, line: str) -> str:
        """Apply the specified replacements to the line and return it."""
        # Process trimming
        if self.inline.trim:
            line = line[self.inline.trim:]
        # Process inline content regex
        if self.inline.content:
            match_object = _get_match(self.inline.content, line)
            if match_object.lastindex:
                return match_object[match_object.lastindex]
        # Preform replace operations
        if not self.replace:
            return line
        for item in self.replace:
            pattern = item[0] if isinstance(item, tuple) else item
            match_object = pattern.search(line)
            if match_object:
                if isinstance(item, tuple):
                    return match_object.expand(item[1])
                if match_object.lastindex:
                    return match_object[match_object.lastindex]
                return None
        # Otherwise, just return the line.
        return line


class LazyFile:
    """Create the file only if a non-empty string is written.

    Like a file object, but only ever creates the directory and opens the
    file if a non-empty string is written.
    """

    def __init__(self, directory: str, name: str):
        """Initialize with a directory and file name."""
        self.file_directory = directory
        self.file_name = name
        self.file_object = None

    def __eq__(self, other) -> bool:
        """Check equality if directory and names are the same."""
        return self.file_directory == other.file_directory \
            and self.file_name == other.file_name

    def __str__(self) -> str:
        """Return the full file path as a string."""
        return os.path.join(self.file_directory, self.file_name)

    def write(self, arg: str) -> None:
        """Create and write a string line to the file, iff not none."""
        if arg is None:
            return
        if self.file_object is None:
            filename = os.path.join(self.file_directory, self.file_name)
            os.makedirs(self.file_directory, exist_ok=True)
            self.file_object = open(filename, 'w+')

        def get_line(line: str) -> str:
            """Returns line with EOL."""
            return line if line.endswith("\n") else line + '\n'

        self.file_object.write(get_line(arg))

    def close(self) -> str:
        """Finish the file."""
        if self.file_object is not None:
            file_path = os.path.join(self.file_directory, self.file_name)
            utils.log.debug("        ... extracted %s", file_path)
            self.file_object.close()
            self.file_object = None
            return file_path
        return None


class StreamExtract:
    """Extract files to an output stream.

    Optionally filter using a list of ExtractionPatterns.
    """

    def __init__(
            self,
            input_stream: TextIOWrapper,
            output_stream: LazyFile,
            terminate: re.Pattern = None,
            patterns: ExtractionPattern = None,
            **kwargs):
        """Initialize StreamExtract with input and output streams."""
        self.input_stream = input_stream
        self.output_stream = output_stream
        self.terminate = terminate
        self.patterns = patterns

        self._default_stream = output_stream
        self._output_files = []
        self._streams = {
            output_stream.file_name: output_stream
        }

    def _try_extract_match(
            self,
            match_object: re.Match,
            emit_last: bool = True) -> bool:
        """Extracts line iff there's a match.

        Returns:
            True iff match_object exists.
        """
        if not match_object:
            return False
        if match_object.lastindex and emit_last:
            self.output_stream.write(match_object[match_object.lastindex])
        return True

    def close(self) -> list:
        """Close the file and return a list of filenames written to."""
        file = self.output_stream.close()
        if file:
            self._output_files.append(file)
        return self._output_files

    def set_output_file(self, filename: str) -> LazyFile:
        """Set the current output stream from filename and return the stream."""
        output_stream = self.output_stream
        if filename:
            # If we've opened this file before, re-use its stream.
            if filename in self._streams:
                return self.set_output_stream(self._streams[filename])
            # Otherwise, make a new one and save it to the list.
            output_stream = LazyFile(
                self.output_stream.file_directory, filename)
            self._streams[filename] = output_stream
        return self.set_output_stream(output_stream)

    def set_output_stream(self, stream: LazyFile) -> LazyFile:
        """Set the current output stream and return the stream."""
        if self.output_stream != stream:
            self.close()
            self.output_stream = stream
        return self.output_stream

    def extract(self, **kwargs) -> list:
        """Extract from file with semiliterate configuration.

        Invoke this method to perform the extraction.

        Returns:
            A list of files extracted.
        """
        active_pattern = None if self.patterns else ExtractionPattern()
        patterns = self.patterns if self.patterns else []
        for pattern in patterns:
            if not pattern.start:
                active_pattern = pattern

        for line in self.input_stream:
            # Check terminate, regardless of state:
            if self._try_extract_match(
                    _get_match(self.terminate, line), active_pattern):
                return self.close()
            # Change state if flagged to do so:
            if active_pattern is None:
                for pattern in patterns:
                    start = _get_match(pattern.start, line)
                    if start:
                        active_pattern = pattern
                        active_pattern.setup(line)
                        self.set_output_file(active_pattern.get_filename())
                        self._try_extract_match(start)
                        break
                continue
            # We are extracting. See if we should stop:
            if self._try_extract_match(_get_match(active_pattern.stop, line)):
                active_pattern = None
                self.set_output_stream(self._default_stream)
                continue
            # Extract all other lines in the normal way:
            self.extract_line(line, active_pattern)
        return self.close()

    def extract_line(self, line: str, extraction_pattern: re.Pattern) -> None:
        """Copy line to the output stream, applying specified replacements."""
        line = extraction_pattern.replace_line(line)
        self.output_stream.write(line)


class Semiliterate:
    """Extract documentation from source files using regex settings."""

    # md file="Semiliterate.snippet"
    # #### pattern
    #
    # Any file in the searched directories whose name contains this
    # required regular expression parameter will be scanned.
    #
    # #### destination
    #
    # By default, the extracted documentation will be copied to a file
    # whose name is generated by removing the (last) extension from the
    # original filename, if any, and appending `.md`. However, if this
    # parameter is specified, it will be expanded as a template using
    # the match object from matching "pattern" against the filename,
    # to produce the name of the destination file.
    #
    # #### terminate
    #
    # If specified, all extraction from the file is terminated when
    # a line containing this regexp is encountered (whether or not
    # any extraction is currently active per the parameters below).
    # The last matching group in the `terminate` expression, if any,
    # is written to the destination file; note that "start" and "stop"
    # below share that same behavior.
    #
    # #### extract
    #
    # This parameter determines what will be extracted from a scanned
    # file that matches the pattern above. Its value should be a block
    # or list of blocks of settings.
    # /md

    def __init__(
            self,
            pattern: str,
            destination: str = None,
            terminate: str = None,
            extract: list = None):
        """Initialize semiliterate with pattern from configuration.

        Args:
            pattern (str): File matching pattern.
            destination (str): Destination file pattern for extracted text.
            terminate (str): Termination pattern.
            extract (ExtractionPattern): Extraction parameters.

        """
        self.file_filter = re.compile(pattern)
        self.destination = destination
        self.terminate = (terminate is not None) and re.compile(terminate)
        self.extractions = []
        if not extract:
            extract = []
        if isinstance(extract, dict):
            # if there is only one extraction pattern, allow it to be a single
            # dict entry
            extract = [extract]
        for extract_params in extract:
            self.extractions.append(ExtractionPattern(**extract_params))

    def filename_match(self, name: str) -> str:
        """Get the filename for the match, otherwise return None.

        Args:
            name (str): The name to match with the pattern filter

        Returns:
            The output filename for 'name' or None
        """
        name_match = self.file_filter.search(name)
        if name_match:
            new_name = os.path.splitext(name)[0] + '.md'
            if self.destination:
                new_name = name_match.expand(self.destination)
            return new_name
        return None

    def try_extraction(
            self,
            from_directory: str,
            from_file: str,
            destination_directory: str,
            **kwargs) -> list:
        """Try to extract documentation from file with name.

        Args:
            from_directory (str): The source directory
            from_file (str): The source filename within directory
            destination_directory (str): The destination directory

        Returns a list of extracted files.
        """
        to_file = self.filename_match(from_file)
        if not to_file:
            return []
        from_file_path = os.path.join(from_directory, from_file)
        try:
            with open(from_file_path) as original_file:
                utils.log.debug(
                    "mkdocs-simple-plugin: Scanning %s...", from_file_path)
                extraction = StreamExtract(
                    input_stream=original_file,
                    output_stream=LazyFile(destination_directory, to_file),
                    terminate=self.terminate,
                    patterns=self.extractions,
                    **kwargs)
                return extraction.extract()
        except (UnicodeDecodeError) as error:
            utils.log.debug("mkdocs-simple-plugin: Skipped  %s", from_file_path)
            utils.log.debug(
                "mkdocs-simple-plugin: Error details: %s", str(error))
        except (OSError, IOError) as error:
            utils.log.error("mkdocs-simple-plugin: could not build %s\n %s",
                            from_file_path, str(error))
        return []
