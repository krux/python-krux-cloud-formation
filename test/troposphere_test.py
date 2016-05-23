# -*- coding: utf-8 -*-
#
# © 2016 Krux Digital, Inc.
#

#
# Standard libraries
#

from __future__ import absolute_import
from copy import deepcopy
import unittest

#
# Third party libraries
#

import simplejson
from mock import MagicMock, patch
from botocore.exceptions import ClientError

#
# Internal libraries
#

import krux_boto.boto
import krux_troposphere.troposphere


class TroposphereTest(unittest.TestCase):
    TEST_STACK_NAME = 'test_stack'
    FAKE_ERROR_RESP = {
        'ResponseMetadata': {
            'HTTPStatusCode': 400,
            'RequestId': 'fake-request',
        },
        'Error': {
            'Message': '',
            'Code': 'ValidationError',
            'Type': 'Sender',
        }
    }
    STACK_NOT_EXIST_ERROR_MSG = 'Stack with id {stack_name} does not exist'.format(stack_name=TEST_STACK_NAME)
    NO_UPDATE_ERROR_MSG = 'No updates are to be performed.'

    def setUp(self):
        # Set up a fake Boto3 object
        self._cf = MagicMock()
        boto = MagicMock(
            client=MagicMock(
                return_value=self._cf
            )
        )

        # Mock isinstance() so that it will accept MagicMock object
        with patch('krux_troposphere.troposphere.isinstance', MagicMock(return_value=True)):
            self._troposphere = krux_troposphere.troposphere.Troposphere(
                boto=boto
            )

    def test_is_stack_exists_success(self):
        """
        _is_stack_exists() handles existing stacks properly
        """
        self._cf.get_template.return_value = True

        self.assertTrue(self._troposphere._is_stack_exists(self.TEST_STACK_NAME))
        self._cf.get_template.assert_called_once_with(StackName=self.TEST_STACK_NAME)

    def test_is_stack_exists_failure(self):
        """
        _is_stack_exists() handles non-existing stacks properly
        """
        resp = deepcopy(self.FAKE_ERROR_RESP)
        resp['Error']['Message'] = self.STACK_NOT_EXIST_ERROR_MSG
        self._cf.get_template.side_effect = ClientError(resp, '')

        self.assertFalse(self._troposphere._is_stack_exists(self.TEST_STACK_NAME))
        self._cf.get_template.assert_called_once_with(StackName=self.TEST_STACK_NAME)

    def test_is_stack_exists_boto_error(self):
        """
        _is_stack_exists() handles unknown boto errors properly
        """
        resp = deepcopy(self.FAKE_ERROR_RESP)
        resp['Error']['Message'] = 'An error that I cannot handle happened'
        self._cf.get_template.side_effect = ClientError(resp, '')

        with self.assertRaises(ClientError):
            self._troposphere._is_stack_exists(self.TEST_STACK_NAME)
            self._cf.get_template.assert_called_once_with(StackName=self.TEST_STACK_NAME)

    def test_is_stack_exists_std_error(self):
        """
        _is_stack_exists() handles unknown standard errors properly
        """
        self._cf.get_template.side_effect = StandardError()

        with self.assertRaises(StandardError):
            self._troposphere._is_stack_exists(self.TEST_STACK_NAME)
            self._cf.get_template.assert_called_once_with(StackName=self.TEST_STACK_NAME)

    def test_save_create(self):
        """
        save() detects a new stack and creates it properly
        """
        self._cf.create_stack.return_value = True

        with patch('krux_troposphere.troposphere.Troposphere._is_stack_exists', MagicMock(return_value=False)):
            self._troposphere.save(self.TEST_STACK_NAME)
            self._cf.create_stack.assert_called_once_with(
                StackName=self.TEST_STACK_NAME,
                TemplateBody=self._troposphere.template.to_json()
            )

    def test_save_update_success(self):
        """
        save() detects an existing stack and updates it properly
        """
        self._cf.update_stack.return_value = True

        with patch('krux_troposphere.troposphere.Troposphere._is_stack_exists', MagicMock(return_value=True)):
            self._troposphere.save(self.TEST_STACK_NAME)
            self._cf.update_stack.assert_called_once_with(
                StackName=self.TEST_STACK_NAME,
                TemplateBody=self._troposphere.template.to_json()
            )

    def test_save_update_no_update(self):
        """
        save() detects when there is no change in the update and does not propagate the error
        """
        resp = deepcopy(self.FAKE_ERROR_RESP)
        resp['Error']['Message'] = self.NO_UPDATE_ERROR_MSG
        self._cf.update_stack.side_effect = ClientError(resp, '')

        with patch('krux_troposphere.troposphere.Troposphere._is_stack_exists', MagicMock(return_value=True)):
            self._troposphere.save(self.TEST_STACK_NAME)
            self._cf.update_stack.assert_called_once_with(
                StackName=self.TEST_STACK_NAME,
                TemplateBody=self._troposphere.template.to_json()
            )

    def test_save_update_boto_error(self):
        """
        save() handles unknown boto errors properly
        """
        resp = deepcopy(self.FAKE_ERROR_RESP)
        resp['Error']['Message'] = 'An error that I cannot handle happened'
        self._cf.update_stack.side_effect = ClientError(resp, '')

        with patch('krux_troposphere.troposphere.Troposphere._is_stack_exists', MagicMock(return_value=True)):
            with self.assertRaises(ClientError):
                self._troposphere.save(self.TEST_STACK_NAME)
                self._cf.update_stack.assert_called_once_with(
                    StackName=self.TEST_STACK_NAME,
                    TemplateBody=self._troposphere.template.to_json()
                )

    def test_save_update_std_error(self):
        """
        save() handles unknown standard errors properly
        """
        self._cf.update_stack.side_effect = StandardError()

        with patch('krux_troposphere.troposphere.Troposphere._is_stack_exists', MagicMock(return_value=True)):
            with self.assertRaises(StandardError):
                self._troposphere.save(self.TEST_STACK_NAME)
                self._cf.update_stack.assert_called_once_with(
                    StackName=self.TEST_STACK_NAME,
                    TemplateBody=self._troposphere.template.to_json()
                )
