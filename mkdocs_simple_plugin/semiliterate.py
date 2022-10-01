"""Semiliterate module handles document extraction from source files."""
import os
import re

from mkdocs import utils


def get_line(line: str) -> str:
    """Returns line with EOL."""
    if not line:
        return None
    return line if line.endswith("\n") else line + '\n'


def get_match(pattern: re.Pattern, line: str) -> re.Match:
    """Returns the match for the given pattern."""
    if not pattern:
        return None
    return pattern.search(line)


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
        self._filename_pattern = re.compile(r"file=[\"']?(\w+.\w+)[\"']?\b")
        self._filename = None
        #
        # #### Trim the front of a line
        #
        # Useful for removing leading spaces.
        #
        # ```
        # trim=#
        # ```
        self._trim_pattern = re.compile(r"trim=[\"']?(\d+)[\"']?\b")
        self._trim = 0
        # #### Capture content
        #
        # Regex expression to capture content, otherwise all lines are captured.
        #
        # ```
        # content=<regex>
        # ```
        self._content_pattern = re.compile(r"content=[\"']?([^\"']*)[\"']?")
        self._content = None
        #
        # #### Stop capture
        #
        # Regex expression to indicate capture should stop.
        #
        # ```
        # stop=<regex>
        # ```
        self._stop_pattern = re.compile(r"stop=[\"']?([^\"']*)[\"']?")
        # /md

    def setup(self, line: str):
        """Process input parameters."""
        self._filename = None
        file_match = get_match(self._filename_pattern, line)
        if file_match and file_match.lastindex:
            self._filename = file_match[file_match.lastindex]

        self._trim = 0
        trim_match = get_match(self._trim_pattern, line)
        if trim_match and trim_match.lastindex:
            self._trim = int(trim_match[trim_match.lastindex])

        self._content = None
        content_match = get_match(self._content_pattern, line)
        if content_match and content_match.lastindex:
            regex_pattern = content_match[content_match.lastindex]
            self._content = re.compile(regex_pattern)

        self.stop = self._stop_default
        stop_match = get_match(self._stop_pattern, line)
        if stop_match and stop_match.lastindex:
            regex_pattern = stop_match[stop_match.lastindex]
            self.stop = re.compile(regex_pattern)

    def get_filename(self) -> str:
        """Returns the filename if defined in start arguments."""
        return self._filename

    def replace_line(self, line: str) -> str:
        """Apply the specified replacements to the line and return it."""
        # Process trimming
        if self._trim:
            line = line[self._trim:]
        # Process inline content regex
        if self._content:
            match_object = get_match(self._content, line)
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

    def __eq__(self, other):
        """Check equality if directory and names are the same."""
        return self.file_directory == other.file_directory \
            and self.file_name == other.file_name

    def __str__(self):
        """Return the full file path as a string."""
        return os.path.join(self.file_directory, self.file_name)

    def write(self, arg: str):
        """Create and write the file, only if not empty."""
        if not arg:
            return
        if self.file_object is None:
            os.makedirs(self.file_directory, exist_ok=True)
            self.file_object = open(
                os.path.join(
                    self.file_directory,
                    self.file_name),
                'a+')
        self.file_object.write(arg)

    def close(self):
        """Finish the file."""
        if self.file_object is not None:
            utils.log.info(
                "        ... extracted %s",
                os.path.join(
                    self.file_directory,
                    self.file_name))
            self.file_object.close()
            self.file_object = None


class StreamExtract:
    """Extract documentation portions of files to an output stream."""

    def __init__(
            self,
            input_stream: LazyFile,
            output_stream: LazyFile,
            terminate: re.Pattern = None,
            patterns: ExtractionPattern = None,
            **kwargs):
        """Initialize StreamExtract with input and output streams."""
        self.input_stream = input_stream
        self.default_stream = output_stream
        self.output_stream = output_stream
        self.terminate = terminate
        self.patterns = patterns
        self.wrote_something = False

    def transcribe(self, text: str):
        """Write some text and record if something was written."""
        self.output_stream.write(text)
        if text:
            self.wrote_something = True

    def try_extract_match(
            self,
            match_object: re.Match,
            emit_last: bool = True) -> bool:
        """Extract match into output.

        If _match_object_ is not false-y, returns true.
        If extract flag is true, emits the last group of the match if any.
        """
        if not match_object:
            return False
        if match_object.lastindex and emit_last:
            self.transcribe(get_line(match_object[match_object.lastindex]))
        return True

    def close(self) -> bool:
        """Returns true if something was written"""
        self.output_stream.close()
        return self.wrote_something

    def set_output_file(self, filename: str):
        """Set output stream from filename."""
        output_stream = self.output_stream
        if filename:
            output_stream = LazyFile(
                self.output_stream.file_directory, filename)
        self.set_output_stream(output_stream)

    def set_output_stream(self, stream: LazyFile):
        """Set the output stream."""
        if self.output_stream != stream:
            self.close()
            self.output_stream = stream

    def extract(self, **kwargs) -> bool:
        """Extract from file with semiliterate configuration.

        Invoke this method to perform the extraction. Returns true if
        any text is actually extracted, false otherwise.
        """
        active_pattern = None if self.patterns else ExtractionPattern()
        for pattern in self.patterns:
            if not pattern.start:
                active_pattern = pattern

        for line in self.input_stream:
            # Check terminate, regardless of state:
            if self.try_extract_match(
                    get_match(self.terminate, line), active_pattern):
                return self.close()
            # Change state if flagged to do so:
            if active_pattern is None:
                for pattern in self.patterns:
                    start = get_match(pattern.start, line)
                    if start:
                        active_pattern = pattern
                        active_pattern.setup(line)
                        self.set_output_file(active_pattern.get_filename())
                        self.try_extract_match(start)
                        break
                continue
            # We are extracting. See if we should stop:
            if self.try_extract_match(get_match(active_pattern.stop, line)):
                active_pattern = None
                self.set_output_stream(self.default_stream)
                continue
            # Extract all other lines in the normal way:
            self.extract_line(line, active_pattern)
        return self.close()

    def extract_line(self, line: str, extraction_pattern: re.Pattern):
        """Copy line to the output stream, applying specified replacements."""
        line = get_line(extraction_pattern.replace_line(line))
        self.transcribe(line)


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
        self.patterns = []
        if not extract:
            extract = []
        if isinstance(extract, dict):
            # if there is only one extraction pattern, allow it to be a single
            # dict entry
            extract = [extract]
        for pattern in extract:
            self.patterns.append(ExtractionPattern(**pattern))

    def filename_match(self, name: str) -> str:
        """Get the filename for the match, otherwise return None."""
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
            **kwargs) -> bool:
        """Try to extract documentation from file with name.

        Returns True if extraction was successful.
        """
        to_file = self.filename_match(from_file)
        if not to_file:
            return False
        from_file_path = os.path.join(from_directory, from_file)
        try:
            with open(from_file_path) as original_file:
                utils.log.debug(
                    "mkdocs-simple-plugin: Scanning %s...", from_file)
                extraction = StreamExtract(
                    input_stream=original_file,
                    output_stream=LazyFile(destination_directory, to_file),
                    terminate=self.terminate,
                    patterns=self.patterns,
                    **kwargs)
                return extraction.extract()
        except (UnicodeDecodeError) as error:
            utils.log.info("mkdocs-simple-plugin: skipping  %s\n %s",
                           from_file_path, str(error))
        except (OSError, IOError) as error:
            utils.log.error("mkdocs-simple-plugin: could not build %s\n %s",
                            from_file_path, str(error))
        return False
