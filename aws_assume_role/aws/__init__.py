import os

import boto3

from aws_assume_role.configuration import Profile, Configuration


def default_boto_client_factory(service_name, profile: Profile, configuration: Configuration) -> boto3.client:

    aws_credentials_file = configuration.aws_credentials_file
    if aws_credentials_file is not None:
        os.environ.setdefault('AWS_SHARED_CREDENTIALS_FILE', aws_credentials_file)

    aws_config_file = configuration.aws_config_file
    if aws_config_file is not None:
        os.environ.setdefault('AWS_CONFIG_FILE', aws_config_file)

    session = boto3.Session(profile_name=profile.aws_profile)

    return session.client(service_name)
