# -*- coding: utf-8 -*-
#
# © 2016 Krux Digital, Inc.
#

#
# Standard libraries
#

from __future__ import absolute_import
import os

#
# Internal libraries
#

from krux.cli import get_group
import krux_boto.cli
from krux_troposphere.troposphere import add_troposphere_cli_arguments, get_troposphere, NAME


class Application(krux_boto.cli.Application):

    def __init__(self, name=NAME):
        # Call to the superclass to bootstrap.
        super(Application, self).__init__(name=name)

        self.troposphere = get_troposphere(self.args, self.logger, self.stats)

    def add_cli_arguments(self, parser):
        # Call to the superclass
        super(Application, self).add_cli_arguments(parser)

        add_troposphere_cli_arguments(parser, include_boto_arguments=False)

    def run(self):
        pass


def main():
    app = Application()
    with app.context():
        app.run()


# Run the application stand alone
if __name__ == '__main__':
    main()
