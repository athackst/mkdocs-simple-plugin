#!/usr/bin/env python3
import re
import sys

try:
    import configparser
except ImportError:  # 2.7
    import ConfigParser as configparser

import click
from first import first
from packaging.utils import canonicalize_version

# pylint: disable=no-value-for-parameter
pattern = re.compile(r"((?:__)?version(?:__)? ?= ?[\"'])(.+?)([\"'])")


class SemVer(object):
    def __init__(self, major=0, minor=0, patch=0, pre=None, local=None):
        self.major = major
        self.minor = minor
        self.patch = patch
        self.pre = pre
        self.local = local

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        version_string = ".".join(
            map(str, [self.major, self.minor, self.patch]))
        if self.pre:
            version_string += "-" + self.pre
        if self.local:
            version_string += "+" + self.local
        return version_string

    @classmethod
    def parse(cls, version):
        major = minor = patch = 0
        local = pre = None
        local_split = version.split("+")
        if len(local_split) > 1:
            version, local = local_split
        pre_split = version.split("-", 1)
        if len(pre_split) > 1:
            version, pre = pre_split
        major_split = version.split(".", 1)
        if len(major_split) > 1:
            major, version = major_split
            minor_split = version.split(".", 1)
            if len(minor_split) > 1:
                minor, version = minor_split
                if version:
                    patch = version
            else:
                minor = version
        else:
            major = version
        return cls(
            major=int(major), minor=int(minor), patch=int(patch), pre=pre, local=local
        )

    def bump(self, major=False, minor=False, patch=False, pre=None, local=None):
        if major:
            self.major += 1
        if minor:
            self.minor += 1
        if patch:
            self.patch += 1
        if pre:
            self.pre = pre
        if local:
            self.local = local
        if not (major or minor or patch or pre or local):
            self.patch += 1


class NoVersionFound(Exception):
    pass


def find_version(input_string):
    match = first(pattern.findall(input_string))
    if match is None:
        raise NoVersionFound
    return match[1]


@click.command()
@click.option(
    "--major", "-M", "major", flag_value=True, default=None, help="Bump major number"
)
@click.option(
    "--minor", "-m", "minor", flag_value=True, default=None, help="Bump minor number"
)
@click.option(
    "--patch", "-p", "patch", flag_value=True, default=None, help="Bump patch number"
)
@click.option("--pre", help="Set the pre-release identifier")
@click.option("--local", help="Set the local version segment")
@click.option(
    "--canonicalize", flag_value=True, default=None, help="Canonicalize the new version"
)
@click.argument("input", type=click.File("rb"), default="setup.py", required=False)
@click.argument("output", type=click.File("wb"), default=None, required=False)
def main(input, output, major, minor, patch, pre, local, canonicalize):

    config = configparser.RawConfigParser()
    config.read([".bump", "setup.cfg"])

    major = major or config.getboolean("bump", "major", fallback=False)
    minor = minor or config.getboolean("bump", "minor", fallback=False)
    patch = patch or config.getboolean("bump", "patch", fallback=True)
    input = input or click.File("rb")(
        config.get("bump", "input", fallback="setup.py"))
    output = output or click.File("wb")(input.name)
    canonicalize = canonicalize or config.get(
        "bump", "canonicalize", fallback=False)

    contents = input.read().decode("utf-8")
    try:
        version_string = find_version(contents)
    except NoVersionFound:
        click.echo("No version found in ./{}.".format(input.name))
        sys.exit(1)

    version = SemVer.parse(version_string)
    version.bump(major, minor, patch, pre, local)
    version_string = str(version)
    if canonicalize:
        version_string = canonicalize_version(version_string)
    new = pattern.sub(r"\g<1>{}\g<3>".format(version_string), contents)
    output.write(new.encode())
    click.echo(version_string)


if __name__ == "__main__":
    main()
