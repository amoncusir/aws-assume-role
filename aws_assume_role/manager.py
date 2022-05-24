from typing import Optional

from aws_assume_role.authentication.authorization import Authorizer
from aws_assume_role.authentication.authorization_writer import AuthorizationWriter
from aws_assume_role.configuration import Configuration, Profile
from aws_assume_role.exceptions import ProfileNotConfiguredException


class ProfileAuthenticationManager:

    def __init__(self, authorizer: Authorizer, writer: AuthorizationWriter, configuration: Configuration):
        self.authorizer = authorizer
        self.writer = writer
        self.configuration = configuration

    def init_job(self, profile: str, region: Optional[str]):

        profile = self._get_profile(profile)
        details = self.authorizer.request_details(profile)

        self.writer.write(details, profile, region)

    def _get_profile(self, profile: str) -> Profile:

        profile = self.configuration.find_profile(profile)

        if profile is None:
            raise ProfileNotConfiguredException(f"For profile {profile}")

        return profile

