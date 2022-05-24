from aws_assume_role.authentication.authorization_details import AuthorizationDetails
from aws_assume_role.authentication.authorization_writer import AuthorizationWriter
from aws_assume_role.aws.sts import StsClient
from aws_assume_role.configuration import Configuration, Profile


class Authorizer:

    def __init__(self, sts_client: StsClient, configuration: Configuration, writer: AuthorizationWriter):
        self.sts_client = sts_client
        self.configuration = configuration
        self.writer = writer

    def request_details(self, profile: Profile) -> AuthorizationDetails:
        assumed_role = self.sts_client.assume(profile)
        credentials = assumed_role['Credentials']

        return AuthorizationDetails(
            access_key=credentials['AccessKeyId'],
            secret_key=credentials['SecretAccessKey'],
            session_token=credentials['SessionToken'],
        )
