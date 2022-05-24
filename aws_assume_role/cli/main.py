import argparse
from argparse import Namespace
from pathlib import Path

from aws_assume_role import configuration
from aws_assume_role.authentication import Authorizer, AuthorizationWriter
from aws_assume_role.authentication.authorization_writer import SessionEnvAuthorizationWriter, \
    ConfigFileAuthorizationWriter
from aws_assume_role.aws.sts import StsClient
from aws_assume_role.cli.guided_configuration import CmdConfiguration
from aws_assume_role.configuration import Configuration
from aws_assume_role.exceptions import ConfigurationNotFoundException
from aws_assume_role.manager import ProfileAuthenticationManager


def _get_parser():

    parser = argparse.ArgumentParser(description='')

    parser.add_argument('-s', '--session', action='store_true',
                        help='Not modify the aws config file and export the aws credentials variables')

    parser.add_argument('--configure', action='store_true',
                        help='Start the configuration process and ignore other parameters')

    parser.add_argument('-r', '--region', action='store',
                        help='Override the region parameter over the configuration file')

    parser.add_argument('--config-path', action='store', default=str(configuration.default_config_file_path()),
                        help='Set the configuration file path (default: {})'
                             .format(configuration.default_config_file_path()))

    parser.add_argument('profile', metavar='profile', nargs='?',
                        help='The profile name on your config file')

    return parser


def start_configuration(args: Namespace):

    config_path = Path(args.config_path)

    if not config_path.exists():
        configuration.write_config(config_path, Configuration(None))

    config = configuration.read_config(config_path)
    guided_config = CmdConfiguration(config)

    guided_config.cmdqueue.append('help')

    try:
        guided_config.cmdloop()
    except KeyboardInterrupt:
        print("\nDiscard changes! By!")


def start_authorization(args: Namespace):

    config_path = Path(args.config_path)

    if not config_path.exists():
        raise ConfigurationNotFoundException("Config file not found, please, run with the --config flag first!")

    config = configuration.read_config(config_path)
    sts_client = StsClient.from_default_factory(config)
    writer = get_authorization_writer(args, config)
    authorizer = Authorizer(sts_client, config, writer)

    manager = ProfileAuthenticationManager(authorizer, writer, config)
    manager.init_job(args.profile, args.region)


def get_authorization_writer(args: Namespace, config: Configuration) -> AuthorizationWriter:

    if args.session:
        return SessionEnvAuthorizationWriter(config)

    return ConfigFileAuthorizationWriter(config)


def main():
    parser = _get_parser()
    arguments = parser.parse_args()

    if arguments.configure:
        start_configuration(arguments)
    elif arguments.profile is None:
        parser.error("You must be define a profile or set the --configure flag. Run flag -h to get more information")
    else:
        start_authorization(arguments)


if __name__ == '__main__':
    main()
