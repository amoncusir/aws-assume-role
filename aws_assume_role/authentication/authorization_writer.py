import abc
import textwrap
from abc import ABCMeta
from configparser import ConfigParser
from typing import Optional, Callable

import pyperclip

from aws_assume_role.authentication.authorization_details import AuthorizationDetails
from aws_assume_role.configuration import Configuration, Profile


class AuthorizationWriter(metaclass=ABCMeta):

    @abc.abstractmethod
    def write(self, details: AuthorizationDetails, profile: Profile, region: Optional[str]):
        pass


class ConfigFileAuthorizationWriter(AuthorizationWriter):

    def __init__(self, config: Configuration):
        self.config = config
        self.parser_factory = ConfigParser

    def write(self, details: AuthorizationDetails, profile: Profile, region: Optional[str]):
        credentials = self.__read_credentials()

        merged_region = region or self.config.aws_default_region

        if profile.name not in credentials:
            credentials[profile.name] = {}

        profile_cred = credentials[profile.name]

        profile_cred['region'] = merged_region
        profile_cred['aws_access_key_id'] = details.access_key
        profile_cred['aws_secret_access_key'] = details.secret_key
        profile_cred['aws_session_token'] = details.session_token

        self.__write_credentials(credentials)

    def __read_credentials(self) -> ConfigParser:
        credentials_path = self.config.aws_credentials_file_path
        parser = self.parser_factory()
        parser.read(credentials_path)
        return parser

    def __write_credentials(self, credentials: ConfigParser):
        credentials_path = self.config.aws_credentials_file_path

        with credentials_path.open(mode='w') as writeable:
            credentials.write(writeable)


class SessionEnvAuthorizationWriter(AuthorizationWriter):

    def __init__(self, config: Configuration, user_output_interface: Callable[[str], None] = print):
        self.config = config
        self.user_output_interface = user_output_interface

    def write(self, details: AuthorizationDetails, profile: Profile, region: Optional[str]):

        default_region = region or self.config.aws_default_region

        copy_content = textwrap.dedent(f'''
        export AWS_ACCESS_KEY_ID="{details.access_key}"
        export AWS_SECRET_ACCESS_KEY="{details.secret_key}"
        export AWS_SESSION_TOKEN="{details.session_token}"
        export AWS_DEFAULT_REGION={default_region}
        ''')

        print_content = textwrap.dedent(f'''
        Authorization done!

        Because isn't possible to export variables from child process to parent, you need to write in your shell the
        following values.

        NOTE: These values have already been copied to your clipboard, only just need to paste!

        {copy_content}
        ''')

        pyperclip.copy(copy_content)
        self.user_output_interface(print_content)
