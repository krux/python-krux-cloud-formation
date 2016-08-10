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
from troposphere import Template
from mock import MagicMock, patch
from botocore.exceptions import ClientError

#
# Internal libraries
#

from kruxstatsd import StatsClient
import krux_boto.boto
import krux_cloud_formation.cloud_formation


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
    NO_BOTO3_ERROR_MSG = 'Currently krux_cloud_formation.cloud_formation.CloudFormation only supports krux_boto.boto.Boto3'
    FAKE_URL = 'http://www.example.com'
    S3_URL_EXPIRY = 3600
    S3_BUCKET = 'FAKE_BUCKET'
    S3_FAKE_KEY = 'FAKE_KEY'
    NAME = krux_cloud_formation.cloud_formation.NAME

    def setUp(self):
        # Set up a fake Boto3 object
        self._cf = MagicMock()
        self._boto = MagicMock(
            client=MagicMock(
                return_value=self._cf
            )
        )

        s3_file = MagicMock(
            generate_url=MagicMock(
                return_value=self.FAKE_URL
            )
        )
        self._s3 = MagicMock(
            create_key=MagicMock(
                return_value=s3_file
            ),
            update_key=MagicMock(
                return_value=s3_file
            )
        )

        self.mock_logger = MagicMock()
        self.mock_stats = MagicMock()

        # Mock isinstance() so that it will accept MagicMock object
        with patch('krux_cloud_formation.cloud_formation.isinstance', MagicMock(return_value=True)):
            self._cfn = krux_cloud_formation.cloud_formation.CloudFormation(
                boto=self._boto,
                s3=self._s3,
                bucket_name=self.S3_BUCKET,
                logger=self.mock_logger,
                stats=self.mock_stats,
            )

    def test_init(self):
        """
        __init__() properly creates all properties
        """
        self.assertEqual(self.NAME, self._cfn._name)
        self.assertEqual(self.mock_logger, self._cfn._logger)
        self.assertEqual(self.mock_stats, self._cfn._stats)

        self.assertEqual(self._s3, self._cfn._s3)
        self.assertEqual(self.S3_BUCKET, self._cfn._bucket_name)
        self.assertEqual(self._cf, self._cfn._cf)
        self.assertIsInstance(self._cfn.template, Template)

    def test_init_passed(self):
        """
        __init__() properly creates logger and stats when not passed
        """
        # Mock isinstance() so that it will accept MagicMock object
        with patch('krux_cloud_formation.cloud_formation.isinstance', MagicMock(return_value=True)):
            cfn = krux_cloud_formation.cloud_formation.CloudFormation(
                boto=self._boto,
                s3=self._s3,
                bucket_name=self.S3_BUCKET,
            )

        self.assertEqual(self.NAME, cfn._logger.name)
        self.assertIsInstance(cfn._stats, StatsClient)

    def test_init_non_boto3(self):
        """
        __init__() properly errors out when krux.boto3 is not passed
        """
        with self.assertRaises(NotImplementedError) as e:
            krux_cloud_formation.cloud_formation.CloudFormation(
                boto=self._boto,
                s3=self._s3,
                bucket_name=self.S3_BUCKET,
            )

        self.assertEqual(self.NO_BOTO3_ERROR_MSG, str(e.exception))

    def test_is_stack_exists_success(self):
        """
        _is_stack_exists() handles existing stacks properly
        """
        self._cf.get_template.return_value = True

        self.assertTrue(self._cfn._is_stack_exists(self.TEST_STACK_NAME))
        self._cf.get_template.assert_called_once_with(StackName=self.TEST_STACK_NAME)

    def test_is_stack_exists_failure(self):
        """
        _is_stack_exists() handles non-existing stacks properly
        """
        resp = deepcopy(self.FAKE_ERROR_RESP)
        resp['Error']['Message'] = self.STACK_NOT_EXIST_ERROR_MSG
        self._cf.get_template.side_effect = ClientError(resp, '')

        self.assertFalse(self._cfn._is_stack_exists(self.TEST_STACK_NAME))
        self._cf.get_template.assert_called_once_with(StackName=self.TEST_STACK_NAME)

    def test_is_stack_exists_boto_error(self):
        """
        _is_stack_exists() handles unknown boto errors properly
        """
        resp = deepcopy(self.FAKE_ERROR_RESP)
        resp['Error']['Message'] = 'An error that I cannot handle happened'
        self._cf.get_template.side_effect = ClientError(resp, '')

        with self.assertRaises(ClientError):
            self._cfn._is_stack_exists(self.TEST_STACK_NAME)
            self._cf.get_template.assert_called_once_with(StackName=self.TEST_STACK_NAME)

    def test_is_stack_exists_std_error(self):
        """
        _is_stack_exists() handles unknown standard errors properly
        """
        self._cf.get_template.side_effect = StandardError()

        with self.assertRaises(StandardError):
            self._cfn._is_stack_exists(self.TEST_STACK_NAME)
            self._cf.get_template.assert_called_once_with(StackName=self.TEST_STACK_NAME)

    def test_save_create_with_key(self):
        """
        save() uses the given string as S3 file name correctly
        """
        self._cf.create_stack.return_value = True

        with patch('krux_cloud_formation.cloud_formation.CloudFormation._is_stack_exists', MagicMock(return_value=False)):
            self._cfn.save(self.TEST_STACK_NAME, self.S3_FAKE_KEY)
            self._s3.create_key.assert_called_once_with(
                bucket_name=self.S3_BUCKET,
                key=self.S3_FAKE_KEY,
                str_content=self._cfn.template.to_json()
            )
            self._cf.create_stack.assert_called_once_with(
                StackName=self.TEST_STACK_NAME,
                TemplateURL=self.FAKE_URL
            )

    def test_save_create(self):
        """
        save() detects a new stack and creates it properly
        """
        self._cf.create_stack.return_value = True

        with patch('krux_cloud_formation.cloud_formation.CloudFormation._is_stack_exists', MagicMock(return_value=False)):
            self._cfn.save(self.TEST_STACK_NAME)
            self._s3.create_key.assert_called_once_with(
                bucket_name=self.S3_BUCKET,
                key=self.TEST_STACK_NAME,
                str_content=self._cfn.template.to_json()
            )
            self._cf.create_stack.assert_called_once_with(
                StackName=self.TEST_STACK_NAME,
                TemplateURL=self.FAKE_URL
            )

    def test_save_update_success(self):
        """
        save() detects an existing stack and updates it properly
        """
        self._cf.update_stack.return_value = True

        with patch('krux_cloud_formation.cloud_formation.CloudFormation._is_stack_exists', MagicMock(return_value=True)):
            self._cfn.save(self.TEST_STACK_NAME)
            self._s3.update_key.assert_called_once_with(
                bucket_name=self.S3_BUCKET,
                key=self.TEST_STACK_NAME,
                str_content=self._cfn.template.to_json()
            )
            self._cf.update_stack.assert_called_once_with(
                StackName=self.TEST_STACK_NAME,
                TemplateURL=self.FAKE_URL
            )

    def test_save_update_no_update(self):
        """
        save() detects when there is no change in the update and does not propagate the error
        """
        resp = deepcopy(self.FAKE_ERROR_RESP)
        resp['Error']['Message'] = self.NO_UPDATE_ERROR_MSG
        self._cf.update_stack.side_effect = ClientError(resp, '')

        # GOTCHA: S3 portion of the code is already covered by test_save_create() and test_save_update_success()
        # Skip through that part.
        with patch('krux_cloud_formation.cloud_formation.CloudFormation._is_stack_exists', MagicMock(return_value=True)):
            self._cfn.save(self.TEST_STACK_NAME)
            self._cf.update_stack.assert_called_once_with(
                StackName=self.TEST_STACK_NAME,
                TemplateURL=self.FAKE_URL
            )

    def test_save_update_boto_error(self):
        """
        save() handles unknown boto errors properly
        """
        resp = deepcopy(self.FAKE_ERROR_RESP)
        resp['Error']['Message'] = 'An error that I cannot handle happened'
        self._cf.update_stack.side_effect = ClientError(resp, '')

        # GOTCHA: S3 portion of the code is already covered by test_save_create() and test_save_update_success()
        # Skip through that part.
        with patch('krux_cloud_formation.cloud_formation.CloudFormation._is_stack_exists', MagicMock(return_value=True)):
            with self.assertRaises(ClientError):
                self._cfn.save(self.TEST_STACK_NAME)
                self._cf.update_stack.assert_called_once_with(
                    StackName=self.TEST_STACK_NAME,
                    TemplateURL=self.FAKE_URL
                )

    def test_save_update_std_error(self):
        """
        save() handles unknown standard errors properly
        """
        self._cf.update_stack.side_effect = StandardError()

        # GOTCHA: S3 portion of the code is already covered by test_save_create() and test_save_update_success()
        # Skip through that part.
        with patch('krux_cloud_formation.cloud_formation.CloudFormation._is_stack_exists', MagicMock(return_value=True)):
            with self.assertRaises(StandardError):
                self._cfn.save(self.TEST_STACK_NAME)
                self._cf.update_stack.assert_called_once_with(
                    StackName=self.TEST_STACK_NAME,
                    TemplateURL=self.FAKE_URL
                )
