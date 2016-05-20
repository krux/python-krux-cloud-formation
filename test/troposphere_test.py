# -*- coding: utf-8 -*-
#
# © 2016 Krux Digital, Inc.
#

#
# Standard libraries
#

from __future__ import absolute_import
import unittest

#
# Third party libraries
#

from mock import MagicMock, patch

#
# Internal libraries
#

import krux_boto.boto
import krux_troposphere.troposphere


class TroposphereTest(unittest.TestCase):
    TEST_REGION = 'us-west-2'
    TEST_QUEUE_NAME = 'jib-test'

    def setUp(self):
        self._cf = MagicMock()
        boto = MagicMock(
            client=MagicMock(
                return_value=self._cf
            )
        )

        with patch('krux_troposphere.troposphere.isinstance', MagicMock(return_value=True)):
            self._troposphere = krux_troposphere.troposphere.Troposphere(
                boto=boto
            )

    def test_is_stack_exists(self):
        pass
