
class AwsAssumeBaseException(BaseException):
    pass


class InvalidCredentialsException(AwsAssumeBaseException):
    """
    User not logged
    """
    pass


class InvalidAccountIdException(AwsAssumeBaseException):
    """
    Invalid Account ID Configuration
    """
    pass


class ConfigurationNotFoundException(AwsAssumeBaseException):
    pass


class ProfileNotConfiguredException(AwsAssumeBaseException):
    pass
