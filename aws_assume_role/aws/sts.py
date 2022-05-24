import os
import platform
from typing import Callable

import boto3
from botocore.exceptions import BotoCoreError

from aws_assume_role.aws import default_boto_client_factory
from aws_assume_role.configuration import Configuration, Profile
from aws_assume_role.exceptions import InvalidCredentialsException, InvalidAccountIdException


class StsClient:

    def __init__(self, boto_sts_client_factory: Callable[[Profile], boto3.client], landing_account_id: str):
        self.boto_sts_client_factory = boto_sts_client_factory
        self.landing_account_id = landing_account_id

    @staticmethod
    def from_default_factory(configuration: Configuration):

        def factory_wrapper(profile: Profile):
            return default_boto_client_factory('sts', profile, configuration)

        return StsClient(factory_wrapper, configuration.aws_landing_account_id)

    def assume(self, profile: Profile):

        sts_client = self.boto_sts_client_factory(profile)

        if not self._can_assume(sts_client):
            raise InvalidAccountIdException('Invalid Account id')

        return sts_client.assume_role(
            RoleArn=f'arn:aws:iam::{profile.account_id}:role/{profile.role_name}',
            RoleSessionName=profile.name
        )

    def _can_assume(self, sts_client) -> bool:
        try:
            response = sts_client.get_caller_identity()
            return self.landing_account_id is None or response['Account'] == self.landing_account_id
        except BotoCoreError as e:
            raise InvalidCredentialsException from e

    def _get_tags(self) -> [{str: str}]:
        return [
            {
                'Key': 'UserOS',
                'Value': os.environ.get('USER', 'Unknown')
            },
            {
                'Key': 'Shell',
                'Value': os.environ.get('SHELL', 'Unknown')
            },
            {
                'Key': 'Term',
                'Value': os.environ.get('TERM', 'Unknown')
            },
            {
                'Key': 'Platform',
                'Value': platform.platform()
            },
        ]


