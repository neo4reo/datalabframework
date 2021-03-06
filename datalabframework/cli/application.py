# encoding: utf-8
"""
A base Application class for Datalabframework applications.

All Datalabframework applications should inherit from this.
"""

# Copyright (c) Datalabframework Development Team.
# Distributed under the terms of the Modified BSD License.

import logging
import os
import sys

from shutil import which
from traitlets import Unicode
from traitlets.config.application import Application, catch_config_error

# aliases and flags

base_aliases = {
    'log-level': 'Application.log_level'
}

base_flags = {
    'debug': ({'Application': {'log_level': logging.DEBUG}},
              "set log level to logging.DEBUG (maximize logging output)")
}


class NoStart(Exception):
    """Exception to raise when an application shouldn't start"""


def _log_level_default():
    return logging.INFO


class DatalabframeworkApp(Application):
    """Base class for Datalabframework applications"""
    name = 'datalabframework'  # override in subclasses
    description = "A Datalabframework Application"

    aliases = base_aliases
    flags = base_flags

    # subcommand-related
    def _find_subcommand(self, name):
        name = '{}-{}'.format(self.name, name)
        return which(name)

    @property
    def _dispatching(self):
        """Return whether we are dispatching to another command

        or running ourselves.
        """
        return bool(self.subapp or self.subcommand)

    subcommand = Unicode()

    @catch_config_error
    def initialize(self, argv=None):
        # don't hook up crash handler before parsing command-line
        if argv is None:
            argv = sys.argv[1:]
        if argv:
            subc = self._find_subcommand(argv[0])
            if subc:
                self.argv = argv
                self.subcommand = subc
                return
        self.parse_command_line(argv)
        if self._dispatching:
            return

    def start(self):
        """Start the whole thing"""
        if self.subcommand:
            os.execv(self.subcommand, [self.subcommand] + self.argv[1:])
            raise NoStart()

        if self.subapp:
            self.subapp.start()
            raise NoStart()

    @classmethod
    def launch_instance(cls, argv=None, **kwargs):
        """Launch an instance of a Datalabframework Application"""
        try:
            return super(DatalabframeworkApp, cls).launch_instance(argv=argv, **kwargs)
        except NoStart:
            return


if __name__ == '__main__':
    DatalabframeworkApp.launch_instance()
