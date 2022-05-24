import cmd
import typing
from pathlib import Path

from aws_assume_role.cli.exceptions import InvalidArgumentsException
from aws_assume_role.configuration import Configuration, Profile, default_config_file_path, write_config, StoredProfile
from aws_assume_role.utils.typing_utils import is_optional


class CmdConfiguration(cmd.Cmd):

    intro = 'Guided configuration process. Type help or ? to list commands.'
    prompt = '(command) '

    def __init__(self, config: Configuration):
        super().__init__()
        self.config = config

    def _write_line(self, msg):
        self.stdout.write(f'{msg}\n')

    def _write_space(self):
        self._write_line('')

    def _write_attributes(self, attrs: typing.List[str]):

        filled_parameters = [(p, self.config[p]) for p in attrs]

        self._write_line('List of attributes:')
        self._write_space()

        longest_key = max([len(p) for p in attrs])

        for k, v in filled_parameters:
            spaces_left = (longest_key - len(k)) * ' '
            value = v if v is not None else ''
            self._write_line(f'\t{k}{spaces_left} = {value}')

    def _write_profiles(self, profiles: typing.List[Profile]):

        attrs = list(typing.get_type_hints(Profile).keys())

        self._write_line('List of profiles:')
        self._write_space()

        longest_key = max([len(p) for p in attrs])

        for profile in profiles:

            self._write_line(f'\t:: Profile')

            for attr in attrs:
                spaces_left = (longest_key - len(attr)) * ' '
                value = getattr(profile, attr)
                value = value if value is not None else ''
                self._write_line(f'\t{attr}{spaces_left} = {value}')

            self._write_space()

    def _get_valid_config_parameters(self) -> typing.List[str]:

        attrs = typing.get_type_hints(self.config.__class__)

        simple_attrs = [k for k, v in attrs.items() if v in (str, int, bool)]
        complex_attrs = [k for k, v in attrs.items() if is_optional(v) and str in typing.get_args(v)]

        return simple_attrs + complex_attrs

    def _set_value(self, item, value):

        if item in self._get_valid_config_parameters():
            self.config[item] = value
        else:
            self._write_line(f'Invalid key <<{item}>>. Skip')

    def do_list(self, _):
        """Return a list of all editable attributes: list"""

        parameters = self._get_valid_config_parameters()

        self._write_attributes(parameters)

        self._write_space()

        self._write_profiles(self.config.stored_profiles)

        self._write_space()

    def do_set(self, arg: str):
        """Set config value: set PROPERTY VALUE"""

        def parse_key_and_value(args: str) -> (str, str):
            args = args.split(' ')

            if len(args) != 2:
                raise InvalidArgumentsException(args)

            return *args,

        try:
            self._set_value(*parse_key_and_value(arg))
        except InvalidArgumentsException:
            self._write_line('Invalid arguments. Skip')

    def do_set_default(self, item: str):
        """Remove config value (set as default value): set_default PROPERTY"""
        if item in self._get_valid_config_parameters():
            del self.config[item]
        else:
            self._write_line(f'Invalid key <<{item}>>. Skip')

    def do_remove(self, key: str):
        """Remove config value (set as None value): remove PROPERTY"""
        self._set_value(key, None)

    def do_add_profile(self, arg: str):
        """Create new Profile on config: add_profile NAME ACCOUNT_ID [ROLE_NAME] [AWS_PROFILE]"""

        def parse_args(args: str) -> tuple:
            args = args.split(' ')

            if len(args) < 2:
                raise InvalidArgumentsException(args)

            args = iter(args)

            return next(args), next(args), next(args, None), next(args, None)

        profile = StoredProfile(*parse_args(arg))
        self.config.stored_profiles.append(profile)

    def do_edit_profile(self, arg: str):
        """Create new Profile on config: edit_profile NAME KEY VALUE"""

        def parse_args(args: str) -> tuple:
            args = args.split(' ')

            if len(args) != 3:
                raise InvalidArgumentsException(args)

            return *args,

        name, key, value = parse_args(arg)

        profile = self.config.find_stored_profile(name)

        if profile is None:
            self._write_line(f"Unknown profile: {name}")
            return

        profile[key] = value

    def do_remove_profile(self, name: str):
        """Remove a Profile from config: remove_profile NAME"""

        profile = self.config.find_profile(name)

        if profile is None:
            self._write_line(f"Unknown profile: {name}")
        else:
            self.config.del_profile(name)

    def do_save(self, path: str):
        """Save current configuration and optionally specify a custom path: save [PATH]"""

        config_path = default_config_file_path()

        if path is not None and path != '':
            config_path = Path(path)

        write_config(config_path, self.config)

        self._write_line(f"Configuration Saved on {config_path}")

    def do_exit(self, _):
        """Exit: exit"""
        return True

