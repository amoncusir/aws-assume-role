import dataclasses
import json
import os
from pathlib import Path
from typing import Final, List, Optional, get_type_hints, get_args, Dict

from aws_assume_role.exceptions import ConfigurationNotFoundException
from aws_assume_role.utils.typing_utils import is_optional

CONFIG_FILE_NAME: Final[str] = '.aws_assume_role.config'


def default_config_file_path() -> Path:
    return Path.home()/CONFIG_FILE_NAME


class Dictionable:

    def __getitem__(self, item: str):
        return getattr(self, item)

    def __setitem__(self, key, value):

        if value is not None:
            item_type = next((v for k, v in get_type_hints(self.__class__).items() if k == key))

            if is_optional(item_type):
                item_type, _ = get_args(item_type)

            if isinstance(value, item_type):
                setattr(self, key, value)

            setattr(self, key, item_type(value))
        else:

            setattr(self, key, value)

    def __delitem__(self, key):
        setattr(self, key, getattr(self.__class__, key))


@dataclasses.dataclass
class Profile:
    name: str
    account_id: str
    role_name: str
    aws_profile: str


@dataclasses.dataclass
class StoredProfile(Profile, Dictionable):
    role_name: Optional[str] = None
    aws_profile: Optional[str] = None

    def to_dict(self):
        return self.__dict__

    @staticmethod
    def from_dict(dictionary):
        return StoredProfile(**dictionary)


@dataclasses.dataclass
class Configuration(Dictionable):
    """
    Configuration class
    """
    aws_default_role_name: str
    aws_landing_account_id: str
    aws_default_region: str = 'us-west-1'
    aws_landing_profile: str = 'default'
    aws_config_file: Optional[str] = None
    aws_credentials_file: Optional[str] = None
    stored_profiles: List[StoredProfile] = dataclasses.field(default_factory=list)

    @property
    def aws_credentials_file_path(self) -> Path:
        path = os.environ.get('ASSUME_AWS_SHARED_CREDENTIALS_FILE')\
               or self.aws_credentials_file\
               or Path.home()/'.aws'/'credentials'

        return Path(path)

    @property
    def aws_config_file_path(self) -> Path:
        path = os.environ.get('ASSUME_AWS_CONFIG_FILE')\
               or self.aws_config_file \
               or Path.home()/'.aws'/'config'
        return Path(path)

    @property
    def aws_profile(self) -> str:
        return os.environ.get('ASSUME_AWS_PROFILE') or self.aws_landing_profile

    @property
    def profiles(self) -> List[Profile]:
        return [self.__from_stored_to_profile(sp) for sp in self.stored_profiles]

    def find_stored_profile(self, profile_name: str) -> Optional[StoredProfile]:
        return next((p for p in self.stored_profiles if p.name == profile_name), None)

    def find_profile(self, profile_name: str) -> Optional[Profile]:
        return next((p for p in self.profiles if p.name == profile_name), None)

    def del_profile(self, profile_name: str):

        for i in range(len(self.stored_profiles)):
            profile = self.stored_profiles[i]

            if profile.name == profile_name:
                del self.stored_profiles[i]
                break

    def to_dict(self) -> Dict:
        return {
            **self.__dict__,
            'stored_profiles': [p.to_dict() for p in self.stored_profiles]
        }

    def __from_stored_to_profile(self, stored_profile: StoredProfile) -> Profile:
        role_name = stored_profile.role_name or self.aws_default_role_name
        aws_profile = stored_profile.aws_profile or self.aws_profile

        return Profile(stored_profile.name, stored_profile.account_id, role_name, aws_profile)

    @staticmethod
    def from_dict(dictionary):

        stored_profiles = [StoredProfile.from_dict(sp) for sp in dictionary.pop('stored_profiles', [])]

        return Configuration(stored_profiles=stored_profiles, **dictionary)


def read_config(path: Path) -> Configuration:
    if not path.exists():
        raise ConfigurationNotFoundException()

    with path.open(mode='r', encoding='utf-8') as readable:
        return Configuration.from_dict(json.load(readable))


def write_config(path: Path, config: Configuration):

    json_str = json.dumps(config.to_dict(), indent=2, sort_keys=True)

    with path.open(mode='w', encoding='utf-8') as writable:
        writable.write(json_str)
        writable.write('\n')
