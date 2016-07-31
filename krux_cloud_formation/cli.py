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
import krux_s3.cli
from krux_cloud_formation.cloud_formation import add_cloud_formation_cli_arguments, get_cloud_formation, NAME


class Application(krux_s3.cli.Application):

    def __init__(self, name=NAME):
        # Call to the superclass to bootstrap.
        super(Application, self).__init__(name=name)

        self.cloud_formation = get_cloud_formation(self.args, self.logger, self.stats)

    def add_cli_arguments(self, parser, include_bucket_arguments=True):
        # Call to the superclass
        super(Application, self).add_cli_arguments(parser)

        add_cloud_formation_cli_arguments(
            parser=parser,
            include_boto_arguments=False,
            include_bucket_arguments=include_bucket_arguments
        )

    def run(self):
        # GOTCHA: Purposely left blank. Troposphere does not provide a solid parser of the Cloud Formation template.
        # This makes getter rather difficult. Without creating a test stack that is perfectly constant and lots of code to
        # regenerate that stack, I cannot make a no-op call. So leaving this method empty for now.
        pass


def main():
    app = Application()
    with app.context():
        app.run()


# Run the application stand alone
if __name__ == '__main__':
    main()
