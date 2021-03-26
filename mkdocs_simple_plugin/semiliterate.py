"""Semiliterate module handles document extraction from source files."""
import os
import re

from mkdocs import utils


def get_line(line):
    """Returns line with EOL."""
    return line if line.endswith("\n") else line + '\n'


class LazyFile:
    """Create the file only if a non-empty string is written.

    Like a file object, but only ever creates the directory and opens the
    file if a non-empty string is written.
    """

    def __init__(self, directory, name):
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

    def write(self, arg):
        """Create and write the file, only if not empty."""
        if arg == '':
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
            self.file_object.close()
            self.file_object = None


class StreamExtract:
    """Extract documentation portions of files to an output stream."""

    def __init__(
            self,
            input_stream,
            output_stream,
            terminate=None,
            patterns=None,
            **kwargs):
        """Initialze StreamExtract with input and output streams."""
        self.input_stream = input_stream
        self.default_stream = output_stream
        self.output_stream = output_stream
        self.output_pattern = re.compile(r"file=[\"']?(\w+.\w+)[\"']?\b")
        self.terminate = terminate
        self.patterns = patterns
        self.wrote_something = False

    def transcribe(self, text):
        """Write some text and record if something was written."""
        self.output_stream.write(text)
        if text:
            self.wrote_something = True

    def check_pattern(self, pattern, line, emit_last=True):
        """Check if pattern is contained in line.

        If _pattern_ is not false-y and is contained in _line_,
        returns true (and if the _emit_last_ flag is true,
        emits the last group of the match if any). Otherwise,
        check_pattern does nothing but return false.
        """
        if not pattern:
            return False
        match_object = pattern.search(line)
        if not match_object:
            return False
        if match_object.lastindex and emit_last:
            self.transcribe(get_line(match_object[match_object.lastindex]))
        return True

    def close(self):
        """Returns true if something was written"""
        if self.wrote_something:
            utils.log.debug(
                "        ... extracted {}".format(
                    os.path.join(
                        self.output_stream.file_directory,
                        self.output_stream.file_name)))
        self.output_stream.close()
        return self.wrote_something

    def set_output_stream(self, line):
        """Set output stream from pattern match."""
        match_object = self.output_pattern.search(line)
        if not match_object:
            return
        output_stream = self.output_stream
        if match_object:
            output_stream = LazyFile(
                self.output_stream.file_directory,
                match_object[1])

        if self.output_stream != output_stream:
            self.close()
            self.output_stream = output_stream

    def extract(self, **kwargs):
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
            if self.check_pattern(self.terminate, line, active_pattern):
                return self.close()
            # Change state if flagged to do so:
            if active_pattern is None:
                for pattern in self.patterns:
                    if self.check_pattern(pattern.start, line):
                        active_pattern = pattern
                        self.set_output_stream(line)
                        break
                continue
            # We are extracting. See if we should stop:
            if self.check_pattern(active_pattern.stop, line):
                active_pattern = None
                self.output_stream = self.default_stream
                continue
            # Extract all other lines in the normal way:
            self.extract_line(line, active_pattern)
        return self.close()

    def extract_line(self, line, extraction_pattern):
        """Copy line to the output stream, applying specified replacements."""
        line = extraction_pattern.replace_line(line)
        self.transcribe(line)


class Semiliterate:
    """Extract documentation from source files using regex settings."""

    # md file="semiliterate.snippet"
    #
    # #### pattern
    # Any file in the searched directories whose name contains this
    # required regular expression parameter will be scanned.
    #
    # #### destination
    # By default, the extracted documentation will be copied to a file
    # whose name is generated by removing the (last) extension from the
    # original filename, if any, and appending `.md`. However, if this
    # parameter is specified, it will be expanded as a template using
    # the match object from matching "pattern" against the filename,
    # to produce the name of the destination file.
    #
    # #### terminate
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
            pattern,
            destination=None,
            terminate=None,
            extract=[]):
        """Initialize semiliterate with pattern from configuration.

        Args:
            pattern (str): File matching pattern.
            destination (str): Desitnation file pattern for extracted text.
            terminate (str): Termination pattern.
            extract (ExtractionPattern): Extraction parameters.

        """
        self.file_filter = re.compile(pattern)
        self.destination = destination
        self.terminate = (terminate is not None) and re.compile(terminate)
        self.patterns = []
        if isinstance(extract, dict):
            # if there is only one extraction pattern, allow it to be a single
            # dict entry
            extract = [extract]
        for pattern in extract:
            self.patterns.append(ExtractionPattern(**pattern))

    def filenname_match(self, name):
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
            from_directory,
            from_file,
            destination_directory,
            **kwargs):
        """Try to extract documentation from file with name.

        Returns True if extraction was successful.
        """
        to_file = self.filenname_match(from_file)
        if not to_file:
            return False
        from_file_path = os.path.join(from_directory, from_file)
        try:
            with open(from_file_path) as original_file:
                utils.log.debug(
                    "mkdocs-simple-plugin: Scanning {}...".format(from_file))
                extraction = StreamExtract(
                    input_stream=original_file,
                    output_stream=LazyFile(destination_directory, to_file),
                    terminate=self.terminate,
                    patterns=self.patterns,
                    **kwargs)
                return extraction.extract()
        except BaseException:
            utils.log.error("mkdocs-simple-plugin: could not build {}".format(
                from_file_path))
        return False


class ExtractionPattern:
    """An ExtractionPattern for a file."""
    # md file="semiliterate.snippet"
    #
    # ##### start
    # (optional) The regex pattern to indicate the start of extraction.
    #
    # Only the first mode whose `start` expression matches is activated, so at
    # most one mode of extraction can be active at any time.
    # When an extraction is active, lines from the scanned
    # file are copied to the destination file (possibly modified by
    # the "replace" parameter below).
    #
    # Additionally, start can specify an output path for the extracted
    # content. Simply add `file=output_path.md` to the start token line.
    #
    # Example:
    #
    # `````
    # # md file=ouput_path.md
    # `````
    #
    # !!!Note
    #       The (last) extraction mode (if any) with no `start`
    #       parameter is active beginning with the first line of the scanned
    #       file; there is no way such a mode can be reactivated if it stops.
    #       This convention allows for convenient "front-matter" extraction.
    #
    # ##### stop
    # (optional) The regex pattern to indicate the stop of extraction.
    #
    # The `simple` plugin will begin searching for further occurrences
    # of `start` expressions on the _next_ line of the scanned file.
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
            start=None,
            stop=None,
            replace=[]):
        """Initialize an with an empty extraction pattern.

        Args:
            start (str): Start regex expression
            stop (str): Stop regex expression
            replace (list): List of (From, To) regex expressions

        """
        self.start = (start is not None) and re.compile(start)
        self.stop = (stop is not None) and re.compile(stop)
        self.replace = []
        for item in replace:
            if isinstance(item, str):
                self.replace.append(re.compile(item))
            else:
                self.replace.append((re.compile(item[0]), item[1]))

    def replace_line(self, line):
        """Apply the specified replacements to the line and return it."""
        if not self.replace:
            return line
        for item in self.replace:
            pattern = item[0] if isinstance(item, tuple) else item
            match_object = pattern.search(line)
            if match_object:
                if isinstance(item, tuple):
                    return get_line(match_object.expand(item[1]))
                if match_object.lastindex:
                    return get_line(match_object[match_object.lastindex])
                return ''
        # Otherwise, just return the line.
        return line
